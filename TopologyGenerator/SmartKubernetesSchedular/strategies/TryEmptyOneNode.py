import random

from SmartKubernetesSchedular import deployment
from kubernetes_tools import extract_nodes, extract_pods
from SmartKubernetesSchedular.strategies.AbstractStratagy import AbstractStratagy, CouldNotGenerateImprovementException


class TryEmptyOneNode(AbstractStratagy):

    def generate_improvement(self, settings):
        nodes = extract_nodes.extract_all_nodes_cpu_pods()
        removable_nodes = select_removable_nodes(nodes)
        print(removable_nodes)



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


def check_if_node_can_be_removed(remove_node_name, nodes):
    reschedule = find_pods_to_be_rescheduled(nodes[remove_node_name]["pods"])
    for pod in reschedule:
        for node_name, info in nodes.items():
            if node_name == remove_node_name:
                continue
