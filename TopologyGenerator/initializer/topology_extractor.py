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


def extract_topology():
    # Requests all the running containers on the supervised machines.
    response = requests.get("http://localhost:4040/api/topology/containers?stopped=running")
    print(response.status_code)

    nodes = response.json()["nodes"]
    filtered_nodes = {}

    # TODO: allow the recognition of duplicated containers using the container_name.
    node_id = 0
    for node, node_info in nodes.items():
        container_name, image_name, image_tag = extract_node_metadata(node_info)
        # TODO removing hardcoded ignore of images that are needed for topology generation
        if image_name == "neo4j" or image_name == "google/cadvisor" or image_name == "prom/prometheus":
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
    topology = extract_topology()
    initialize_graph.initialize_graph(settings, topology)


if __name__ == '__main__':
    main()
