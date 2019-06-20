import datetime
import math
import random
import subprocess
import sys
import time

import load_settings
from SmartKubernetesSchedular import enforcer, rank_executions
from SmartKubernetesSchedular.deployment import state_transition_plan
from SmartKubernetesSchedular.load_extractors.LoadExtractorBytesIn import LoadExtractorBytesIn
from SmartKubernetesSchedular.matcher import match_nodes_desired_with_current_state, find_transitions_execution_change
from SmartKubernetesSchedular.retrieve_executions import retrieve_executions
from SmartKubernetesSchedular.strategies.TryEmptyOneNode import TryEmptyOneNode, calc_removal_resulting_cost
from SmartKubernetesSchedular.time_window import create_time_window
from initializer.neo4j_queries import execute_query_function
from kubernetes_tools import extract_pods, extract_nodes
from kubernetes_tools.cluster_stability import cluster_stable
from kubernetes_tools.extract_nodes import calc_cost, node_sum_requested
from kubernetes_tools.migrate_pod import PodException
from log import log


class AllNodesToFullToMove(Exception):
    pass


def delete_execution(tx, execution_id):
    tx.run("MATCH (e:Execution) \
            WHERE id(e) = $execution_id \
            MATCH (e) -[:HasNode]-> (n:Node) \
            DETACH DELETE n, e",
           execution_id=execution_id)


def select_random_deployment_pod_to_transition(nodes):
    node_list = list(nodes.items())
    for i in range(0, 1000):
        source_node, source_node_info = random.choice(node_list)
        destination_node, destination_node_info = random.choice(node_list)
        if source_node == destination_node:
            continue

        pod = random.choice(list(source_node_info["pods"]))
        if not pod["deployment_name"]:
            continue

        if node_sum_requested(destination_node_info) + pod["total_requested"] < destination_node_info["cpu"]*0.95:
            transitions = {
                pod["node_name"]: {
                    "add": [],
                    "remove": [pod["pod_name"]]
                },
                destination_node: {
                    "add": [pod["pod_generate_name"]],
                    "remove": []
                }
            }
            return transitions
    raise AllNodesToFullToMove("Randomness was forever in our disfavor (or all nodes are perfectly filled)")


def get_best_transitions(load, nodes, settings):
    removal_possible, node_removed, removal_transitions = TryEmptyOneNode().generate_improvement(settings)
    removal_resulting_cost = math.inf
    cur_cost = calc_cost(nodes, settings)
    if removal_possible:
        removal_resulting_cost = calc_removal_resulting_cost(nodes, node_removed, settings)
        print("cost removal:", removal_resulting_cost)

    old_executions = retrieve_executions(load, settings)
    old_best_execution = rank_executions.find_best_execution(old_executions, settings["prometheus_address"])
    old_best_execution_cost = calc_cost(old_best_execution["nodes"], settings)

    print("costs for all options: current= {}, removal= {}, old_best= {}".format(cur_cost, removal_resulting_cost, old_best_execution_cost))
    if removal_resulting_cost <= old_best_execution_cost:
        log.info("TAKE REMOVAL ACTION")
        return removal_transitions
    elif cur_cost <= old_best_execution_cost:
        print("Staying with current execution, but randomly changing one random pod")
        current_state = extract_nodes.extract_all_nodes_cpu_pods()
        return select_random_deployment_pod_to_transition(current_state)
    else:
        print("Changing to old_best_execution found in time: {}".format(old_best_execution["start_time"]))
        current_state = extract_nodes.extract_all_nodes_cpu_pods_dict()
        print(current_state)
        print(old_best_execution)

        # Remove executions to ensure that it doesn't get stuck on one lucky run.
        execute_query_function(delete_execution, old_best_execution["execution_id"])
        success, transitions = find_transitions_execution_change(current_state, old_best_execution["nodes"])
        if success:
            return transitions
        else:
            print("The old_best required stateful sets to be moved, so therefore was blocked")
            return get_best_transitions(load, nodes, settings)



def transition_state(transitions, pods, nodes):
    print(transitions)
    down, migrate, up = state_transition_plan(transitions, pods, nodes)
    print(down)
    print(migrate)
    print(up)
    enforcer.enforce(down, migrate, up)


def update_step(time_window, load_extractor, settings):
    end_time = datetime.datetime.now()
    if cluster_stable(end_time, time_window, settings) or True:
        print("Cluster was stable for {} seconds till {}, calculating best transition".format(time_window.seconds, end_time))
        pods = extract_pods.extract_all_pods()
        nodes = extract_nodes.extract_all_nodes_cpu()

        load = load_extractor.extract_load(end_time, time_window, settings)
        create_time_window(end_time, load, time_window, extract_pods.pods_dict_to_list(pods), nodes)

        transitions = get_best_transitions(load, nodes, settings)
        transition_state(transitions, pods, nodes)
        return True
    else:
        print("Cluster was not stable, waiting for the next time_window to check stability")
        return False


def tuning_loop(time_window, load_extractor, settings):
    went_wrong_counter = 0
    went_correct_counter = 0
    not_stable_counter = 0
    nodes_to_full_to_move = 0
    while True:
        # Hack to fix authentication issue
        #subprocess.run(["gcloud", "container", "clusters", "get-credentials", "demo-cluster-1"])

        print("Time for an update_step iteration! {}".format(datetime.datetime.now()))
        try:
            if update_step(time_window, load_extractor, settings):
                print("went correct")
                went_correct_counter += 1
            else:
                not_stable_counter += 1
        except PodException:
            print("went wrong")
            went_wrong_counter += 1
        except AllNodesToFullToMove:
            print("All nodes to full to do random move")
            nodes_to_full_to_move += 1

        print("Current not stable:correct:wrong balance {}:{}:{}".format(not_stable_counter, went_correct_counter, went_wrong_counter))
        log.info("Going back to sleep")
        time.sleep(time_window.seconds)


def main():
    print(extract_nodes.extract_all_nodes_cpu_pods())
    settings = load_settings.load_settings(sys.argv[1])
    time_window = datetime.timedelta(seconds=settings["measure_window"])
    load_extractor = LoadExtractorBytesIn()
    tuning_loop(time_window, load_extractor, settings)


if __name__ == '__main__':
    main()

