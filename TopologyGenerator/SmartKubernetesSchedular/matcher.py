import copy
import datetime

from kubernetes_tools import extract_pods


class StatefulSetMappingException(Exception):
    pass


class NodeAssignedButDoesNotContainStatefulSetException(Exception):
    pass


def select_all_current_stateful_set_pods(current_state_pods):
    stateful_set_pods = []
    for pod_name, pod_info in current_state_pods.items():
        if pod_info["kind"] == "StatefulSet":
            stateful_set_pods.append(pod_name)
    return stateful_set_pods


"""
def stateful_set_node_already_assigned(desired_state_copy, mapping, pod_info):
    # check if the node is not already assigned
    generate_name = pod_info["pod_generate_name"]
    for desired_node_name, current_node_name in mapping.items():
        if pod_info["node_name"] == current_node_name:
            for pod_name, pod_info in desired_state_copy["nodes"][desired_node_name]["pods"].items():
                if pod_info["pod_generate_name"] == generate_name:
                    del desired_state_copy["nodes"][desired_node_name]["pods"][pod_name]
                    return True
            raise NodeAssignedButDoesNotContainStatefulSetException()
    return False
"""


def find_original_node(stateful_set_pod_name, desired_state_copy, current_state_pods, mapping):
    for node_name, node_info in desired_state_copy["nodes"].items():
        if stateful_set_pod_name in node_info["pods"]:
            if node_name not in mapping:
                mapping[node_name] = current_state_pods[stateful_set_pod_name]["node_name"]
            elif not mapping[node_name] == current_state_pods[stateful_set_pod_name]["node_name"]:
                raise StatefulSetMappingException("One stateful sets changed location, WRONGLY")
            return
    raise StatefulSetMappingException("No match found for statefulset: {}".format(stateful_set_pod_name))


def match_stateful_sets(desired_state, current_state_pods):
    #desired_state_copy = copy.deepcopy(desired_state)
    mapping = {} #  containing a mapping from desired to current state
    stateful_set_pods = select_all_current_stateful_set_pods(current_state_pods)

    print(stateful_set_pods)
    # Check if old stateful sets are still named the same, if so use those since they are for sure the same.
    for stateful_set_pod_name in stateful_set_pods:
        find_original_node(stateful_set_pod_name, desired_state, current_state_pods, mapping)
    return mapping


def get_unmatched_nodes(matched, desired_state):
    pass


def match_desired_with_current_state(desired_state):
    current_state_pods = extract_pods.extract_all_pods()
    print(current_state_pods)
    print(match_stateful_sets(desired_state, current_state_pods))


