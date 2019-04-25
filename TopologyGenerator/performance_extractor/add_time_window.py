import datetime
import json
import sys

from kubernetes import client, config

from initializer.neo4j_queries import create_execution_node


def extract_pod_info(pod_info):
    #print(pod_info)
    pod = {"node_name": pod_info.spec.node_name,
           "pod_name": pod_info.metadata.name,
           "containers": []}
    for container_info in pod_info.spec.containers:
        pod["containers"].append(container_info.name)
    return pod


def extract_pods(settings):
    config.load_kube_config()
    k8s_api = client.CoreV1Api()
    name_space = settings["kubernetes_project_namespace"]

    pods_info = k8s_api.list_namespaced_pod(name_space)
    pods = []
    for pod_info in pods_info.items:
        pods.append(extract_pod_info(pod_info))
    return pods


def retrieve_times(window_size):
    #TODO: add proper implementation
    end_time = datetime.datetime.now()
    start_time = end_time - window_size
    return start_time, end_time


def create_time_window(settings, window_size):
    start_time, end_time = retrieve_times(window_size)
    pods = extract_pods(settings)

    #TODO: make a load analyser
    load = 4
    create_execution_node(load, start_time, end_time, pods)



def main():
    print("starting add_time_window")
    settings_file_name = sys.argv[1]
    print("Settings: {}".format(settings_file_name))
    with open(settings_file_name) as file:
        settings = json.load(file)
    create_time_window(settings, datetime.timedelta(minutes=5))


if __name__ == '__main__':
    main()
