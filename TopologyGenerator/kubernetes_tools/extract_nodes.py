from KubernetesAPIConnector import get_k8s_api
from kubernetes_tools import extract_pods


def extract_nodes_cpu(nodes_info):
    nodes = {}
    for node_info in nodes_info.items:
        nodes[node_info.metadata.name] = {
            "cpu": float(node_info.status.capacity["cpu"]),
            "memory": float(node_info.status.capacity["memory"].split("K")[0])/1048576  # get value from Kilo to Giga
        }
    return nodes


def extract_all_nodes_cpu():
    nodes_info = get_k8s_api().list_node()
    return extract_nodes_cpu(nodes_info)


def extract_generate_per_node():
    pods = extract_pods.extract_all_pods()
    generate_per_node = {}
    for name, info in pods.items():
        generate_per_node[info["node_name"]] = info["pod_generate_name"]
    return generate_per_node

def extract_all_nodes_cpu_pods():
    nodes = extract_all_nodes_cpu()
    for info in nodes.values():
        info["pods"] = []
    pods = extract_pods.pods_dict_to_list(extract_pods.extract_all_pods())
    for info in pods:
        nodes[info["node_name"]]["pods"].append(info)
    return nodes


def node_sum_requested(node_pods):
    requested = 0.0
    for pod_info in node_pods["pods"]:
        requested += pod_info["total_requested"]
    return requested


def node_request_fits(node_cpu_pods):
    return node_cpu_pods["cpu"] >= node_sum_requested(node_cpu_pods)




