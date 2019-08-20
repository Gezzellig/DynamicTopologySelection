import copy
import random
import re

from SmartKubernetesSchedular import enforcer
from kubernetes_tools import extract_nodes, extract_pods


def merge_found_migrations_sets(migration, migrations_sets):
    """"
    Adds the given migration to all elements present in migration_sets.
    """
    for other in migrations_sets:
        other.append(migration)
    migrations_sets.append([migration])
    return migrations_sets


def find_suitable_migrations_sets(selected_add, destination_node, transitions):
    """
    For one add action finds all possible suitable remove actions to and lists them in the migration sets.
    """
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
    """
    Recursively generates all possible migration sets that can be retrieved from the transitions.
    """
    selected_add = None
    selected_node = None
    for node_name, content in transitions.items():
        if content["add"]:
            selected_add = content["add"].pop(0)
            selected_node = node_name
            break

    # Base case
    if selected_add is None:
        return []

    # migrate
    migrations_sets = find_suitable_migrations_sets(selected_add, selected_node, transitions)

    # don't migrate
    migrations_sets += recurse_find_all_migrations_sets(copy.deepcopy(transitions))
    return migrations_sets


def find_all_migrations_sets(transitions):
    """
    Starts the recursive function to retrieve all migration sets, and then orders them decreaslingy on length.
    """
    migrations_sets = recurse_find_all_migrations_sets(copy.deepcopy(transitions))
    migrations_sets.append([])

    # Sort the result so that the longest migration is in front, as we want to try this one the first
    migrations_sets.sort(key=len, reverse=True)
    return migrations_sets


def remove_non_migrated_remove_pods(transitions, migration_set, pods):
    local_transitions = copy.deepcopy(transitions)
    local_pods = copy.deepcopy(pods)
    for migration in migration_set:
        local_transitions[migration["source"]]["remove"].remove(migration["pod_name"])
    for node_transitions in local_transitions.values():
        for removes in node_transitions["remove"]:
            del local_pods[removes]
    return local_pods


def extract_deployment(pods, nodes):
    """
    Transforms the given pods and nodes into a dictionary where the pods running on a node are added in a list under the node names key.
    """
    deployment = {}
    for node_name in nodes:
        deployment[node_name] = []
    for pod_name, info in pods.items():
        node = info["node_name"]
        deployment[node].append(pod_name)
    return deployment


def simulate_migration(cur_deployment, migration):
    """
    Generates the resulting deployment after the given migration would be performed
    """
    pod_name = migration["pod_name"]
    source = migration["source"]
    destination = migration["destination"]
    cur_deployment[source].remove(pod_name)
    cur_deployment[destination].append(pod_name)
    return cur_deployment


def verify_deployment(deployment, pods, nodes):
    """
    Checks for every node if the amount of requested cpu does not excel the available cpu.
    """
    for node_name, pod_names in deployment.items():
        cpu_available = nodes[node_name]["cpu"]
        cpu_needed = 0.0
        for pod_name in pod_names:
            cpu_needed += pods[pod_name]["total_requested"]
        if cpu_needed > cpu_available:
            return False
    return True


def helper_recursive_construction_migration_order(migration, migrations, cur_deployment, pods, nodes):
    """
    Helps with finding of the given set of migrations can be performed and return its found order
    """
    migrations.remove(migration)
    cur_deployment = simulate_migration(cur_deployment, migration)
    if not verify_deployment(cur_deployment, pods, nodes):
        return False, []
    return recursive_construction_migration_order(migrations, cur_deployment, pods, nodes)


def recursive_construction_migration_order(migrations, cur_deployment, pods, nodes):
    """
    Recursively searches for a possible order of migrations to perform the provided migrations.
    When this is found it is returned.
    """
    # Base case no more migrations to schedule
    if not migrations:
        return True, []

    for migration in migrations:
        success, result = helper_recursive_construction_migration_order(migration, list(migrations), copy.deepcopy(cur_deployment), pods, nodes)
        if success:
            return True, [migration] + result
    return False, []


def find_suitable_migrations(transitions, migrations_sets, pods, nodes):
    """
    Finds the first and therefore largest migrations set that can be executed and returns its order.
    """
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
                "destination_node": node_name,
                "pod_generate_name": add,
                "deployment_name": generate_names[add]["deployment_name"],
                "namespace": generate_names[add]["namespace"]
            })
    return downscalers, upscalers


def get_node_removals(transitions):
    node_removals = []
    for node_name, transition_info in transitions.items():
        if "delete" in transition_info:
            if transition_info["delete"]:
                node_removals.append(node_name)
    return node_removals


def state_transition_plan(transitions, pods, nodes):
    migrations_sets = find_all_migrations_sets(transitions)
    migration_order = find_suitable_migrations(transitions, migrations_sets, pods, nodes)
    downscalers, upscalers = scale_actions(transitions, migration_order, pods)
    node_removals = get_node_removals(transitions)
    return downscalers, migration_order, upscalers, node_removals



