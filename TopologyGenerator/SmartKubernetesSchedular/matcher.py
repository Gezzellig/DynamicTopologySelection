import copy
import math

from kubernetes_tools.extract_pods import movable, removable


def scoring(pod_info, not_movable_score, movable_score):
    """
    This function return the appropriate score for the given pod type.
    """
    if pod_info["kind"] == "DaemonSet":
        return 0
    if movable(pod_info):
        return movable_score
    else:
        return not_movable_score


def pod_score(pod_a_name, pod_a, node_b, copy_node_a, copy_node_b, not_movable_score, movable_score):
    """
    Tries to find a pod of the deployement of pod_a in the node_b.
    """
    for pod_b_name, pod_b in node_b["pods"].items():
        if pod_a["pod_generate_name"] == pod_b["pod_generate_name"]:
            if pod_b_name in copy_node_b["pods"]:
                del copy_node_b["pods"][pod_b_name]
                del copy_node_a["pods"][pod_a_name]
                return scoring(pod_a, not_movable_score, movable_score)
    return 0


def remaining_pods_score(copy_node, not_movable_score, movable_score):
    """
    Returns the score that will be subtracted as it are pods that are not matched.
    """
    score = 0
    for pod_info in copy_node["pods"].values():
        score += scoring(pod_info, not_movable_score, movable_score)
    return score


def calc_score_per_node(node_a, node_b, not_movable_score, movable_score):
    """
    Returns the score of matching the contents of two nodes.
    """
    copy_node_a = copy.deepcopy(node_a)
    copy_node_b = copy.deepcopy(node_b)
    score = 0
    for pod_a_name, pod_a_info in node_a["pods"].items():
        score += pod_score(pod_a_name, pod_a_info, node_b, copy_node_a, copy_node_b, not_movable_score, movable_score)

    score -= remaining_pods_score(copy_node_a, not_movable_score, movable_score)
    score -= remaining_pods_score(copy_node_b, not_movable_score, movable_score)
    return score


def get_scores(current_state, desired_state):
    """
    Generates all possible combinations between nodes and calculates the score for each combination.
    """
    not_movable_score = 100
    movable_score = 1

    #Current -> Desired
    scores = {}
    for node_current_name, node_current_info in current_state.items():
        score = {None: -remaining_pods_score(node_current_info, not_movable_score, movable_score)}
        for node_desired_name, node_desired_info in desired_state.items():
            cur_score = calc_score_per_node(node_current_info, node_desired_info, not_movable_score, movable_score)
            score[node_desired_name] = cur_score
        scores[node_current_name] = score
    return scores


def rec_find_highest_score(current_state_list, desired_state_list, scores):
    """
    Uses recursion to find the highest scoring mapping of current nodes to desired nodes.
    """
    if not current_state_list:
        return 0, {}

    copy_current_state_list = list(current_state_list)
    node_name = copy_current_state_list.pop()
    max_score = -math.inf
    max_mapping = None
    for node_b_name in desired_state_list:
        score = scores[node_name][node_b_name]
        copy_desired_state_list = list(desired_state_list)
        copy_desired_state_list.remove(node_b_name)
        prev_score, prev_mapping = rec_find_highest_score(copy_current_state_list, copy_desired_state_list, scores)
        cur_score = prev_score + score
        prev_mapping[node_name] = node_b_name
        cur_mapping = prev_mapping
        if cur_score > max_score:
            max_score = cur_score
            max_mapping = cur_mapping
    # CHANGE IT Mapping is from current -> desired
    return max_score, max_mapping


def find_highest_score_mapping(current_state_list, desired_state_list, scores):
    """
    Helper function to start the recursion loop to find the highest scoring mapping of current nodes to desired nodes.
    """
    for i in range(0, len(current_state_list)-len(desired_state_list)):
        desired_state_list.append(None)
    score, mapping = rec_find_highest_score(current_state_list, desired_state_list, scores)
    return mapping


def match_nodes_desired_with_current_state(current_state, desired_state):
    """
    Retrieves first the matching scores and uses this to initiate the search for the best mapping. This mapping is returned.
    """
    scores = get_scores(current_state, desired_state)
    return find_highest_score_mapping(list(current_state.keys()), list(desired_state.keys()), scores)


def already_on_node(des_pod_info, current_state_pods, remove_list):
    """
    Checks if the given node is already present. Taking into account previously matched node using the remove_list.
    """
    for cur_pod_name, cur_pod_info in current_state_pods.items():
        if des_pod_info["pod_generate_name"] == cur_pod_info["pod_generate_name"]:
            if cur_pod_name in remove_list:
                remove_list.remove(cur_pod_name)
                return True
    return False


def remove_daemon_sets(state):
    """
    Deamonsets do not have to be taken into account when matching nodes, and therefore can be removed.
    """
    state_copy = copy.deepcopy(state)
    for node_name, node_info in state.items():
        for pod_name, pod_info in node_info["pods"].items():
            if pod_info["kind"] == "DaemonSet":
                del state_copy[node_name]["pods"][pod_name]
    return state_copy


def valid_transition(add_list, remove_list, pods):
    """
    Verifies that no unmovable pods have to be moved.
    """
    for name in add_list:
        for pod_info in pods.values():
            if pod_info["pod_generate_name"] == name:
                if not removable(pod_info):
                    return False
    for name in remove_list:
        if not removable(pods[name]):
            return False
    return True


def find_transitions_execution_change(current_state, desired_state):
    """
    First matches the nodes.
    Verifies the matching.
    Generates the transition description that can be used by the planner.
    """
    transitions = {}
    node_mapping = match_nodes_desired_with_current_state(current_state, desired_state)

    daemon_less_current_state = remove_daemon_sets(current_state)
    daemon_less_desired_state = remove_daemon_sets(desired_state)

    for cur_node_name, cur_node_info in daemon_less_current_state.items():
        des_mapped_node_name = node_mapping[cur_node_name]
        add_list = []
        remove_list = list(cur_node_info["pods"].keys())
        if des_mapped_node_name is not None:
            for des_pod_info in daemon_less_desired_state[des_mapped_node_name]["pods"].values():
                if not already_on_node(des_pod_info, cur_node_info["pods"], remove_list):
                    add_list.append(des_pod_info["pod_generate_name"])

        if not valid_transition(add_list, remove_list, cur_node_info["pods"]):
            return False, None

        transitions[cur_node_name] = {
            "add": add_list,
            "remove": remove_list
        }

        if node_mapping[cur_node_name] is None:
            transitions[cur_node_name]["delete"] = True
    return True, transitions
