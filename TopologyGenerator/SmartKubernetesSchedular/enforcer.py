import json
import unittest

from SmartKubernetesSchedular import extract_pods
from kubernetes_tools.migrate_pod import migrate_pod


class PodHasScaledWhileEnforcingException(Exception):
    pass

def state_to_generate_name_count(state):
    generate_name_count = {}
    for pod in state:
        gen_name = pod["pod_generate_name"]
        if gen_name in generate_name_count:
            generate_name_count[gen_name] += 1
        else:
            generate_name_count[gen_name] = 1
    return generate_name_count


def enforce_movements(movements, initial_state):
    initial_generate_name_count = state_to_generate_name_count(initial_state)
    for pod_name, destination_node in movements.items():
        current_state = extract_pods.extract_all_pods()
        current_generate_name_count = state_to_generate_name_count(current_state)
        if not initial_generate_name_count == current_generate_name_count:
            raise PodHasScaledWhileEnforcingException()
        print("performing movement: {} to {}".format(pod_name, destination_node))
        migrate_pod(pod_name, destination_node)



def main():
    print("starting enforcer")
    movements_file_name = "movement.json"
    print("Movement file: {}".format(movements_file_name))
    with open(movements_file_name) as file:
        movements = json.load(file)

    initial_state = extract_pods.extract_all_pods()
    enforce_movements(movements, initial_state)


if __name__ == '__main__':
    main()
