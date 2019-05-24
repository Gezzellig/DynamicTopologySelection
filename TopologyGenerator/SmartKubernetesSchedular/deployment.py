import copy
import random

from SmartKubernetesSchedular import extract_nodes, enforcer
from SmartKubernetesSchedular import extract_pods


def verify_deployment(deployment, pods, nodes):
    for node_name, pod_names in deployment.items():
        cpu_available = nodes[node_name]["cpu"]
        cpu_needed = 0.0
        for pod_name in pod_names:
            cpu_needed += pods[pod_name]["total_requested"]
        if cpu_needed > cpu_available:
            return False
    return True


def find_migrations(init_deployment, goal_deployment):
    migrations = []
    for node, pod_names in goal_deployment.items():
        for pod_name in pod_names:
            if pod_name not in init_deployment[node]:
                for source_node, pods in init_deployment.items():
                    if pod_name in pods:
                        migrations.append({"pod_name": pod_name, "source": source_node, "destination": node})
                        break
    return migrations


def extract_deployment(pods, nodes):
    deployment = {}
    for node_name in nodes:
        deployment[node_name] = []
    for pod_name, info in pods.items():
        node = info["node_name"]
        deployment[node].append(pod_name)
    return deployment


def simulate_migration(cur_deployment, migration):
    pod_name = migration["pod_name"]
    source = migration["source"]
    destination = migration["destination"]
    cur_deployment[source].remove(pod_name)
    cur_deployment[destination].append(pod_name)
    return cur_deployment


def helper_recursive_construction(migration, migrations, cur_deployment, pods, nodes):
    migrations.remove(migration)
    cur_deployment = simulate_migration(cur_deployment, migration)
    if not verify_deployment(cur_deployment, pods, nodes):
        return False, []
    return recursive_construction(migrations, cur_deployment, pods, nodes)


def recursive_construction(migrations, cur_deployment, pods, nodes):
    # Base case no more migrations to schedule
    print("migrations: {}".format(migrations))
    if not migrations:
        return True, []

    for migration in migrations:
        success, result = helper_recursive_construction(migration, list(migrations), copy.deepcopy(cur_deployment), pods, nodes)
        if success:
            return True, [migration] + result
    return False, []


def construct_deployment_sequence(goal_deployment):
    nodes = extract_nodes.extract_all_nodes()
    pods = extract_pods.extract_all_pods_dict()
    init_deployment = extract_deployment(pods, nodes)
    print(init_deployment)

    migrations = find_migrations(init_deployment, goal_deployment)
    # Shuffle them to reduce the change of changing a lot on one node at a time
    random.shuffle(migrations)
    return recursive_construction(migrations, init_deployment, pods, nodes)


def main():
    goal_deployment = {'gke-develop-cluster-larger-pool-9ecdadbf-fpf5': ['php-apache-85546b856f-svcbk', 'php-apache-85546b856f-h64mq', 'php-apache-85546b856f-x297d', 'php-apache-85546b856f-xbd9c', 'event-exporter-v0.2.3-85644fcdf-xgdbp', 'fluentd-gcp-scaler-8b674f786-ntgl4', 'fluentd-gcp-v3.2.0-mg5c5', 'kube-dns-76dbb796c5-gp2j5', 'kube-dns-76dbb796c5-pk2s6', 'kube-dns-autoscaler-67c97c87fb-cmgn6', 'kube-proxy-gke-develop-cluster-larger-pool-9ecdadbf-fpf5', 'l7-default-backend-7ff48cffd7-hh5ck', 'metrics-server-75b8d78f76-r75zd', 'metrics-server-v0.2.1-fd596d746-t25xv', 'prometheus-to-sd-vqqjv', 'prometheus-1-alertmanager-0', 'prometheus-1-grafana-0', 'prometheus-1-kube-state-metrics-7f785c4cb9-bbjtk', 'prometheus-1-node-exporter-htczm', 'prometheus-1-prometheus-1'],
                       'gke-develop-cluster-larger-pool-9ecdadbf-w7ln': ['fluentd-gcp-v3.2.0-5pwm2', 'heapster-v1.6.0-beta.1-797bcbf978-f8xlz', 'kube-proxy-gke-develop-cluster-larger-pool-9ecdadbf-w7ln', 'prometheus-to-sd-h2t4h', 'prometheus-1-alertmanager-1', 'prometheus-1-grafana-1', 'prometheus-1-node-exporter-gtfhp', 'prometheus-1-prometheus-0']}
    success, migrations = construct_deployment_sequence(goal_deployment)
    if success:
        initial_state = extract_pods.extract_all_pods()
        enforcer.enforce_migrations(migrations, initial_state)


if __name__ == '__main__':
    main()
