import datetime
import math
import random
import subprocess
import sys
import time

import load_settings
from Neo4jGraphDriver import disconnect_neo4j
from SmartKubernetesSchedular import enforcer, rank_executions
from SmartKubernetesSchedular.deployment import state_transition_plan
from SmartKubernetesSchedular.empty_node import empty_node_transitions
from SmartKubernetesSchedular.load_extractors.LoadExtractorBytesIn import LoadExtractorBytesIn
from SmartKubernetesSchedular.matcher import match_nodes_desired_with_current_state, find_transitions_execution_change
from SmartKubernetesSchedular.retrieve_executions import retrieve_executions
from SmartKubernetesSchedular.strategies.TryEmptyOneNode import TryEmptyOneNode, calc_removal_resulting_cost
from SmartKubernetesSchedular.time_window import create_time_window
from initializer import neo4j_queries
from initializer.neo4j_queries import execute_query_function
from kubernetes_tools import extract_pods, extract_nodes
from kubernetes_tools.cluster_stability import cluster_stable
from kubernetes_tools.extract_nodes import calc_cost, node_sum_requested
from kubernetes_tools.migrate_pod import PodException
from log import log, remove_file_handler

action = "none"

class AllNodesToFullToMove(Exception):
    pass


class MigrationChanceNotMet(Exception):
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
        if not extract_pods.movable(pod):
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
    removal_possible, node_removed, removal_transitions = empty_node_transitions(settings)
    removal_resulting_cost = math.inf
    cur_cost = calc_cost(nodes, settings)
    if removal_possible:
        removal_resulting_cost = calc_removal_resulting_cost(nodes, node_removed, settings)

    old_executions = retrieve_executions(load, settings)
    old_best_execution = rank_executions.find_best_execution(old_executions, settings["prometheus_address"])
    old_best_execution_cost = calc_cost(old_best_execution["nodes"], settings)

    log.info("Costs for all options: current= {}, removal= {}, old_best= {}".format(cur_cost, removal_resulting_cost, old_best_execution_cost))
    global action
    if removal_resulting_cost <= old_best_execution_cost:
        log.info("Removing node: {}".format(node_removed))
        action = "rem"
        return removal_transitions
    elif cur_cost <= old_best_execution_cost:
        migration_chance = settings["migration_chance"]
        if random.random() <= migration_chance:
            log.info("Staying with current execution, but randomly changing one random pod")
            current_state = extract_nodes.extract_all_nodes_cpu_pods()
            action = "mig"
            return select_random_deployment_pod_to_transition(current_state)
        else:
            raise MigrationChanceNotMet()
    else:
        log.info("Changing to old_best_execution found in time: {}".format(old_best_execution["start_time"]))
        current_state = extract_nodes.extract_all_nodes_cpu_pods_dict()

        # Remove executions to ensure that it doesn't get stuck on one lucky run.
        # TODO: add this line again!!!!!!
        execute_query_function(delete_execution, old_best_execution["execution_id"])
        success, transitions = find_transitions_execution_change(current_state, old_best_execution["nodes"])
        if success:
            action = "old"
            return transitions
        else:
            log.info("The old_best required stateful sets to be moved, so therefore was blocked")
            return get_best_transitions(load, nodes, settings)


def transition_state(transitions, pods, nodes):
    down, migrate, up, node_removals = state_transition_plan(transitions, pods, nodes)
    enforcer.enforce(down, migrate, up, node_removals)


def update_step(time_window, load_extractor, settings):
    end_time = datetime.datetime.now()
    # TODO: remove the "or TRUE"
    if cluster_stable(end_time, time_window, settings):
        log.info("Cluster was stable for {} seconds till {}, calculating best transition".format(time_window.seconds, end_time))
        pods = extract_pods.extract_all_pods()
        nodes = extract_nodes.extract_all_nodes_cpu()

        load = load_extractor.extract_load(end_time, time_window, settings)
        create_time_window(end_time, load, time_window, extract_pods.pods_dict_to_list(pods), nodes)

        transitions = get_best_transitions(load, nodes, settings)
        transition_state(transitions, pods, nodes)
        return True
    else:
        log.info("Cluster was not stable, waiting for the next time_window to check stability")
        global action
        action = "none"
        return False


def tuning_loop(time_window, load_extractor, settings):
    mig_correct = 0
    mig_wrong = 0
    mig_chance_blocked = 0
    rem_correct = 0
    rem_wrong = 0
    old_correct = 0
    old_wrong = 0

    went_wrong_counter = 0
    went_correct_counter = 0
    not_stable_counter = 0
    nodes_to_full_to_move = 0
    while True:
        log.info("Time for an update_step iteration! {}".format(datetime.datetime.now()))
        try:
            if update_step(time_window, load_extractor, settings):
                log.info("went correct")
                if action == "mig":
                    mig_correct += 1
                elif action == "rem":
                    rem_correct += 1
                elif action == "old":
                    old_correct += 1
            else:
                not_stable_counter += 1
        except PodException as e:
            log.info("went wrong: {}".format(type(e)))
            if action == "mig":
                mig_wrong += 1
            elif action == "rem":
                rem_wrong += 1
            elif action == "old":
                old_wrong += 1
            went_wrong_counter += 1
        except MigrationChanceNotMet:
            mig_chance_blocked += 1
        except AllNodesToFullToMove:
            log.info("All nodes to full to do random move")
            nodes_to_full_to_move += 1
        log.info("Update step finished: {}".format(datetime.datetime.now()))
        log.info(f"Current scores\n\
                 Not stable: {not_stable_counter}\n\
                 All nodes full: {nodes_to_full_to_move}\n\
                 Migration correct: {mig_correct} wrong: {mig_wrong} chance blocked: {mig_chance_blocked}\n\
                 Node removal correct: {rem_correct} wrong: {rem_wrong}\n\
                 Old state correct: {old_correct} wrong: {old_wrong}")
        log.info("Going back to sleep")
        time.sleep(time_window.seconds)


def official_startup():
    neo4j_queries.emtpy_graph_database()
    log.info("Graphdatabase emptied")
    warmup_seconds = 900
    log.info("Waiting for warmup to finish. {} seconds".format(warmup_seconds))
    time.sleep(warmup_seconds)


def main():
    #official_startup()
    settings = load_settings.load_settings(sys.argv[1])
    time_window = datetime.timedelta(seconds=settings["measure_window"])
    load_extractor = LoadExtractorBytesIn()
    #try:
    tuning_loop(time_window, load_extractor, settings)
    #except Exception as e:
    #    log.exception(e)
    #remove_file_handler()
    #disconnect_neo4j()


if __name__ == '__main__':
    main()

