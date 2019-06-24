import copy
import datetime
import json
import sys

from Neo4jGraphDriver import disconnect_neo4j
from SmartKubernetesSchedular.retrieve_executions import retrieve_single_execution
from initializer.neo4j_queries import execute_query_function
from kubernetes_tools import extract_pods, extract_nodes


def add_time_window_command(tx, load, pods, start_time, end_time):
    return tx.run("CREATE (e:Execution {load:$load, start_time:datetime({ epochMillis: $start_time }), end_time:datetime({ epochMillis: $end_time})}) \
                    with e \
                    UNWIND $pods as pod \
                    MERGE (e)-[:HasNode]->(n:Node {name:pod.node_name, cpu:pod.node_cpu, memory:pod.node_memory}) \
                    WITH e, n, pod.pod_generate_name as pod_generate_name, pod.pod_name as pod_name, pod.kind as kind, pod.deployment_name as deployment_name\
                    MERGE (p:Pod{generate_name:pod_generate_name, kind:kind, deployment_name:deployment_name}) \
                    WITH e, n, p, pod_name \
                    CREATE (n)-[:Ran{name:pod_name}]->(p) \
                    RETURN DISTINCT id(e) AS execution_id",
                  load=load, pods=pods, start_time=int(start_time.timestamp()*1000), end_time=int(end_time.timestamp()*1000))


def create_time_window(end_time, load, time_window, pods, nodes):
    pods_local = copy.deepcopy(pods)
    # add node information to each pod so it can be added to neo4j
    print("EXECUTION ADDED: {}".format(load))
    for pod in pods_local:
        pod["node_cpu"] = nodes[pod["node_name"]]["cpu"]
        pod["node_memory"] = nodes[pod["node_name"]]["memory"]
        if pod["deployment_name"] is None:
            pod["deployment_name"] = "None"
    result = execute_query_function(add_time_window_command, load, pods_local, end_time-time_window, end_time)
    cur_execution_id = result.single()["execution_id"]
    return retrieve_single_execution(cur_execution_id)


def main():
    print("starting add_time_window")
    settings_file_name = sys.argv[1]
    print("Settings: {}".format(settings_file_name))
    with open(settings_file_name) as file:
        settings = json.load(file)

    pods = extract_pods.pods_dict_to_list(extract_pods.extract_all_pods())
    nodes = extract_nodes.extract_all_nodes_cpu()
    print(create_time_window(datetime.datetime.now(), 10000, datetime.timedelta(minutes=5), pods, nodes))


if __name__ == '__main__':
    main()
    disconnect_neo4j()
