from neo4j import GraphDatabase

class Neo4jGraphDriver:
    def __init__(self):
        self.driver = None
        self.connect()

    def connect(self):
        self.driver = GraphDatabase.driver("bolt://localhost", auth=("neo4j", "neo"))

    def disconnect(self):
        self.driver.close()

    def session(self):
        return self.driver.session()
