from neo4j import GraphDatabase


def main():
    print("lets go")
    driver = GraphDatabase.driver("bolt://localhost", auth=("neo4j", "neo"))
    print("connected")
    sess = driver.session()
    result = sess.run("MATCH (nineties:Movie) WHERE nineties.released >= 1990 AND nineties.released < 2000 RETURN nineties.title")
    for record in result:
        print(record["nineties.title"])
    driver.close()
    print("disconnected")


if __name__ == "__main__":
    main()
