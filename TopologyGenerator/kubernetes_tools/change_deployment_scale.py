import subprocess

import requests

from KubernetesAPIConnector import get_k8s_client


def get_deployment_scale(deployment_name, namespace):
    print(deployment_name)
    print(namespace)
    url = "http://localhost:8080/apis/extensions/v1beta1/namespaces/{}/deployments/{}/scale".format(namespace, deployment_name)
    result = requests.get(url).json()
    return result["spec"]["replicas"]


def change_deployment_scale(deployment_name, namespace, new_scale):
    subprocess.run(["kubectl", "scale", "--replicas={}".format(new_scale), "deployment/{}".format(deployment_name), "-n", namespace])


def increase_deployment_scale(deployment_name, namespace, amount=1):
    cur_scale = get_deployment_scale(deployment_name, namespace)
    new_scale = cur_scale + amount
    change_deployment_scale(deployment_name, namespace, new_scale)


def decrease_deployment_scale(deployment_name, namespace, amount=1):
    increase_deployment_scale(deployment_name, namespace, amount=-amount)

