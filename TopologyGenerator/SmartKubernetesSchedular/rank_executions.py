import math

import requests

import load_settings
from SmartKubernetesSchedular.retrieve_executions import retrieve_executions


def retrieve_nodes_cpu_usage(execution, prometheus_address):
    time_window = execution["end_time"] - execution["start_time"]

    url = "http://{prom_address}/api/v1/query?query=sum(rate(node_cpu{{mode!=%22idle%22,mode!=%22iowait%22,mode!~%22^(?:guest.*)$%22}}[{time_window}s]))%20by%20(instance)&time={start_time}".format(prom_address=prometheus_address, time_window=time_window.seconds, start_time=execution["start_time"].timestamp())
    results = requests.get(url).json()

    cpu_usage_nodes = {}
    for result in results["data"]["result"]:
        node_name = result["metric"]["instance"]
        cpu_usage = float(result["value"][1])
        cpu_usage_nodes[node_name] = cpu_usage
    return cpu_usage_nodes


def rank_execution_node_cpu_usage(execution, prometheus_address):
    nodes_cpu_usage = retrieve_nodes_cpu_usage(execution, prometheus_address)
    rank = 0
    for max_cpu_usage in nodes_cpu_usage.values():
        rank += pow(1+max_cpu_usage, 2)
    return rank


def find_best_execution(executions, prometheus_address):
    best_rank = math.inf
    best_ranked_execution = None
    for execution in executions:
        rank = rank_execution_node_cpu_usage(execution, prometheus_address)
        if rank < best_rank:
            best_rank = rank
            best_ranked_execution = execution
    return best_ranked_execution



