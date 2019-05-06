import json
import random
import sys

import requests
from kubernetes import config, client

from SmartKubernetesSchedular import extract_pods


def redeploy(settings):
    #Todo: probably move this to a central file
    #configuration = config.load_kube_config()
    #k8s_api = client.CoreV1Api(client.ApiClient(configuration))


    redeploy_amount = settings["strategy"]["settings"]["redeploy_amount"]
    pods = extract_pods.extract_pods(settings)
    redeploy_pods = random.sample(pods, redeploy_amount)
    for redeploy_pod in redeploy_pods:
        #TODO change this so it uses the kubernetes package
        #result = k8s_api.connect_delete_namespaced_pod_proxy(redeploy_pod["pod_name"], settings["kubernetes_project_namespace"], path="")

        command = "http://localhost:8080/api/v1/namespaces/{namespace}/pods/{pod_name}".format(namespace=settings["kubernetes_project_namespace"], pod_name=redeploy_pod["pod_name"])
        print(requests.delete(command))

def main():
    print("random_pod_redeployment")
    settings_file_name = sys.argv[1]
    print("Settings: {}".format(settings_file_name))
    with open(settings_file_name) as file:
        settings = json.load(file)
    redeploy(settings)


if __name__ == '__main__':
    main()
