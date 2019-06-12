import datetime
import math
import sys

import load_settings
from SmartKubernetesSchedular import enforcer, rank_executions
from SmartKubernetesSchedular.deployment import state_transition_plan
from SmartKubernetesSchedular.load_extractors.LoadExtractorBytesIn import LoadExtractorBytesIn
from SmartKubernetesSchedular.retrieve_executions import retrieve_executions
from SmartKubernetesSchedular.strategies.TryEmptyOneNode import TryEmptyOneNode, calc_removal_resulting_cost
from SmartKubernetesSchedular.time_window import create_time_window
from kubernetes_tools import extract_pods, extract_nodes
from SmartKubernetesSchedular.strategies.RandomPodMigrationInNameSpace import RandomPodMigrationInNameSpace
from kubernetes_tools.extract_nodes import calc_cost


def loop(time_window, settings):
    end_time = datetime.datetime.now()
    load_extractor = LoadExtractorBytesIn()
    load = load_extractor.extract_load(end_time, time_window, settings)
    pods = extract_pods.pods_dict_to_list(extract_pods.extract_all_pods())
    nodes = extract_nodes.extract_all_nodes_cpu()
    create_time_window(end_time, load, time_window, pods, nodes)

    removal_possible, removal_transitions = TryEmptyOneNode().generate_improvement(settings)
    removal_resulting_cost = math.inf
    print(removal_transitions)
    cur_cost = calc_cost(nodes, settings)
    if removal_possible:
        removal_resulting_cost = calc_removal_resulting_cost(nodes, removal_transitions, settings)
        print("cost removal:", removal_resulting_cost)

    old_executions = retrieve_executions(load, settings)
    old_best_execution = rank_executions.find_best_execution(old_executions, settings["prometheus_address"])
    print(old_best_execution)

    old_best_execution_cost = calc_cost(old_best_execution["nodes"], settings)
    if removal_resulting_cost <= old_best_execution_cost:
        print("TAKE REMOVAL ACTION")

        return
    elif cur_cost <= old_best_execution_cost:
        print("Staying with current execution, but randomly changing one random pod")
        return
    else:
        print("Changing to old_best_execution found in time: {}".format(old_best_execution["start_time"]))
        # Todo implement this transition.





def transition_state(transitions, pods, nodes):
    print(transitions)
    down, migrate, up = state_transition_plan(transitions, pods, nodes)
    print(down)
    print(migrate)
    print(up)
    enforcer.enforce(down, migrate, up)


def main():
    settings = load_settings.load_settings(sys.argv[1])
    time_window = datetime.timedelta(seconds=settings["measure_window"])
    loop(time_window, settings)
    """algorithm = TryEmptyOneNode()

    initial_pods = extract_pods.extract_all_pods()
    initial_nodes = extract_nodes.extract_all_nodes_cpu()
    success, transitions = algorithm.generate_improvement(settings)
    if success:
        transition_state(transitions, initial_pods, initial_nodes)"""


if __name__ == '__main__':
    main()
