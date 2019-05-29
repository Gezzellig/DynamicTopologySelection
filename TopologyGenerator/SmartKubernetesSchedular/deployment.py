import copy
import random
import re

from SmartKubernetesSchedular import enforcer
from kubernetes_tools import extract_nodes, extract_pods


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


def helper_recursive_construction_migration_order(migration, migrations, cur_deployment, pods, nodes):
    migrations.remove(migration)
    cur_deployment = simulate_migration(cur_deployment, migration)
    if not verify_deployment(cur_deployment, pods, nodes):
        return False, []
    return recursive_construction_migration_order(migrations, cur_deployment, pods, nodes)


def recursive_construction_migration_order(migrations, cur_deployment, pods, nodes):
    # Base case no more migrations to schedule
    if not migrations:
        return True, []

    for migration in migrations:
        success, result = helper_recursive_construction_migration_order(migration, list(migrations), copy.deepcopy(cur_deployment), pods, nodes)
        if success:
            return True, [migration] + result
    return False, []


def merge_found_migrations_sets(migration, migrations_sets):
    for other in migrations_sets:
        other.append(migration)
    migrations_sets.append([migration])
    return migrations_sets


def find_suitable_migrations_sets(selected_add, destination_node, transitions):
    migrations_sets = []
    for source_node, content in transitions.items():
        for pod_remove in content["remove"]:
            if re.match("{}*".format(selected_add), pod_remove):
                migration = {"pod_name": pod_remove, "source": source_node, "destination": destination_node}
                new_trans = copy.deepcopy(transitions)
                new_trans[source_node]["remove"].remove(pod_remove)
                migrations_sets += merge_found_migrations_sets(migration, recurse_find_all_migrations_sets(new_trans))
    return migrations_sets


def recurse_find_all_migrations_sets(transitions):
    iterator = iter(transitions.values())
    selected_add = None
    selected_node = None
    for node_name, content in transitions.items():
        if content["add"]:
            selected_add = content["add"].pop(0)
            selected_node = node_name
            break

    #Base case
    if selected_add is None:
        return []

    #migrate
    migrations_sets = find_suitable_migrations_sets(selected_add, selected_node, transitions)

    #don't migrate
    migrations_sets += recurse_find_all_migrations_sets(copy.deepcopy(transitions))
    return migrations_sets


def find_all_migrations_sets(transitions):
    migrations_sets = recurse_find_all_migrations_sets(copy.deepcopy(transitions))
    migrations_sets.append([])

    #Sort the result so that the longest migration is in frond, as we want to try this one the first
    migrations_sets.sort(key=len, reverse=True)
    return migrations_sets



def construct_deployment_sequence(goal_deployment):
    nodes = extract_nodes.extract_all_nodes_cpu()
    pods = extract_pods.extract_all_pods()
    init_deployment = extract_deployment(pods, nodes)
    print(init_deployment)

    migrations = find_migrations(init_deployment, goal_deployment)
    # Shuffle them to reduce the change of changing a lot on one node at a time
    random.shuffle(migrations)
    return recursive_construction_migration_order(migrations, init_deployment, pods, nodes)


def remove_non_migrated_remove_pods(transitions, migration_set, pods):
    local_transitions = copy.deepcopy(transitions)
    local_pods = copy.deepcopy(pods)
    for migration in migration_set:
        local_transitions[migration["source"]]["remove"].remove(migration["pod_name"])
    for node_transitions in local_transitions.values():
        for removes in node_transitions["remove"]:
            del local_pods[removes]
    return local_pods


def find_suitable_migrations(transitions, migrations_sets, pods, nodes):
    for migrations_set in migrations_sets:
        local_pods_removed = remove_non_migrated_remove_pods(transitions, migrations_set, pods)
        cur_deployment = extract_deployment(local_pods_removed, nodes)
        result, migration_order = recursive_construction_migration_order(migrations_set, cur_deployment, local_pods_removed, nodes)
        if result:
            return migration_order


def scale_actions(transitions, migration_order, pods):
    local_transitions = copy.deepcopy(transitions)
    downscalers = []
    upscalers = []
    for migration in migration_order:
        local_transitions[migration["source"]]["remove"].remove(migration["pod_name"])

        generate_name = pods[migration["pod_name"]]["pod_generate_name"]
        local_transitions[migration["destination"]]["add"].remove(generate_name)
    generate_names = extract_pods.pods_to_generate_names(pods)
    for node_name, node_transitions in local_transitions.items():
        for remove in node_transitions["remove"]:
            downscalers.append({
                "pod_name": remove,
                "pod_generate_name": pods[remove]["pod_generate_name"],
                "deployment_name": pods[remove]["deployment_name"],
                "namespace": pods[remove]["namespace"]
            })

        for add in node_transitions["add"]:
            upscalers.append({
                "node_name": node_name,
                "pod_generate_name": add,
                "deployment_name": generate_names[add]["deployment_name"],
                "namespace": generate_names[add]["namespace"]
            })
    return downscalers, upscalers


def state_transition_plan(transitions, pods, nodes):
    migrations_sets = find_all_migrations_sets(transitions)
    migration_order = find_suitable_migrations(transitions, migrations_sets, pods, nodes)
    downscalers, upscalers = scale_actions(transitions, migration_order, pods)
    return downscalers, migration_order, upscalers



def main():
    goal_deployment = {'gke-develop-cluster-larger-pool-9ecdadbf-fpf5': ['php-apache-85546b856f-svcbk', 'php-apache-85546b856f-h64mq', 'php-apache-85546b856f-x297d', 'php-apache-85546b856f-xbd9c', 'event-exporter-v0.2.3-85644fcdf-xgdbp', 'fluentd-gcp-scaler-8b674f786-ntgl4', 'fluentd-gcp-v3.2.0-mg5c5', 'kube-dns-76dbb796c5-gp2j5', 'kube-dns-76dbb796c5-pk2s6', 'kube-dns-autoscaler-67c97c87fb-cmgn6', 'kube-proxy-gke-develop-cluster-larger-pool-9ecdadbf-fpf5', 'l7-default-backend-7ff48cffd7-hh5ck', 'metrics-server-75b8d78f76-r75zd', 'metrics-server-v0.2.1-fd596d746-t25xv', 'prometheus-to-sd-vqqjv', 'prometheus-1-alertmanager-0', 'prometheus-1-grafana-0', 'prometheus-1-kube-state-metrics-7f785c4cb9-bbjtk', 'prometheus-1-node-exporter-htczm', 'prometheus-1-prometheus-1'],
                       'gke-develop-cluster-larger-pool-9ecdadbf-w7ln': ['fluentd-gcp-v3.2.0-5pwm2', 'heapster-v1.6.0-beta.1-797bcbf978-f8xlz', 'kube-proxy-gke-develop-cluster-larger-pool-9ecdadbf-w7ln', 'prometheus-to-sd-h2t4h', 'prometheus-1-alertmanager-1', 'prometheus-1-grafana-1', 'prometheus-1-node-exporter-gtfhp', 'prometheus-1-prometheus-0']}
    success, migrations = construct_deployment_sequence(goal_deployment)
    if success:
        initial_state = extract_pods.extract_all_pods()
        enforcer.enforce_migrations(migrations, initial_state)


if __name__ == '__main__':
    main()
