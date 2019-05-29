from neo4j import GraphDatabase


class Neo4jGraphDriver:
    class __Neo4jGraphDriver:
        def __init__(self):
            self.driver = None
            self.connect()

        def connect(self):
            self.driver = GraphDatabase.driver("bolt://localhost", auth=("neo4j", "neo"))
            pass

        def disconnect(self):
            self.driver.close()

        def session(self):
            return self.driver.session()

    instance = None

    def __init__(self):
        if not Neo4jGraphDriver.instance:
            Neo4jGraphDriver.instance = Neo4jGraphDriver.__Neo4jGraphDriver()


def disconnect_neo4j():
    singleton = Neo4jGraphDriver()
    singleton.instance.disconnect()
    singleton.instance = None


def get_neo4j_driver():
    return Neo4jGraphDriver().instance


def get_neo4j_session():
    return Neo4jGraphDriver().instance.session()
