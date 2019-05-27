from kubernetes import client, config

from KubernetesAPIConnector import get_k8s_api
from initializer.neo4j_queries import execute_query_function


def connect_pods_to_containers_command(tx, pods):
    # TODO: Update, as pods structure has changed
    return tx.run("UNWIND $pods as pod \
                    MERGE (p:Pod{generate_name:pod.pod_generate_name}) \
                    WITH p, pod.containers as containers \
                    UNWIND containers as container \
                    MERGE (c:Container{name:container}) \
                    MERGE (p)-[:Contains]->(c)"
                  , pods=pods)


def extract_pod_info(pod_info):
    #print(pod_info)
    containers = []
    total_requested = 0.0
    for container_info in pod_info.spec.containers:
        containers.append(container_info.name)
        if container_info.resources.requests is None:
            #todo: find a good number to use as a placeholder when no request is set
            total_requested += 0
        else:
            total_requested += float(container_info.resources.requests["cpu"].split("m")[0])/1000
    name = pod_info.metadata.name
    pod = {"node_name": pod_info.spec.node_name,
           "pod_generate_name": pod_info.metadata.generate_name,
           "namespace": pod_info.metadata.namespace,
           "total_requested": total_requested,
           "containers": containers}
    if "name" in pod_info.metadata.labels:
        pod["deployment_name"] = pod_info.metadata.labels["name"]
    return name, pod


def extract_pods(pods_info):
    pods = {}
    for pod_info in pods_info.items:
        name, pod = extract_pod_info(pod_info)
        pods[name] = pod
    return pods


def extract_pods_namespace(name_space):
    pods_info = get_k8s_api().list_namespaced_pod(name_space)
    return extract_pods(pods_info)


def extract_pods_deployment(deployment):
    pods_deployment = {}
    for pod, info in extract_all_pods().items():
        if "deployment_name" in info:
            if info["deployment_name"] == deployment:
                pods_deployment[pod] = info
    return pods_deployment


def extract_all_pods():
    pods_info = get_k8s_api().list_pod_for_all_namespaces()
    return extract_pods(pods_info)


def extract_pods_on_node(node_name):
    pods = extract_all_pods()
    pods_on_node = {}
    for name, info in pods.items():
        if info["node_name"] == node_name:
            pods_on_node[name] = info
    return pods_on_node


def connect_pods_to_containers(settings):
    pods = extract_pods_namespace(settings["kubernetes_project_namespace"])
    execute_query_function(connect_pods_to_containers_command, pods)


if __name__ == '__main__':
    print(extract_pods_deployment("php-apache", "demo"))
