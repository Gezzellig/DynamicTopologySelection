from datetime import datetime

from Neo4jGraphDriver import get_neo4j_session


def retrieve_all_container_names_command(tx):
    return tx.run("MATCH (n:IMAGE) RETURN n.container_name AS container_name")


def retrieve_all_container_names():
    container_names = []
    with get_neo4j_session() as session:
        containers_holder = session.write_transaction(retrieve_all_container_names_command)
    for container_holder in containers_holder:
        container_names.append(container_holder["container_name"])
    return container_names


def create_execution_node_command_OLDD(tx, load, start_time, end_time, combinations):
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


def create_execution_node_command(tx, load, start_time, end_time, pods):
    return tx.run("CREATE (e:EXECUTION {load:$load, start_time:datetime({ epochMillis: $start_time }), end_time:datetime({ epochMillis: $end_time})}) \
                    WITH e \
                    UNWIND $pods as pod \
                    MERGE (e)-[:HAS_NODE]->(n:NODE {name:pod.node_name}) \
                    WITH n, pod.containers as containers, pod.pod_name as pod_name \
                    MATCH (p:IMAGE)<-[:CONTAINS]-(m:COMBINATION) \
                    WHERE p.container_name in containers \
                    WITH n, m, size(containers) as inputCnt, count(DISTINCT p) as cnt, pod_name \
                    WHERE cnt = inputCnt \
                    WITH n, m, inputCnt, pod_name\
                    MATCH (q:IMAGE)<-[:CONTAINS]-(m:COMBINATION) WITH n, m, inputCnt, count(q) as total_cnt, pod_name \
                    WHERE inputCnt = total_cnt \
                    WITH n, m, pod_name \
                    CREATE (n)-[:RAN{pod_name:pod_name}]->(m)",
                    load=load, start_time=int(start_time.timestamp()*1000), end_time=int(end_time.timestamp()*1000), pods=pods,
                  )


def create_execution_node(load, start_time, end_time, pods):
    with get_neo4j_session() as session:
        return session.write_transaction(create_execution_node_command, load, start_time, end_time, pods)


def get_start_end_times_executions_command(tx, load):
    return tx.run("MATCH (e:EXECUTION{load:$load}) RETURN e.start_time AS start_time, e.end_time AS end_time", load=load)


def get_start_end_times_executions(load):
    with get_neo4j_session() as session:
        results = session.write_transaction(get_start_end_times_executions_command, load)
    start_end_times = []
    for result in results:
        start = result["start_time"]
        end = result["end_time"]
        start_end_times.append({
            "start_time": datetime(start.year, start.month, start.day, start.hour, start.minute, int(start.second), int(start.second * 1000 % 1000)),
            "end_time": datetime(end.year, end.month, end.day, end.hour, end.minute, int(end.second), int(end.second * 1000 % 1000)),
        })
    return start_end_times


def empty_graph_database_command(tx):
    tx.run("MATCH (n) DETACH DELETE n")


def emtpy_graph_database():
    execute_query_function(empty_graph_database_command)


def execute_query_function(func, *par):
    with get_neo4j_session() as session:
        return session.write_transaction(func, *par)

