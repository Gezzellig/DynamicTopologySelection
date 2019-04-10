from initializer import neo4j_driver


def retrieve_all_container_names_command(tx):
    return tx.run("MATCH (n:IMAGE) RETURN n.container_name AS container_name")


def retrieve_all_container_names():
    container_names = []
    with neo4j_driver.driver.session() as session:
        containers_holder = session.write_transaction(retrieve_all_container_names_command)
    for container_holder in containers_holder:
        container_names.append(container_holder["container_name"])
    return container_names

def retrieve_combination_connected_to_list_of_containers_command(tx):
    command = "WITH $container_list AS container_names \
    MATCH(p: IMAGE) < -[: CONTAINS]-(m:COMBINATION) WHERE p.container_name in container_names \
    WITH m, container_names, size(container_names) as inputCnt, count(DISTINCT p) as cnt \
    WHERE cnt = inputCnt \
    MATCH(q: IMAGE) < -[: CONTAINS]-(m:COMBINATION) WITH m, inputCnt, count(q) as total_cnt \
    WHERE inputCnt = total_cnt \
    RETURN m"
    tx.run(command)


def create_execution_node_command(tx, load, start_time, end_time, combinations):
    return tx.run("CREATE (e:EXECUTION {load:$load, start_time:datetime({ epochMillis: $start_time }), end_time:datetime({ epochMillis: $end_time})}) \
                    WITH e \
                    UNWIND $combinations as container_names \
                    MATCH (p:IMAGE)<-[:CONTAINS]-(m:COMBINATION) \
                    WHERE p.container_name in container_names \
                    WITH e, m, container_names, size(container_names) as inputCnt, count(DISTINCT p) as cnt \
                    WHERE cnt = inputCnt \
                    MATCH (q:IMAGE)<-[:CONTAINS]-(m:COMBINATION) WITH e, m, inputCnt, count(q) as total_cnt \
                    WHERE inputCnt = total_cnt \
                    CREATE (e)-[:RAN]->(m)"
                  , load=load, start_time=int(start_time.timestamp()*1000), end_time=int(end_time.timestamp()*1000), combinations=combinations)


def create_execution_node(load, start_time, end_time, combinations):
    with neo4j_driver.driver.session() as session:
        session.write_transaction(create_execution_node_command, load, start_time, end_time, combinations)

def retrieve_combination_connected_to_list_of_containers(container_list):
    pass
