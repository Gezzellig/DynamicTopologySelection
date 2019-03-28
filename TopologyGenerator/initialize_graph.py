import json
import sys

from neo4j import GraphDatabase
from jsonschema import validate

from SetWithCrossProduct import SetWithCrossProduct


class TopologyGraph:
    def __init__(self):
        self.driver = GraphDatabase.driver("bolt://localhost", auth=("neo4j", "neo"))

    def add_image_node(self, image_id, image_name, image_version, replication):
        command = "CREATE (:IMAGE {{image_id:{image_id}, image_name:'{image_name}', image_version:'{image_version}'}})".format(image_id=image_id, image_name=image_name, image_version=image_version)
        self.execute_command(command)

    def add_image_connection(self, source_id, destination_id):
        command = "MATCH (n), (m) " \
                  "WHERE n.image_id = {source_id} AND m.image_id = {destination_id} "\
                  "CREATE (n)-[:CONNECTS_TOO]->(m)".format(source_id=source_id, destination_id=destination_id)
        self.execute_command(command)

    def generate_possible_image_combinations(self):
        all_nodes_id_command = "MATCH (n:IMAGE) SET n.started = false RETURN ID(n) AS node_id"
        results = self.execute_command(all_nodes_id_command)

        for record in results:
            master_node_id = record["node_id"]

            all_paths_one_node_command = "MATCH p = (n:IMAGE) -[:CONNECTS_TOO *0..]- (:IMAGE) WHERE id(n)={} AND all(m IN nodes(p) WHERE m.started=false) RETURN NODES(p) AS path".format(master_node_id)
            paths = self.execute_command(all_paths_one_node_command)
            unique_paths = SetWithCrossProduct()
            for path in paths:
                path_list = list()
                for node in path["path"]:
                    path_list.append(node.id)
                unique_paths.add(frozenset(path_list))
            for unique_path in unique_paths.get():
                create_combination_command = "CREATE (c:COMBINATION) WITH (c) MATCH (n:IMAGE) WHERE ID(n) in {} MERGE (c)-[:CONTAINS]->(n)".format(list(unique_path))
                self.execute_command(create_combination_command)
            set_node_to_visited_command = "MATCH (n:IMAGE) WHERE ID(n) = {} SET n.started = true".format(master_node_id)
            self.execute_command(set_node_to_visited_command)
        #command = "MATCH p =(n:IMAGE)-[:CONNECTS_TOO *0..]->(:IMAGE) CREATE (o:COMBINATION) FOREACH (m IN nodes(p)| CREATE (o)-[:CONTAINS]->(m) )"
        #self.execute_command(command)

    def empty_graph(self):
        command = "MATCH (n) " \
                  "OPTIONAL MATCH (n)-[r]-()" \
                  "DELETE n, r"
        self.execute_command(command)
        print("Graph emptied")

    def execute_command(self, command):
        print("executed on NEO4J: {}".format(command))
        return self.driver.session().run(command)

    def disconnect(self):
        self.driver.close()
        print("disconnected")

"""topology_schema = {
    "type": "object"
    "properties": {
        "type": "array",
        "items": {
            "type": "number"
        }
    }
}"""

#def add_image_node(id, image_name, replication):


def main():
    topology_file_name = sys.argv[1]
    print("Using: {}".format(topology_file_name))
    with open(topology_file_name) as file:
        json_topology = json.load(file)
    #validate(json_topology, topology_schema)

    topology_graph = TopologyGraph()
    # EMPTYING THE GRAPH to start with a clean sheet
    topology_graph.empty_graph()

    for image in json_topology["images"]:
        id = image["id"]
        image_name = image["image_name"]
        image_version = image["image_version"]
        replication = image["replication"]
        image_id = topology_graph.add_image_node(id, image_name, image_version, replication)

    for connection in json_topology["connections"]:
        source_id = connection["source_id"]
        destination_id = connection["destination_id"]
        topology_graph.add_image_connection(source_id, destination_id)
    print("done")

    topology_graph.generate_possible_image_combinations()
    topology_graph.disconnect()






    """
    print("lets go")
    driver = GraphDatabase.driver("bolt://localhost", auth=("neo4j", "neo"))
    print("connected")
    sess = driver.session()
    result = sess.run("MATCH (nineties:Movie) WHERE nineties.released >= 1990 AND nineties.released < 2000 RETURN nineties.title")
    for record in result:
        print(record["nineties.title"])
    
    #Gives a single result, and otherwise a warning
    result.single()
    
    driver.close()
    print("disconnected")"""


if __name__ == "__main__":
    main()
