import subprocess
import time

from kubernetes_tools import extract_pods
from log import log


class PodException(Exception):
    pass


class PodNotMovableException(PodException):
    pass


class PodScheduledOnWrongNodeException(PodException):
    def __init__(self, destination, result):
        PodException("Destination: {}, ended up in: {}".format(destination, result))


class VerificationTookTooLongException(PodException):
    pass


def get_individual_pod_info(pod_name, state):
    for pod_name, pod_info in state.items():
        if pod_info["pod_name"] == pod_name:
            return pod_info


def get_deployment_from_generate_name(pod_info):
    generate_name = pod_info["pod_generate_name"]
    parts = generate_name.rsplit("-", 2)
    return generate_name, parts[0]


def get_pods_of_one_generate(generate_name, state):
    one_deployment = {}
    for pod_name, pod_info in state.items():
        if pod_info["pod_generate_name"] == generate_name:
            one_deployment[pod_name] = pod_info
    return one_deployment


def verify_migration(destination_node, generate_name, initial_state):
    current_state = extract_pods.extract_all_pods()
    if len(current_state) == len(initial_state):
        initial_deployment_pods = get_pods_of_one_generate(generate_name, initial_state)
        current_deployment_pods = get_pods_of_one_generate(generate_name, current_state)
        if len(initial_deployment_pods) == len(current_deployment_pods):
            for current_pod_name, info in current_deployment_pods.items():
                if current_pod_name not in initial_deployment_pods:
                    if info["node_name"] is None:
                        return False
                    if info["node_name"] == destination_node:
                        log.info("MOVEMENT SUCCEEEDED")
                        return True
                    else:
                        log.info("FAILED")
                        raise PodScheduledOnWrongNodeException(destination_node, info["node_name"])
    return False


def migrate_pod(pod_name, destination_node):
    initial_state = extract_pods.extract_all_pods()

    migrating_pod_info = initial_state[pod_name]
    if not extract_pods.movable(migrating_pod_info):
        raise PodNotMovableException()
    namespace = migrating_pod_info["namespace"]
    deployment_name = migrating_pod_info["deployment_name"]
    generate_name = migrating_pod_info["pod_generate_name"]

    log.info("moving: {} to {} using deployment name: {}".format(pod_name, destination_node, deployment_name))
    try:
        subprocess.run(["kubectl", "label", "node", destination_node, "node-preference={}".format(deployment_name)])
        subprocess.run(["kubectl", "delete", "pod", pod_name, "-n", namespace])
        log.info("pod {} is deleted".format(pod_name))
        counter = 0
        while not verify_migration(destination_node, generate_name, initial_state):
            time.sleep(2)
            if counter > 5:
                raise VerificationTookTooLongException()
            counter += 1
    except PodException as e:
        raise e
    finally:
        subprocess.run(["kubectl", "label", "node", destination_node, "node-preference-"])
