import copy
import math
import random

from SmartKubernetesSchedular import deployment
from SmartKubernetesSchedular.rank_executions import retrieve_nodes_cpu_usage
from kubernetes_tools import extract_nodes, extract_pods
from SmartKubernetesSchedular.strategies.AbstractStratagy import AbstractStratagy, CouldNotGenerateImprovementException
from kubernetes_tools.extract_nodes import node_request_fits, node_sum_requested, calc_cost


class TryEmptyOneNode(AbstractStratagy):

    def generate_improvement(self, settings):
        nodes = extract_nodes.extract_all_nodes_cpu_pods()
        removable_nodes = select_removable_nodes(nodes)
        candidate_node_name = least_transitions_removable(removable_nodes, nodes)
        if candidate_node_name is None:
            print("No node could be shutdown for improvement, because all nodes have a statefull set")
            return False, None

        for pod in nodes[candidate_node_name]["pods"]:
            print(pod["pod_name"])

        reschedule_pods = find_pods_to_be_rescheduled(nodes[candidate_node_name]["pods"])
        nodes_node_removed = copy.deepcopy(nodes)
        del nodes_node_removed[candidate_node_name]
        distributions = find_new_distributions(reschedule_pods, nodes_node_removed)
        if not distributions:
            print("No node could be shutdown for improvement, because all the resources are needed")
            return False, None
        selected_distribution = select_lowest_max_requested(distributions)
        print("Emptying node: {}".format(candidate_node_name))
        return True, change_selected_distribution_into_transitions(selected_distribution, nodes)


def node_removable(pods_info):
    for pod_info in pods_info:
        if pod_info["kind"] == "StatefulSet":
            return False
    return True


def select_removable_nodes(nodes):
    removable_nodes = []
    for name, node_info in nodes.items():
        if node_removable(node_info["pods"]):
            removable_nodes.append(name)
    return removable_nodes


def find_pods_to_be_rescheduled(pods):
    reschedule = []
    for pod in pods:
        if not pod["kind"] == "DaemonSet":
            reschedule.append(pod)
    return reschedule

# Todo change to least amount of cpu usage
def least_transitions_removable(removable_nodes, nodes):
    least_transitions = math.inf
    least_transitions_node = None
    for node_name in removable_nodes:
        num_pods = len(find_pods_to_be_rescheduled(nodes[node_name]["pods"]))
        if num_pods < least_transitions:
            least_transitions = num_pods
            least_transitions_node = node_name
    return least_transitions_node


def recursive_find_new_distributions(reschedule_pods, new_nodes):
    #Base case no pods have to be rescheduled anymore
    if not reschedule_pods:
        return [new_nodes]

    #Recursive step
    suitable_distributions = []
    pod = reschedule_pods.pop()
    for node_name in new_nodes.keys():
        new_new_nodes = copy.deepcopy(new_nodes)
        new_new_nodes[node_name]["pods"].append(pod)
        if node_request_fits(new_new_nodes[node_name]):
            suitable_distributions += recursive_find_new_distributions(copy.deepcopy(reschedule_pods), new_new_nodes)
    return suitable_distributions


def find_new_distributions(reschedule_pods, new_nodes):
    return recursive_find_new_distributions(copy.deepcopy(reschedule_pods), copy.deepcopy(new_nodes))


def get_max_requested(distribution):
    max_requested = 0.0
    for node_info in distribution.values():
        requested = node_sum_requested(node_info)
        if requested > max_requested:
            max_requested = requested
    return max_requested


def select_lowest_max_requested(distributions):
    lowest_max_requested = math.inf
    lowest_max_requested_distribution = None
    for distribution in distributions:
        max_requested = get_max_requested(distribution)
        if max_requested < lowest_max_requested:
            lowest_max_requested = max_requested
            lowest_max_requested_distribution = distribution
    return lowest_max_requested_distribution


def change_selected_distribution_into_transitions(selected_distribution, original_distribution):
    transitions = {}
    for node_name, node_info in selected_distribution.items():
        for pod in node_info["pods"]:
            if pod not in original_distribution[node_name]["pods"]:
                if pod["node_name"] not in transitions:
                    transitions[pod["node_name"]] = {"add": [], "remove": []}
                transitions[pod["node_name"]]["remove"].append(pod["pod_name"])
                if node_name not in transitions:
                    transitions[node_name] = {"add": [], "remove": []}
                transitions[node_name]["add"].append(pod["pod_generate_name"])
    return transitions


def calc_removal_resulting_cost(nodes, transitions, settings):
    copy_nodes = copy.deepcopy(nodes)
    print("hier")
    for node_name, transition in transitions.items():
        if transition["remove"]:
            print("removed:", node_name)
            del copy_nodes[node_name]
            break
    return calc_cost(copy_nodes, settings)

