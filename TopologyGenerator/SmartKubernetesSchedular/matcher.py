import copy
import datetime
import math


def pod_score(pod_a_name, pod_a, node_b, copy_node_a, copy_node_b, stateful_set_score, deployment_score):
        for pod_b_name, pod_b in node_b["pods"].items():
            if pod_a["pod_generate_name"] == pod_b["pod_generate_name"]:
                if pod_b_name in copy_node_b["pods"]:
                    del copy_node_b["pods"][pod_b_name]
                    del copy_node_a["pods"][pod_a_name]
                    if pod_a["kind"] == "StatefulSet":
                        return stateful_set_score
                    elif pod_a["kind"] == "ReplicaSet":
                        return deployment_score
                    return 0
        return 0


def remaining_pods_score(copy_node, stateful_set_score, deployment_score):
    score = 0
    for pod_info in copy_node["pods"].values():
        if pod_info["kind"] == "StatefulSet":
            score += stateful_set_score
        elif pod_info["kind"] == "ReplicaSet":
            score += deployment_score
    return score


def calc_score_per_node(node_a, node_b):
    copy_node_a = copy.deepcopy(node_a)
    copy_node_b = copy.deepcopy(node_b)
    stateful_set_score = 100
    deployment_score = 1
    score = 0
    for pod_a_name, pod_a_info in node_a["pods"].items():
        score += pod_score(pod_a_name, pod_a_info, node_b, copy_node_a, copy_node_b, stateful_set_score, deployment_score)

    score -= remaining_pods_score(copy_node_a, stateful_set_score, deployment_score)
    score -= remaining_pods_score(copy_node_b, stateful_set_score, deployment_score)
    return score


def get_scores(current_state, desired_state):
    scores = {}
    for node_desired_name, node_desired_info in desired_state.items():
        score = {}
        for node_current_name, node_current_info in current_state.items():
            cur_score = calc_score_per_node(node_current_info, node_desired_info)
            score[node_current_name] = cur_score
        scores[node_desired_name] = score
    return scores


def rec_find_highest_score(desired_state_list, scores):
    if not desired_state_list:
        return 0, {}
    copy_desired_state_list = list(desired_state_list)
    node_name = copy_desired_state_list.pop()
    max_score = -math.inf
    max_mapping = None
    for node_b, score in scores[node_name].items():
        copy_scores = copy.deepcopy(scores)
        for remove_node_match in copy_scores.values():
            del remove_node_match[node_b]
        prev_score, prev_mapping = rec_find_highest_score(copy_desired_state_list, copy_scores)
        cur_score = prev_score + score
        prev_mapping[node_name] = node_b
        cur_mapping = prev_mapping
        if cur_score > max_score:
            max_score = cur_score
            max_mapping = cur_mapping
    return max_score, max_mapping


def find_highest_score_mapping(scores):
    score, mapping = rec_find_highest_score(list(scores.keys()), scores)
    return mapping


def match_nodes_desired_with_current_state(current_state, desired_state):
    scores = get_scores(current_state, desired_state)
    return find_highest_score_mapping(scores)


def already_on_node(des_pod_info, current_state_pods, remove_list):
    for cur_pod_name, cur_pod_info in current_state_pods.items():
        if des_pod_info["pod_generate_name"] == cur_pod_info["pod_generate_name"]:
            if cur_pod_name in remove_list:
                remove_list.remove(cur_pod_name)
                return True
    return False


def stateful_set_movement(add_list, remove_list, current_state_node):
    for name in add_list:
        for pod_info in current_state_node["pods"].values():
            if pod_info["pod_generate_name"] == name:
                if pod_info["kind"] == "StatefulSet":
                    return True
    for name in remove_list:
        if current_state_node["pods"][name]["kind"] == "StatefulSet":
            return True
    return False


def find_transitions_execution_change(current_state, desired_state):
    transitions = {}
    node_mapping = match_nodes_desired_with_current_state(current_state, desired_state)

    for des_node_name, des_node_info in desired_state.items():
        mapped_node_name = node_mapping[des_node_name]
        add_list = []
        remove_list = list(current_state[mapped_node_name]["pods"].keys())
        for des_pod_info in des_node_info["pods"].values():
            if not already_on_node(des_pod_info, current_state[mapped_node_name]["pods"], remove_list):
                add_list.append(des_pod_info["pod_generate_name"])

        if stateful_set_movement(add_list, current_state[mapped_node_name]) or stateful_set_movement(remove_list, current_state[mapped_node_name]):
            return False, None


        transitions[mapped_node_name] = {
            "add": add_list,
            "remove": remove_list
        }
    return True, transitions


