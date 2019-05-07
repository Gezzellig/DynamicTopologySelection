from kubernetes import client, config

from initializer.neo4j_queries import execute_query_function


def connect_pods_to_containers_command(tx, pods):
    return tx.run("UNWIND $pods as pod \
                    MERGE (p:Pod{generate_name:pod.pod_generate_name}) \
                    WITH p, pod.containers as containers \
                    UNWIND containers as container \
                    MERGE (c:Container{name:container}) \
                    MERGE (p)-[:Contains]->(c)"
                  , pods=pods)


def extract_pod_info(pod_info):
    #print(pod_info)
    pod = {"node_name": pod_info.spec.node_name,
           "pod_generate_name": pod_info.metadata.generate_name,
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
    print(pods)
    return pods


def connect_pods_to_containers(settings):
    pods = extract_pods(settings)
    execute_query_function(connect_pods_to_containers_command, pods)


