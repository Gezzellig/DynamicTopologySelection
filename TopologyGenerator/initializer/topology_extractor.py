import json
import sys
import requests

from initializer import initialize_graph


def extract_node_metadata(node_info):
    container_name = node_info["label"]
    image_name = "NO IMAGE NAME FOUND"
    image_tag = "NO TAG FOUND"
    for entry in node_info["metadata"]:
        if entry["id"] == "docker_image_name":
            image_name = entry["value"]
        if entry["id"] == "docker_image_tag":
            image_tag = entry["value"]
    return container_name, image_name, image_tag


def extract_node_tables(node_info):
    namespace = "NO NAMESPACE FOUND"
    for table in node_info["tables"]:
        if table["id"] == "docker_label_":
            for row in table["rows"]:
                if row["id"] == "label_io.kubernetes.pod.namespace":
                    namespace = row["entries"]["value"]
    return namespace


def extract_node_adjacency(node, node_info):
    # Self loops are removed
    adjacency = []
    if "adjacency" in node_info:
        for adjacent in node_info["adjacency"]:
            if not node == adjacent:
                adjacency.append(adjacent)
    return adjacency


def convert_to_topology_notation(filtered_nodes):
    topology = {"images": [],
                "connections": []}
    for node, filtered_info in filtered_nodes.items():
        image = {"id": filtered_info["id"],
                 "container_name": filtered_info["container_name"],
                 "image_name": filtered_info["image_name"],
                 "image_tag": filtered_info["image_tag"],
                 "replication": "NOT_IMPLEMENTED"}
        topology["images"].append(image)
        for other in filtered_info["adjacency"]:
            topology["connections"].append({"source_id": filtered_info["id"],
                                            "destination_id": filtered_nodes[other]["id"]})
    print(topology)
    return topology


def extract_topology(settings):
    # Requests all the running containers on the supervised machines.
    command = "http://{}/api/topology/containers?stopped=running".format(settings["weave_scope_address"])
    print(command)
    response = requests.get(command)
    print(response.status_code)

    nodes = response.json()["nodes"]
    filtered_nodes = {}

    # TODO: allow the recognition of duplicated containers using the container_name.
    node_id = 0
    for node, node_info in nodes.items():
        container_name, image_name, image_tag = extract_node_metadata(node_info)
        namespace = extract_node_tables(node_info)

        #skip all nodes found by node that aren't relevant to the project observed
        if not namespace == settings["kubernetes_project_namespace"]:
            print("Skipping: {}".format(container_name))
            continue

        filtered_node = {"id": node_id,
                         "container_name": container_name,
                         "image_name": image_name,
                         "image_tag": image_tag,
                         "adjacency": extract_node_adjacency(node, node_info)}
        filtered_nodes[node] = filtered_node
        node_id += 1
    return convert_to_topology_notation(filtered_nodes)


def main():
    print("Starting extracting topology")
    setting_file_name = sys.argv[1]
    print("Settings: {}".format(setting_file_name))
    with open(setting_file_name) as file:
        settings = json.load(file)
    topology = extract_topology(settings)
    initialize_graph.initialize_graph(settings, topology)


if __name__ == '__main__':
    main()
