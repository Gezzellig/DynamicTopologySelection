from KubernetesAPIConnector import get_k8s_api
from SmartKubernetesSchedular.extract_pods import extract_all_pods


def extract_nodes(nodes_info):
    nodes = {}
    for node_info in nodes_info.items:
        nodes[node_info.metadata.name] = {
            "cpu": float(node_info.status.capacity["cpu"])
        }
    return nodes


def extract_all_nodes():
    nodes_info = get_k8s_api().list_node()
    return extract_nodes(nodes_info)


def extract_all_nodes_with_pods():
    nodes = extract_all_nodes()
    pods = extract_all_pods()
    for pod in pods:
        node_name = pod["node_name"]
        if "pod" in nodes[node_name]:
            nodes[node_name]["pods"].append(pod)
        else:
            nodes[node_name]["pods"] = [pod]
    return nodes
