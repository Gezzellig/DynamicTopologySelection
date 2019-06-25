import subprocess
import sys
import time

import requests

from kubernetes_tools import extract_pods
from kubernetes_tools.change_deployment_scale import decrease_deployment_scale
from kubernetes_tools.migrate_pod import VerificationTookTooLongException, PodException
from load_settings import load_settings


class CouldNotEvictPodException(PodException):
    pass


class CouldNotDeletePodException(PodException):
    pass


def evict_pod(pod_name, namespace, settings):
    print("evicting pod: {}".format(pod_name))
    eviction_data = \
        {
          "apiVersion": "policy/v1beta1",
          "kind": "Eviction",
          "metadata": {
            "name": pod_name,
            "namespace": namespace
          }
        }
    command = "http://{kube}/api/v1/namespaces/{namespace}/pods/{name}/eviction".format(kube=settings["kubernetes_api"], namespace=namespace, name=pod_name)
    result = requests.post(command, json=eviction_data)
    if not result.status_code == 201:
        raise CouldNotEvictPodException("status_code: {}".format(result.status_code))


def delete_pod(pod_name, namespace):
    subprocess.run(["kubectl", "delete", "pod", pod_name, "-n", namespace])


def verify_deletion(pod_name, deployment_name, initial_state):
    current_state = extract_pods.extract_pods_deployment(deployment_name)
    if not pod_name in current_state:
        if len(initial_state) > len(current_state):
            return True
    return False


def delete_pod_deployment(pod_name, deployment_name, namespace):
    initial_state = extract_pods.extract_pods_deployment(deployment_name)
    delete_pod(pod_name, namespace)
    decrease_deployment_scale(deployment_name, namespace)
    time.sleep(1)
    counter = 0
    while not verify_deletion(pod_name, deployment_name, initial_state):
        time.sleep(2)
        if counter > 10:
            raise VerificationTookTooLongException()
        counter += 1


def main():
    pod_name = "php-apache-85546b856f-m7l9g"
    deployment_name = "php-apache"
    namespace = "demo"
    delete_pod_deployment(pod_name, deployment_name, namespace)


if __name__ == '__main__':
    main()
