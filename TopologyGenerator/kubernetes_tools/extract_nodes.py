from KubernetesAPIConnector import get_k8s_api


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



