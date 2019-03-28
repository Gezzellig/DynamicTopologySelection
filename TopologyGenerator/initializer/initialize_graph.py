import json
import sys

from initializer import neo4j
from initializer.SetWithCrossProduct import SetWithCrossProduct


def emtpy_graph_command(tx):
    tx.run("MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n, r")


def create_image_node_command(tx, image_id, image_name, image_version, replication):
    return tx.run("CREATE (:IMAGE {image_id:$image_id, image_name:'$image_name', image_version:'$image_version'})", image_id=image_id, image_name=image_name, image_version=image_version)


def create_connects_too_relation_command(tx, source_id, destination_id):
    tx.run("MATCH (n), (m) WHERE n.image_id = $source_id AND m.image_id = $destination_id CREATE (n)-[:CONNECTS_TOO]->(m)", source_id=source_id, destination_id=destination_id)


def create_combination_node_command(tx, nodes):
    return tx.run("CREATE (c:COMBINATION) WITH (c) MATCH (n:IMAGE) WHERE ID(n) in $nodes MERGE (c)-[:CONTAINS]->(n);", nodes=nodes)


def fetch_all_image_nodes_command(tx):
    return tx.run("MATCH (n:IMAGE) SET n.started = false RETURN ID(n) AS node_id")


def fetch_all_paths_one_node(tx, master_image_id, max_images_combined=-1):
    if max_images_combined > 0:
        max_images_string = max_images_combined - 1
    else:
        max_images_string = ""
    return tx.run("MATCH p = (n:IMAGE) -[:CONNECTS_TOO *0..{}]- (:IMAGE) WHERE ID(n)=$id AND all(m IN nodes(p) WHERE m.started=false) RETURN NODES(p) AS path".format(max_images_string), id=master_image_id)


def set_image_started_true(tx, master_node_id):
    return tx.run("MATCH (n:IMAGE) WHERE ID(n) = $id SET n.started = true", id=master_node_id)


def emtpy_graph():
    with neo4j.driver.session() as session:
        session.write_transaction(emtpy_graph_command)
    print("Graph emptied")


def create_all_image_nodes(json_topology):
    with neo4j.driver.session() as session:
        for image in json_topology["images"]:
            image_id = image["id"]
            image_name = image["image_name"]
            image_version = image["image_version"]
            replication = image["replication"]
            session.write_transaction(create_image_node_command, image_id, image_name, image_version, replication)
    print("Image nodes created")


def create_all_connects_too_relations(json_topology):
    with neo4j.driver.session() as session:
        for connection in json_topology["connections"]:
            source_id = connection["source_id"]
            destination_id = connection["destination_id"]
            session.write_transaction(create_connects_too_relation_command, source_id, destination_id)
    print("Connections between images nodes made")


def generate_possible_image_combinations(master_node_id, max_images_combined=-1):
    with neo4j.driver.session() as session:
        paths = session.write_transaction(fetch_all_paths_one_node, master_node_id, max_images_combined)
    unique_paths = SetWithCrossProduct(max_images_combined)
    for path in paths:
        path_list = list()
        for node in path["path"]:
            path_list.append(node.id)
        unique_paths.add(frozenset(path_list))

    with neo4j.driver.session() as session:
        for unique_path in unique_paths.get():
            session.write_transaction(create_combination_node_command, list(unique_path))
        session.write_transaction(set_image_started_true, master_node_id)


def generate_all_possible_image_combinations(max_images_combined=-1):
    with neo4j.driver.session() as session:
        results = session.write_transaction(fetch_all_image_nodes_command)
    for record in results:
        generate_possible_image_combinations(record["node_id"], max_images_combined)
    print("Possible combinations generated with max: {}".format(max_images_combined))


def main():
    setting_file_name = sys.argv[1]
    topology_file_name = sys.argv[2]
    print("Settings: {}, Topology: {}".format(setting_file_name, topology_file_name))
    with open(topology_file_name) as file:
        json_topology = json.load(file)
    with open(setting_file_name) as file:
        json_settings = json.load(file)

    # EMPTYING THE GRAPH to start with a clean sheet
    emtpy_graph()
    create_all_image_nodes(json_topology)
    create_all_connects_too_relations(json_topology)
    generate_all_possible_image_combinations(json_settings["max_images_combined"])


if __name__ == "__main__":
    main()
