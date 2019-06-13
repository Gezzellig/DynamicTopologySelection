import datetime
import math
import random
import sys

import load_settings
from SmartKubernetesSchedular import enforcer, rank_executions
from SmartKubernetesSchedular.deployment import state_transition_plan
from SmartKubernetesSchedular.load_extractors.LoadExtractorBytesIn import LoadExtractorBytesIn
from SmartKubernetesSchedular.matcher import match_nodes_desired_with_current_state, find_transitions_execution_change
from SmartKubernetesSchedular.retrieve_executions import retrieve_executions
from SmartKubernetesSchedular.strategies.TryEmptyOneNode import TryEmptyOneNode, calc_removal_resulting_cost
from SmartKubernetesSchedular.time_window import create_time_window
from kubernetes_tools import extract_pods, extract_nodes
from kubernetes_tools.cluster_stability import cluster_stable
from kubernetes_tools.extract_nodes import calc_cost, node_sum_requested


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

        if node_sum_requested(destination_node_info) + pod["total_requested"] < destination_node_info["cpu"]:
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
    raise Exception("Randomness was forever in our disfavor (or all nodes are perfectly filled)")


def get_best_transitions(end_time, time_window, pods, nodes, settings):
    load_extractor = LoadExtractorBytesIn()
    load = load_extractor.extract_load(end_time, time_window, settings)
    create_time_window(end_time, load, time_window, pods, nodes)

    removal_possible, removal_transitions = TryEmptyOneNode().generate_improvement(settings)
    removal_resulting_cost = math.inf
    cur_cost = calc_cost(nodes, settings)
    if removal_possible:
        removal_resulting_cost = calc_removal_resulting_cost(nodes, removal_transitions, settings)
        print("cost removal:", removal_resulting_cost)

    old_executions = retrieve_executions(load, settings)
    old_best_execution = rank_executions.find_best_execution(old_executions, settings["prometheus_address"])
    old_best_execution_cost = calc_cost(old_best_execution["nodes"], settings)

    print("costs for all options: current= {}, removal= {}, old_best= {}".format(cur_cost, removal_resulting_cost, old_best_execution_cost))
    if removal_resulting_cost <= old_best_execution_cost:
        print("TAKE REMOVAL ACTION")
        return removal_transitions
    elif cur_cost <= old_best_execution_cost:
        print("Staying with current execution, but randomly changing one random pod")
        current_state = extract_nodes.extract_all_nodes_cpu_pods()
        return select_random_deployment_pod_to_transition(current_state)
    else:
        print("Changing to old_best_execution found in time: {}".format(old_best_execution["start_time"]))
        current_state = extract_nodes.extract_all_nodes_cpu_pods()
        return find_transitions_execution_change(current_state, old_best_execution["nodes"])


def transition_state(transitions, pods, nodes):
    print(transitions)
    down, migrate, up = state_transition_plan(transitions, pods, nodes)
    print(down)
    print(migrate)
    print(up)
    enforcer.enforce(down, migrate, up)


def update_step(time_window, settings):
    end_time = datetime.datetime.now()
    if cluster_stable(end_time, time_window, settings):
        print("Cluster was stable for {} seconds till {}, calculating best transition".format(time_window.seconds, end_time))
        pods = extract_pods.extract_all_pods()
        nodes = extract_nodes.extract_all_nodes_cpu()
        transitions = get_best_transitions(end_time, time_window, extract_pods.pods_dict_to_list(pods), nodes, settings)
        transition_state(transitions, pods, nodes)
    else:
        print("Cluster was not stable, waiting for the next time_window to check stability")


def nice_print():
    pods = extract_pods.extract_all_pods()
    for pod_name, pod_info in pods.items():
        print(pod_name, pod_info["kind"], pod_info["pod_generate_name"], pod_info["deployment_name"])


def main():
    settings = load_settings.load_settings(sys.argv[1])
    time_window = datetime.timedelta(seconds=settings["measure_window"])
    update_step(time_window, settings)
    """algorithm = TryEmptyOneNode()

    initial_pods = extract_pods.extract_all_pods()
    initial_nodes = extract_nodes.extract_all_nodes_cpu()
    success, transitions = algorithm.generate_improvement(settings)
    if success:
        transition_state(transitions, initial_pods, initial_nodes)"""


if __name__ == '__main__':
    main()
