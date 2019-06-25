import subprocess
import time

from kubernetes_tools import extract_pods
from kubernetes_tools.change_deployment_scale import increase_deployment_scale
from kubernetes_tools.migrate_pod import PodScheduledOnWrongNodeException, PodException, \
    VerificationTookTooLongException
from log import log


class MultiplePodsCreatedException(PodException):
    pass


def verify_addition(destination_node, deployment_name, initial_state):
    current_state = extract_pods.extract_pods_deployment(deployment_name)
    if not len(current_state) == len(initial_state):
        if len(current_state) == len(initial_state)+1:
            for current_pod_name, info in current_state.items():
                if current_pod_name not in initial_state:
                    if info["node_name"] == destination_node:
                        log.info("Addition succeeded, pod name: {}".format(current_pod_name))
                        return True
                    else:
                        log.error("Addition failed")
                        raise PodScheduledOnWrongNodeException(destination_node, info["node_name"])
        else:
            raise MultiplePodsCreatedException()
    return False


def add_pod_deployment(destination_node, deployment_name, namespace):
    initial_state = extract_pods.extract_pods_deployment(deployment_name)
    log.info("creating: {} on {}".format(deployment_name, destination_node))
    try:
        subprocess.run(["kubectl", "label", "node", destination_node, "node-preference={}".format(deployment_name)])
        increase_deployment_scale(deployment_name, namespace)
        counter = 0
        while not verify_addition(destination_node, deployment_name, initial_state):
            time.sleep(2)
            if counter > 5:
                raise VerificationTookTooLongException()
            counter += 1
    except PodException as e:
        raise e
    finally:
        subprocess.run(["kubectl", "label", "node", destination_node, "node-preference-"])



