from neo4j import GraphDatabase

neo4j_driver = GraphDatabase.driver("bolt://localhost", auth=("neo4j", "neo"))
