import math

from Neo4jGraphDriver import disconnect_neo4j
from initializer.neo4j_queries import execute_query_function


def retrieve_executions_on_load(tx, load, delta_load):
    return tx.run("match (e:Execution) -[:HasNode]-> (n:Node) \
                    where $load_min < e.load < $load_max \
                    return id(e) as id, collect({name:n.name, cpu:n.cpu, memory:n.memory}) as nodes",
                  load_min=load-delta_load, load_max=load+delta_load)


def retrieve_cheapest_executions(load, delta_load, price_per_cpu, price_per_gb):
    executions = execute_query_function(retrieve_executions_on_load, load, delta_load)
    cheapest_cost = math.inf
    cheapest_executions = []
    for execution in executions.records():
        total_cost = 0
        for node in execution["nodes"]:
            total_cost += node["cpu"]*price_per_cpu + node["memory"]*price_per_gb

        if total_cost == cheapest_cost:
            cheapest_executions.append(execution["id"])
        elif total_cost < cheapest_cost:
            cheapest_cost = total_cost
            cheapest_executions = [execution["id"]]
    return cheapest_executions


def main():
    print(retrieve_cheapest_executions(10000, 1000, 2, 0.1))
    disconnect_neo4j()


if __name__ == '__main__':
    main()
