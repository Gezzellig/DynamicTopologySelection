import copy
import math


def pod_score(pod_a_name, pod_a, node_b, copy_node_a, copy_node_b, stateful_set_score, deployment_score):
        for pod_b_name, pod_b in node_b["pods"].items():
            if pod_a["pod_generate_name"] == pod_b["pod_generate_name"]:
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
    for pod_a_name, pod_a in node_a["pods"].items():
        score += pod_score(pod_a_name, pod_a, node_b, copy_node_a, copy_node_b, stateful_set_score, deployment_score)

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


def find_transitions_execution_change(current_state, desired_state):
    transitions = {}
    node_mapping = match_nodes_desired_with_current_state(current_state, desired_state)
    for des_node_name, des_node_info in desired_state.items():
        mapped_node_name = node_mapping[des_node_name]
        add_list = []
        for des_pod_info in des_node_info["pods"].values():
            add_list.append(des_pod_info["pod_generate_name"])
        remove_list = list(current_state[mapped_node_name]["pods"].keys())

        for des_pod_info in des_node_info["pods"].values():
            for cur_pod_name, cur_pod_info in current_state[mapped_node_name]["pods"].items():
                if des_pod_info["pod_generate_name"] == cur_pod_info["pod_generate_name"]:
                    add_list.remove(des_pod_info["pod_generate_name"])
                    remove_list.remove(cur_pod_name)

        transitions[des_node_name] = {
            "add": add_list,
            "remove": remove_list
        }
    return transitions
