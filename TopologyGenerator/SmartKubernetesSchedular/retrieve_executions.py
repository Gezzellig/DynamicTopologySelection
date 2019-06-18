import datetime
import math
import sys

import load_settings
from Neo4jGraphDriver import disconnect_neo4j
from initializer.neo4j_queries import execute_query_function


class NoExecutionsFoundException(Exception):
    pass


def retrieve_executions_on_load(tx, load, delta_load):
    return tx.run("match (e:Execution) -[:HasNode]-> (n:Node) \
                    where $load_min <= e.load <= $load_max \
                    return id(e) as id, collect({name:n.name, cpu:n.cpu, memory:n.memory}) as nodes",
                  load_min=load-(load*delta_load), load_max=load+(load*delta_load))


def retrieve_cheapest_executions(load, delta_load, price_per_core, price_per_gb):
    executions = execute_query_function(retrieve_executions_on_load, load, delta_load)
    cheapest_cost = math.inf
    cheapest_execution_ids = []
    for execution in executions.records():
        total_cost = 0
        for node in execution["nodes"]:
            total_cost += node["cpu"]*price_per_core + node["memory"]*price_per_gb

        if total_cost == cheapest_cost:
            cheapest_execution_ids.append(execution["id"])
        elif total_cost < cheapest_cost:
            cheapest_cost = total_cost
            cheapest_execution_ids = [execution["id"]]
    return cheapest_execution_ids


def retrieve_full_execution_data(tx, execution_ids):
    return tx.run("unwind $execution_ids as execution_id \
                    match (e:Execution) where id(e) = execution_id \
                    match (e) -[:HasNode]-> (n:Node) \
                    match (n) -[r:Ran]-> (p:Pod) \
                    with e, n, collect({name:r.name, generate_name:p.generate_name, kind:p.kind}) as pods \
                    return id(e) as id, e.start_time.epochMillis as start_time, e.end_time.epochMillis as end_time, collect({name:n.name, cpu:n.cpu, pods:pods, memory:n.memory}) as nodes",
                  execution_ids=execution_ids)


def extract_node_from_data_node(data_node):
    pods = {}
    node_name = data_node["name"]
    for data_pod in data_node["pods"]:
        pods[data_pod["name"]] = {
            "node_name": node_name,
            "pod_generate_name": data_pod["generate_name"],
            "kind": data_pod["kind"]
        }
    node = {
        "cpu": data_node["cpu"],
        "memory": data_node["memory"],
        "pods": pods
    }
    return node


def retrieve_full_executions(execution_ids):
    data_executions = execute_query_function(retrieve_full_execution_data, execution_ids)
    executions = []
    for data_execution in data_executions.records():
        nodes = {}
        for data_node in data_execution["nodes"]:
            nodes[data_node["name"]] = extract_node_from_data_node(data_node)
        executions.append({
            "execution_id": data_execution["id"],
            "start_time": datetime.datetime.fromtimestamp(data_execution["start_time"]/1000),
            "end_time": datetime.datetime.fromtimestamp(data_execution["end_time"]/1000),
            "nodes": nodes
        })
    return executions


def retrieve_single_execution(execution_id):
    return retrieve_full_executions([execution_id])[0]


def retrieve_executions(load, settings):
    load_delta = settings["load_delta"]
    price_per_core = settings["price_per_core"]
    price_per_gb = settings["price_per_gb"]
    cheapest_executions_ids = retrieve_cheapest_executions(load, load_delta, price_per_core, price_per_gb)
    if not cheapest_executions_ids:
        raise NoExecutionsFoundException()
    executions = retrieve_full_executions(cheapest_executions_ids)
    return executions


def main():
    settings = load_settings.load_settings(sys.argv[1])
    print(retrieve_executions(10000, settings))
    disconnect_neo4j()


if __name__ == '__main__':
    main()
