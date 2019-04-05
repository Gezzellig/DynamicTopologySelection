import json
import sys
import requests

from initializer import initialize_graph


def extract_node_metadata(node_info):
    image_name = "NO IMAGE NAME FOUND"
    for entry in node_info["metadata"]:
        if entry["label"] == "Image name":
            image_name = entry["value"]

            #TODO removing hardcoded ignore of images that are needed for topology generation
            if image_name == "neo4j":
                break
    return image_name


def extract_node_adjacency(node, node_info):
    #Self loops are removed
    print("ADJEACENFE")
    adjacency = []
    print(node_info)
    if "adjacency" in node_info:
        print("IT IS HERE")
        for adjacent in node_info["adjacency"]:
            print("comparing: {} to {}".format(node, adjacent))
            if not node == adjacent:
                adjacency.append(adjacent)
    return adjacency


def convert_to_topology_notation(filtered_nodes):
    topology = {"images": [],
                "connections": []}
    for node, filtered_info in filtered_nodes.items():
        image = {"id": filtered_info["id"],
                 "image_name": filtered_info["image_name"],
                 "image_version": "NOT_IMPLEMENTED",
                 "replication": "NOT_RELEVANT_HERE"}
        topology["images"].append(image)
        for other in filtered_info["adjacency"]:
            topology["connections"].append({"source_id": filtered_info["id"],
                                            "destination_id": filtered_nodes[other]["id"]})
    return topology



def extract_topology():
    #requests all the running containers on the supervised machines.
    response = requests.get("http://localhost:4040/api/topology/containers?stopped=running")
    print(response.status_code)

    nodes = response.json()["nodes"]
    print(nodes)
    filtered_nodes = {}

    #TODO: allow the recognition of duplicated containers.
    node_id = 0
    for node, node_info in nodes.items():
        filtered_node = {"id": node_id,
                         "image_name": extract_node_metadata(node_info),
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
    print(settings)
    topology = extract_topology()
    initialize_graph.initialize_graph(settings, topology)


if __name__ == '__main__':
    main()