def main():
    desired_state = {'start_time': datetime.datetime(2019, 6, 7, 9, 58, 27, 794000), 'end_time': datetime.datetime(2019, 6, 7, 10, 3, 27, 794000), 'nodes': {'gke-develop-cluster-larger-pool-9ecdadbf-dt2l': {'cpu': 2.0, 'pods': {'prometheus-1-node-exporter-zk9rh': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-dt2l', 'pod_generate_name': 'prometheus-1-node-exporter-', 'kind': 'DaemonSet'}, 'gitlab-unicorn-d4c595cc6-46hdd': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-dt2l', 'pod_generate_name': 'gitlab-unicorn-d4c595cc6-', 'kind': 'ReplicaSet'}, 'php-apache-85546b856f-58vkn': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-dt2l', 'pod_generate_name': 'php-apache-85546b856f-', 'kind': 'ReplicaSet'}, 'prometheus-1-prometheus-0': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-dt2l', 'pod_generate_name': 'prometheus-1-prometheus-', 'kind': 'StatefulSet'}, 'kube-proxy-gke-develop-cluster-larger-pool-9ecdadbf-dt2l': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-dt2l', 'pod_generate_name': 'kube-proxy-gke-develop-cluster-larger-pool-9ecdadbf-', 'kind': 'DaemonSet'}, 'prometheus-to-sd-bf2d7': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-dt2l', 'pod_generate_name': 'prometheus-to-sd-', 'kind': 'DaemonSet'}, 'heapster-v1.6.0-beta.1-797bcbf978-kgtgb': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-dt2l', 'pod_generate_name': 'heapster-v1.6.0-beta.1-797bcbf978-', 'kind': 'ReplicaSet'}, 'fluentd-gcp-v3.2.0-k9ldq': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-dt2l', 'pod_generate_name': 'fluentd-gcp-v3.2.0-', 'kind': 'DaemonSet'}}}, 'gke-develop-cluster-larger-pool-9ecdadbf-nbth': {'cpu': 2.0, 'pods': {'metrics-server-v0.2.1-fd596d746-t6s75': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-nbth', 'pod_generate_name': 'metrics-server-v0.2.1-fd596d746-', 'kind': 'ReplicaSet'}, 'prometheus-1-grafana-0': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-nbth', 'pod_generate_name': 'prometheus-1-grafana-', 'kind': 'StatefulSet'}, 'gitlab-minio-7bdfff5f69-d8kzm': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-nbth', 'pod_generate_name': 'gitlab-minio-7bdfff5f69-', 'kind': 'ReplicaSet'}, 'fluentd-gcp-scaler-8b674f786-mrrj9': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-nbth', 'pod_generate_name': 'fluentd-gcp-scaler-8b674f786-', 'kind': 'ReplicaSet'}, 'gitlab-sidekiq-all-in-1-677dff5ccc-j84mb': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-nbth', 'pod_generate_name': 'gitlab-sidekiq-all-in-1-677dff5ccc-', 'kind': 'ReplicaSet'}, 'kube-dns-76dbb796c5-7jcsc': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-nbth', 'pod_generate_name': 'kube-dns-76dbb796c5-', 'kind': 'ReplicaSet'}, 'kube-proxy-gke-develop-cluster-larger-pool-9ecdadbf-nbth': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-nbth', 'pod_generate_name': 'kube-proxy-gke-develop-cluster-larger-pool-9ecdadbf-', 'kind': 'DaemonSet'}, 'prometheus-1-node-exporter-m2njg': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-nbth', 'pod_generate_name': 'prometheus-1-node-exporter-', 'kind': 'DaemonSet'}, 'gitlab-nginx-ingress-default-backend-6d86c499cb-xl85j': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-nbth', 'pod_generate_name': 'gitlab-nginx-ingress-default-backend-6d86c499cb-', 'kind': 'ReplicaSet'}, 'event-exporter-v0.2.3-85644fcdf-jkzj4': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-nbth', 'pod_generate_name': 'event-exporter-v0.2.3-85644fcdf-', 'kind': 'ReplicaSet'}, 'prometheus-1-kube-state-metrics-7f785c4cb9-kfq6j': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-nbth', 'pod_generate_name': 'prometheus-1-kube-state-metrics-7f785c4cb9-', 'kind': 'ReplicaSet'}, 'kube-dns-autoscaler-67c97c87fb-zt5k7': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-nbth', 'pod_generate_name': 'kube-dns-autoscaler-67c97c87fb-', 'kind': 'ReplicaSet'}, 'gitlab-gitlab-shell-64bb7896f5-nqwm7': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-nbth', 'pod_generate_name': 'gitlab-gitlab-shell-64bb7896f5-', 'kind': 'ReplicaSet'}, 'gitlab-gitaly-0': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-nbth', 'pod_generate_name': 'gitlab-gitaly-', 'kind': 'StatefulSet'}, 'l7-default-backend-7ff48cffd7-rvl8s': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-nbth', 'pod_generate_name': 'l7-default-backend-7ff48cffd7-', 'kind': 'ReplicaSet'}, 'prometheus-to-sd-jl9tr': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-nbth', 'pod_generate_name': 'prometheus-to-sd-', 'kind': 'DaemonSet'}, 'gitlab-redis-578654b55f-6zx78': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-nbth', 'pod_generate_name': 'gitlab-redis-578654b55f-', 'kind': 'ReplicaSet'}, 'gitlab-postgresql-c4f7884bc-zw8f5': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-nbth', 'pod_generate_name': 'gitlab-postgresql-c4f7884bc-', 'kind': 'ReplicaSet'}, 'fluentd-gcp-v3.2.0-kr6j8': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-nbth', 'pod_generate_name': 'fluentd-gcp-v3.2.0-', 'kind': 'DaemonSet'}, 'gitlab-task-runner-5b88b674db-r8jfn': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-nbth', 'pod_generate_name': 'gitlab-task-runner-5b88b674db-', 'kind': 'ReplicaSet'}, 'prometheus-1-alertmanager-0': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-nbth', 'pod_generate_name': 'prometheus-1-alertmanager-', 'kind': 'StatefulSet'}, 'metrics-server-75b8d78f76-q54t4': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-nbth', 'pod_generate_name': 'metrics-server-75b8d78f76-', 'kind': 'ReplicaSet'}, 'gitlab-nginx-ingress-controller-7f56dc849f-6sqwq': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-nbth', 'pod_generate_name': 'gitlab-nginx-ingress-controller-7f56dc849f-', 'kind': 'ReplicaSet'}, 'tiller-deploy-54fc6d9ccc-krbj5': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-nbth', 'pod_generate_name': 'tiller-deploy-54fc6d9ccc-', 'kind': 'ReplicaSet'}, 'application-controller-manager-0': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-nbth', 'pod_generate_name': 'application-controller-manager-', 'kind': 'StatefulSet'}, 'gitlab-registry-648777fb6b-j96zq': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-nbth', 'pod_generate_name': 'gitlab-registry-648777fb6b-', 'kind': 'ReplicaSet'}, 'kube-dns-76dbb796c5-tzljz': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-nbth', 'pod_generate_name': 'kube-dns-76dbb796c5-', 'kind': 'ReplicaSet'}}}, 'gke-develop-cluster-larger-pool-9ecdadbf-mhj9': {'cpu': 2.0, 'pods': {'php-apache-85546b856f-blm8s': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-mhj9', 'pod_generate_name': 'php-apache-85546b856f-', 'kind': 'ReplicaSet'}, 'php-apache-85546b856f-brhc7': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-mhj9', 'pod_generate_name': 'php-apache-85546b856f-', 'kind': 'ReplicaSet'}, 'fluentd-gcp-v3.2.0-hbpf6': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-mhj9', 'pod_generate_name': 'fluentd-gcp-v3.2.0-', 'kind': 'DaemonSet'}, 'prometheus-1-node-exporter-5gz6f': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-mhj9', 'pod_generate_name': 'prometheus-1-node-exporter-', 'kind': 'DaemonSet'}, 'prometheus-1-grafana-1': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-mhj9', 'pod_generate_name': 'prometheus-1-grafana-', 'kind': 'StatefulSet'}, 'php-apache-85546b856f-wjg2s': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-mhj9', 'pod_generate_name': 'php-apache-85546b856f-', 'kind': 'ReplicaSet'}, 'prometheus-1-prometheus-1': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-mhj9', 'pod_generate_name': 'prometheus-1-prometheus-', 'kind': 'StatefulSet'}, 'prometheus-to-sd-gfth5': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-mhj9', 'pod_generate_name': 'prometheus-to-sd-', 'kind': 'DaemonSet'}, 'prometheus-1-alertmanager-1': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-mhj9', 'pod_generate_name': 'prometheus-1-alertmanager-', 'kind': 'StatefulSet'}, 'kube-proxy-gke-develop-cluster-larger-pool-9ecdadbf-mhj9': {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-mhj9', 'pod_generate_name': 'kube-proxy-gke-develop-cluster-larger-pool-9ecdadbf-', 'kind': 'DaemonSet'}}}}}
    match_desired_with_current_state(desired_state)


if __name__ == '__main__':
    main()
