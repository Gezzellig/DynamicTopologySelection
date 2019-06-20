import copy
import math

from kubernetes_tools.extract_pods import movable


def scoring(pod_info, not_movable_score, movable_score):
    if pod_info["kind"] == "DaemonSet":
        return 0
    if movable(pod_info):
        return movable_score
    else:
        return not_movable_score


def pod_score(pod_a_name, pod_a, node_b, copy_node_a, copy_node_b, not_movable_score, movable_score):
        for pod_b_name, pod_b in node_b["pods"].items():
            if pod_a["pod_generate_name"] == pod_b["pod_generate_name"]:
                if pod_b_name in copy_node_b["pods"]:
                    del copy_node_b["pods"][pod_b_name]
                    del copy_node_a["pods"][pod_a_name]
                    return scoring(pod_a, not_movable_score, movable_score)
        return 0


def remaining_pods_score(copy_node, not_movable_score, movable_score):
    score = 0
    for pod_info in copy_node["pods"].values():
        score += scoring(pod_info, not_movable_score, movable_score)
    return score


def calc_score_per_node(node_a, node_b):
    copy_node_a = copy.deepcopy(node_a)
    copy_node_b = copy.deepcopy(node_b)
    not_movable_score = 100
    movable_score = 1
    score = 0
    for pod_a_name, pod_a_info in node_a["pods"].items():
        score += pod_score(pod_a_name, pod_a_info, node_b, copy_node_a, copy_node_b, not_movable_score, movable_score)

    score -= remaining_pods_score(copy_node_a, not_movable_score, movable_score)
    score -= remaining_pods_score(copy_node_b, not_movable_score, movable_score)
    return score


def get_scores(current_state, desired_state):
    #Current -> Desired
    scores = {}
    for node_desired_name, node_desired_info in desired_state.items():
        score = {}
        for node_current_name, node_current_info in current_state.items():
            cur_score = calc_score_per_node(node_current_info, node_desired_info)
            score[node_current_name] = cur_score
        print(node_desired_name)
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
    # CHANGE IT Mapping is from current -> desired
    return max_score, max_mapping


def find_highest_score_mapping(scores):
    score, mapping = rec_find_highest_score(list(scores.keys()), scores)
    print(score)
    return mapping


def match_nodes_desired_with_current_state(current_state, desired_state):
    scores = get_scores(current_state, desired_state)
    print(scores)
    return find_highest_score_mapping(scores)


def already_on_node(des_pod_info, current_state_pods, remove_list):
    for cur_pod_name, cur_pod_info in current_state_pods.items():
        if des_pod_info["pod_generate_name"] == cur_pod_info["pod_generate_name"]:
            if cur_pod_name in remove_list:
                remove_list.remove(cur_pod_name)
                return True
    return False


def not_movable_transition(add_list, remove_list, current_state_node):
    for name in add_list:
        for pod_info in current_state_node["pods"].values():
            if pod_info["pod_generate_name"] == name:
                if not movable(pod_info):
                    return True
    for name in remove_list:
        if not movable(current_state_node["pods"][name]):
            return True
    return False


def find_transitions_execution_change(current_state, desired_state):
    transitions = {}
    node_mapping = match_nodes_desired_with_current_state(current_state, desired_state)
    print(node_mapping)

    for des_node_name, des_node_info in desired_state.items():
        mapped_node_name = node_mapping[des_node_name]
        add_list = []
        remove_list = list(current_state[mapped_node_name]["pods"].keys())
        for des_pod_info in des_node_info["pods"].values():
            if not already_on_node(des_pod_info, current_state[mapped_node_name]["pods"], remove_list):
                add_list.append(des_pod_info["pod_generate_name"])

        if not_movable_transition(add_list, remove_list, current_state[mapped_node_name]):
            return False, None


        transitions[mapped_node_name] = {
            "add": add_list,
            "remove": remove_list
        }
    return True, transitions
