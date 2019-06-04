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


def pods_dict_to_list(pod_dict):
    pod_list = []
    for name, info in pod_dict.items():
        info["pod_name"] = name
        pod_list.append(info)
    return pod_list


def pods_to_generate_names(pods):
    generate_names = {}
    for pod_info in pods.values():
        if not pod_info["pod_generate_name"] in generate_names:
            generate_names[pod_info["pod_generate_name"]] = {
                "deployment_name": pod_info["deployment_name"],
                "namespace": pod_info["namespace"]
            }
    return generate_names


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
           "namespace": pod_info.metadata.namespace,
           "total_requested": total_requested,
           "containers": containers}
    if pod_info.metadata.generate_name:
        pod["pod_generate_name"] = pod_info.metadata.generate_name
    else:
        pod["pod_generate_name"] = pod_info.metadata.name.rsplit("-", 1)[0]+"-"
    if pod_info.metadata.owner_references:
        pod["kind"] = pod_info.metadata.owner_references[0].kind
    else:
        # Todo maybe change again, putting it to deamonset so it is not taken into account
        #pod["kind"] = None
        pod["kind"] = "DaemonSet"
    if "name" in pod_info.metadata.labels:
        pod["deployment_name"] = pod_info.metadata.labels["name"]
    else:
        pod["deployment_name"] = None
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