def main():
    current_state = {'gke-demo-cluster-1-default-pool-6f471531-b933': {'cpu': 2.0, 'memory': 7.303501129150391, 'pods': {'fluentd-gcp-v3.2.0-8qdm6': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-b933', 'namespace': 'kube-system', 'total_requested': 0.1, 'containers': ['fluentd-gcp', 'prometheus-to-sd-exporter'], 'pod_generate_name': 'fluentd-gcp-v3.2.0-', 'kind': 'DaemonSet', 'deployment_name': None}, 'heapster-v1.6.0-beta.1-66f866bd4f-dz28z': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-b933', 'namespace': 'kube-system', 'total_requested': 0.063, 'containers': ['heapster', 'prom-to-sd', 'heapster-nanny'], 'pod_generate_name': 'heapster-v1.6.0-beta.1-66f866bd4f-', 'kind': 'ReplicaSet', 'deployment_name': None}, 'kube-dns-autoscaler-76fcd5f658-9f9mq': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-b933', 'namespace': 'kube-system', 'total_requested': 0.02, 'containers': ['autoscaler'], 'pod_generate_name': 'kube-dns-autoscaler-76fcd5f658-', 'kind': 'ReplicaSet', 'deployment_name': None}, 'kube-dns-b46cc9485-4lv6h': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-b933', 'namespace': 'kube-system', 'total_requested': 0.26, 'containers': ['kubedns', 'dnsmasq', 'sidecar', 'prometheus-to-sd'], 'pod_generate_name': 'kube-dns-b46cc9485-', 'kind': 'ReplicaSet', 'deployment_name': None}, 'kube-proxy-gke-demo-cluster-1-default-pool-6f471531-b933': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-b933', 'namespace': 'kube-system', 'total_requested': 0.1, 'containers': ['kube-proxy'], 'pod_generate_name': 'kube-proxy-gke-demo-cluster-1-default-pool-6f471531-', 'kind': 'DaemonSet', 'deployment_name': None}, 'metrics-server-v0.3.1-5b4d6d8d98-fx78m': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-b933', 'namespace': 'kube-system', 'total_requested': 0.047999999999999994, 'containers': ['metrics-server', 'metrics-server-nanny'], 'pod_generate_name': 'metrics-server-v0.3.1-5b4d6d8d98-', 'kind': 'ReplicaSet', 'deployment_name': None}, 'prometheus-to-sd-z6x4m': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-b933', 'namespace': 'kube-system', 'total_requested': 0.001, 'containers': ['prometheus-to-sd'], 'pod_generate_name': 'prometheus-to-sd-', 'kind': 'DaemonSet', 'deployment_name': None}, 'prometheus-1-alertmanager-1': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-b933', 'namespace': 'monitoring', 'total_requested': 0.01, 'containers': ['prometheus-alertmanager'], 'pod_generate_name': 'prometheus-1-alertmanager-', 'kind': 'StatefulSet', 'deployment_name': None}, 'prometheus-1-node-exporter-fmq4v': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-b933', 'namespace': 'monitoring', 'total_requested': 0.01, 'containers': ['prometheus-node-exporter'], 'pod_generate_name': 'prometheus-1-node-exporter-', 'kind': 'DaemonSet', 'deployment_name': None}, 'prometheus-1-prometheus-0': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-b933', 'namespace': 'monitoring', 'total_requested': 0.2, 'containers': ['prometheus-server'], 'pod_generate_name': 'prometheus-1-prometheus-', 'kind': 'StatefulSet', 'deployment_name': None}}}, 'gke-demo-cluster-1-default-pool-6f471531-k0kc': {'cpu': 2.0, 'memory': 7.303501129150391, 'pods': {'application-controller-manager-0': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'namespace': 'application-system', 'total_requested': 0.1, 'containers': ['manager'], 'pod_generate_name': 'application-controller-manager-', 'kind': 'StatefulSet', 'deployment_name': None}, 'php-apache-5f657688bc-fnjlp': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'namespace': 'demo', 'total_requested': 0.2, 'containers': ['php-apache'], 'pod_generate_name': 'php-apache-5f657688bc-', 'kind': 'ReplicaSet', 'deployment_name': 'php-apache'}, 'event-exporter-v0.2.4-5f7d5d7dd4-qhqmw': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'namespace': 'kube-system', 'total_requested': 0.0, 'containers': ['event-exporter', 'prometheus-to-sd-exporter'], 'pod_generate_name': 'event-exporter-v0.2.4-5f7d5d7dd4-', 'kind': 'ReplicaSet', 'deployment_name': None}, 'fluentd-gcp-scaler-7b895cbc89-5pc89': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'namespace': 'kube-system', 'total_requested': 0.0, 'containers': ['fluentd-gcp-scaler'], 'pod_generate_name': 'fluentd-gcp-scaler-7b895cbc89-', 'kind': 'ReplicaSet', 'deployment_name': None}, 'fluentd-gcp-v3.2.0-sx5vm': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'namespace': 'kube-system', 'total_requested': 0.1, 'containers': ['fluentd-gcp', 'prometheus-to-sd-exporter'], 'pod_generate_name': 'fluentd-gcp-v3.2.0-', 'kind': 'DaemonSet', 'deployment_name': None}, 'kube-dns-b46cc9485-q6m76': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'namespace': 'kube-system', 'total_requested': 0.26, 'containers': ['kubedns', 'dnsmasq', 'sidecar', 'prometheus-to-sd'], 'pod_generate_name': 'kube-dns-b46cc9485-', 'kind': 'ReplicaSet', 'deployment_name': None}, 'kube-proxy-gke-demo-cluster-1-default-pool-6f471531-k0kc': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'namespace': 'kube-system', 'total_requested': 0.1, 'containers': ['kube-proxy'], 'pod_generate_name': 'kube-proxy-gke-demo-cluster-1-default-pool-6f471531-', 'kind': 'DaemonSet', 'deployment_name': None}, 'l7-default-backend-6f8697844f-8vgxb': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'namespace': 'kube-system', 'total_requested': 0.01, 'containers': ['default-http-backend'], 'pod_generate_name': 'l7-default-backend-6f8697844f-', 'kind': 'ReplicaSet', 'deployment_name': None}, 'prometheus-to-sd-lpmzg': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'namespace': 'kube-system', 'total_requested': 0.001, 'containers': ['prometheus-to-sd'], 'pod_generate_name': 'prometheus-to-sd-', 'kind': 'DaemonSet', 'deployment_name': None}, 'prometheus-1-alertmanager-0': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'namespace': 'monitoring', 'total_requested': 0.01, 'containers': ['prometheus-alertmanager'], 'pod_generate_name': 'prometheus-1-alertmanager-', 'kind': 'StatefulSet', 'deployment_name': None}, 'prometheus-1-grafana-0': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'namespace': 'monitoring', 'total_requested': 0.05, 'containers': ['grafana'], 'pod_generate_name': 'prometheus-1-grafana-', 'kind': 'StatefulSet', 'deployment_name': None}, 'prometheus-1-kube-state-metrics-66cfd5684-555zl': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'namespace': 'monitoring', 'total_requested': 0.1, 'containers': ['kube-state-metrics', 'addon-resizer'], 'pod_generate_name': 'prometheus-1-kube-state-metrics-66cfd5684-', 'kind': 'ReplicaSet', 'deployment_name': None}, 'prometheus-1-node-exporter-8df9p': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'namespace': 'monitoring', 'total_requested': 0.01, 'containers': ['prometheus-node-exporter'], 'pod_generate_name': 'prometheus-1-node-exporter-', 'kind': 'DaemonSet', 'deployment_name': None}, 'prometheus-1-prometheus-1': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'namespace': 'monitoring', 'total_requested': 0.2, 'containers': ['prometheus-server'], 'pod_generate_name': 'prometheus-1-prometheus-', 'kind': 'StatefulSet', 'deployment_name': None}}}, 'gke-demo-cluster-1-default-pool-6f471531-ltck': {'cpu': 2.0, 'memory': 7.303501129150391, 'pods': {'fluentd-gcp-v3.2.0-2dd56': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-ltck', 'namespace': 'kube-system', 'total_requested': 0.1, 'containers': ['fluentd-gcp', 'prometheus-to-sd-exporter'], 'pod_generate_name': 'fluentd-gcp-v3.2.0-', 'kind': 'DaemonSet', 'deployment_name': None}, 'kube-proxy-gke-demo-cluster-1-default-pool-6f471531-ltck': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-ltck', 'namespace': 'kube-system', 'total_requested': 0.1, 'containers': ['kube-proxy'], 'pod_generate_name': 'kube-proxy-gke-demo-cluster-1-default-pool-6f471531-', 'kind': 'DaemonSet', 'deployment_name': None}, 'prometheus-to-sd-b2sjv': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-ltck', 'namespace': 'kube-system', 'total_requested': 0.001, 'containers': ['prometheus-to-sd'], 'pod_generate_name': 'prometheus-to-sd-', 'kind': 'DaemonSet', 'deployment_name': None}, 'prometheus-1-node-exporter-cxcrp': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-ltck', 'namespace': 'monitoring', 'total_requested': 0.01, 'containers': ['prometheus-node-exporter'], 'pod_generate_name': 'prometheus-1-node-exporter-', 'kind': 'DaemonSet', 'deployment_name': None}}}, 'gke-demo-cluster-1-default-pool-6f471531-m4rj': {'cpu': 2.0, 'memory': 7.303501129150391, 'pods': {'fluentd-gcp-v3.2.0-vbhbk': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-m4rj', 'namespace': 'kube-system', 'total_requested': 0.1, 'containers': ['fluentd-gcp', 'prometheus-to-sd-exporter'], 'pod_generate_name': 'fluentd-gcp-v3.2.0-', 'kind': 'DaemonSet', 'deployment_name': None}, 'kube-proxy-gke-demo-cluster-1-default-pool-6f471531-m4rj': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-m4rj', 'namespace': 'kube-system', 'total_requested': 0.1, 'containers': ['kube-proxy'], 'pod_generate_name': 'kube-proxy-gke-demo-cluster-1-default-pool-6f471531-', 'kind': 'DaemonSet', 'deployment_name': None}, 'prometheus-to-sd-njgpd': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-m4rj', 'namespace': 'kube-system', 'total_requested': 0.001, 'containers': ['prometheus-to-sd'], 'pod_generate_name': 'prometheus-to-sd-', 'kind': 'DaemonSet', 'deployment_name': None}, 'prometheus-1-node-exporter-jsbdb': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-m4rj', 'namespace': 'monitoring', 'total_requested': 0.01, 'containers': ['prometheus-node-exporter'], 'pod_generate_name': 'prometheus-1-node-exporter-', 'kind': 'DaemonSet', 'deployment_name': None}}}}
    old_best_execution = {'start_time': datetime.datetime(2019, 6, 18, 10, 20, 18, 426000), 'end_time': datetime.datetime(2019, 6, 18, 10, 22, 48, 426000), 'nodes': {'gke-demo-cluster-1-default-pool-6f471531-m4rj': {'cpu': 2.0, 'memory': 7.303501129150391, 'pods': {'prometheus-to-sd-njgpd': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-m4rj', 'pod_generate_name': 'prometheus-to-sd-', 'kind': 'DaemonSet'}, 'kube-proxy-gke-demo-cluster-1-default-pool-6f471531-m4rj': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-m4rj', 'pod_generate_name': 'kube-proxy-gke-demo-cluster-1-default-pool-6f471531-', 'kind': 'DaemonSet'}, 'fluentd-gcp-v3.2.0-vbhbk': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-m4rj', 'pod_generate_name': 'fluentd-gcp-v3.2.0-', 'kind': 'DaemonSet'}, 'prometheus-1-node-exporter-jsbdb': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-m4rj', 'pod_generate_name': 'prometheus-1-node-exporter-', 'kind': 'DaemonSet'}}}, 'gke-demo-cluster-1-default-pool-6f471531-b933': {'cpu': 2.0, 'memory': 7.303501129150391, 'pods': {'kube-dns-b46cc9485-4lv6h': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-b933', 'pod_generate_name': 'kube-dns-b46cc9485-', 'kind': 'ReplicaSet'}, 'heapster-v1.6.0-beta.1-66f866bd4f-dz28z': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-b933', 'pod_generate_name': 'heapster-v1.6.0-beta.1-66f866bd4f-', 'kind': 'ReplicaSet'}, 'prometheus-to-sd-z6x4m': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-b933', 'pod_generate_name': 'prometheus-to-sd-', 'kind': 'DaemonSet'}, 'kube-dns-autoscaler-76fcd5f658-9f9mq': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-b933', 'pod_generate_name': 'kube-dns-autoscaler-76fcd5f658-', 'kind': 'ReplicaSet'}, 'fluentd-gcp-v3.2.0-8qdm6': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-b933', 'pod_generate_name': 'fluentd-gcp-v3.2.0-', 'kind': 'DaemonSet'}, 'prometheus-1-prometheus-0': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-b933', 'pod_generate_name': 'prometheus-1-prometheus-', 'kind': 'StatefulSet'}, 'prometheus-1-node-exporter-fmq4v': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-b933', 'pod_generate_name': 'prometheus-1-node-exporter-', 'kind': 'DaemonSet'}, 'metrics-server-v0.3.1-5b4d6d8d98-fx78m': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-b933', 'pod_generate_name': 'metrics-server-v0.3.1-5b4d6d8d98-', 'kind': 'ReplicaSet'}, 'prometheus-1-alertmanager-1': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-b933', 'pod_generate_name': 'prometheus-1-alertmanager-', 'kind': 'StatefulSet'}, 'kube-proxy-gke-demo-cluster-1-default-pool-6f471531-b933': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-b933', 'pod_generate_name': 'kube-proxy-gke-demo-cluster-1-default-pool-6f471531-', 'kind': 'DaemonSet'}}}, 'gke-demo-cluster-1-default-pool-6f471531-k0kc': {'cpu': 2.0, 'memory': 7.303501129150391, 'pods': {'kube-dns-b46cc9485-q6m76': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'pod_generate_name': 'kube-dns-b46cc9485-', 'kind': 'ReplicaSet'}, 'kube-proxy-gke-demo-cluster-1-default-pool-6f471531-k0kc': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'pod_generate_name': 'kube-proxy-gke-demo-cluster-1-default-pool-6f471531-', 'kind': 'DaemonSet'}, 'event-exporter-v0.2.4-5f7d5d7dd4-qhqmw': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'pod_generate_name': 'event-exporter-v0.2.4-5f7d5d7dd4-', 'kind': 'ReplicaSet'}, 'l7-default-backend-6f8697844f-8vgxb': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'pod_generate_name': 'l7-default-backend-6f8697844f-', 'kind': 'ReplicaSet'}, 'fluentd-gcp-v3.2.0-sx5vm': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'pod_generate_name': 'fluentd-gcp-v3.2.0-', 'kind': 'DaemonSet'}, 'php-apache-5f657688bc-fnjlp': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'pod_generate_name': 'php-apache-5f657688bc-', 'kind': 'ReplicaSet'}, 'prometheus-1-grafana-0': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'pod_generate_name': 'prometheus-1-grafana-', 'kind': 'StatefulSet'}, 'application-controller-manager-0': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'pod_generate_name': 'application-controller-manager-', 'kind': 'StatefulSet'}, 'prometheus-1-kube-state-metrics-66cfd5684-555zl': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'pod_generate_name': 'prometheus-1-kube-state-metrics-66cfd5684-', 'kind': 'ReplicaSet'}, 'fluentd-gcp-scaler-7b895cbc89-5pc89': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'pod_generate_name': 'fluentd-gcp-scaler-7b895cbc89-', 'kind': 'ReplicaSet'}, 'prometheus-1-node-exporter-8df9p': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'pod_generate_name': 'prometheus-1-node-exporter-', 'kind': 'DaemonSet'}, 'prometheus-1-alertmanager-0': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'pod_generate_name': 'prometheus-1-alertmanager-', 'kind': 'StatefulSet'}, 'prometheus-to-sd-lpmzg': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'pod_generate_name': 'prometheus-to-sd-', 'kind': 'DaemonSet'}, 'prometheus-1-prometheus-1': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'pod_generate_name': 'prometheus-1-prometheus-', 'kind': 'StatefulSet'}}}, 'gke-demo-cluster-1-default-pool-6f471531-ltck': {'cpu': 2.0, 'memory': 7.303501129150391, 'pods': {'fluentd-gcp-v3.2.0-2dd56': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-ltck', 'pod_generate_name': 'fluentd-gcp-v3.2.0-', 'kind': 'DaemonSet'}, 'prometheus-1-node-exporter-cxcrp': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-ltck', 'pod_generate_name': 'prometheus-1-node-exporter-', 'kind': 'DaemonSet'}, 'kube-proxy-gke-demo-cluster-1-default-pool-6f471531-ltck': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-ltck', 'pod_generate_name': 'kube-proxy-gke-demo-cluster-1-default-pool-6f471531-', 'kind': 'DaemonSet'}, 'prometheus-to-sd-b2sjv': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-ltck', 'pod_generate_name': 'prometheus-to-sd-', 'kind': 'DaemonSet'}}}}}

    print(find_transitions_execution_change(current_state, old_best_execution["nodes"]))


if __name__ == '__main__':
    main()
