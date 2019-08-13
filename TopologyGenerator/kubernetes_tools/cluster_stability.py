import datetime
import sys

import requests

from load_settings import load_settings
from prometheus_requestor import prometheus_request


def cpu_scaled(start_time, end_time, settings):
    num_cpu_query = 'http://{prom}/api/v1/query?query=count(node_cpu{{mode="user"}})&time={time}'
    result = prometheus_request(num_cpu_query.format(prom=settings["prometheus_address"], time=start_time.timestamp())).json()
    start_num_cpu = int(result["data"]["result"][0]["value"][1])
    result = prometheus_request(num_cpu_query.format(prom=settings["prometheus_address"], time=end_time.timestamp())).json()
    end_num_cpu = int(result["data"]["result"][0]["value"][1])
    return not end_num_cpu - start_num_cpu == 0


def convert_result_to_key_value(pods):
    key_value_pod = {}
    for pod in pods:
        key_value_pod[pod["metric"]["container_name"]] = pod["value"][1]
    return key_value_pod


def pod_scaled(start_time, end_time, settings):
    num_pod_query = 'http://{prom}/api/v1/query?query=count(container_cpu_usage_seconds_total{{container_name!="POD",container_name!="",pod_name!=""}}) by (container_name)&time={time}'
    result = prometheus_request(num_pod_query.format(prom=settings["prometheus_address"], time=start_time.timestamp())).json()
    start_num_pod = convert_result_to_key_value(result["data"]["result"])
    result = prometheus_request(num_pod_query.format(prom=settings["prometheus_address"], time=end_time.timestamp())).json()
    end_num_pod = convert_result_to_key_value(result["data"]["result"])

    # If the size is different then for sure some pods have changed.
    if not len(start_num_pod) == len(end_num_pod):
        return True

    # If the size is the same, then we only have to check from one side
    for name, number in end_num_pod.items():
        #Check if the pod name is present at the starttime.
        if name not in start_num_pod:
            return True
        #Check if both have the same number of that container
        if not number == start_num_pod[name]:
            return True
    return False


def cluster_stable(end_time, time_window, settings):
    start_time = end_time-time_window
    #TODO maybe impelment it so that it checks the whole time instead of only begin and end time.
    if cpu_scaled(start_time, end_time, settings):
        return False
    if pod_scaled(start_time, end_time, settings):
        return False
    return True


