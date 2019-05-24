import copy
import random

from SmartKubernetesSchedular import extract_nodes
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
    return recursive_construction(random.shuffle(migrations), init_deployment, pods, nodes)


def main():
    construct_deployment_sequence({})


if __name__ == '__main__':
    main()
