import sys

import requests

from load_settings import load_settings


class CouldNotEvictPodException(Exception):
    pass


class CouldNotDeletePodException(Exception):
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


def delete_pod(pod_name, namespace, settings):
    print("deleting pod: {}".format(pod_name))
    command = "http://localhost:8080/api/v1/namespaces/{namespace}/pods/{name}".format(namespace=namespace, name=pod_name)
    result = requests.delete(command)
    if result.status_code == 200:
        raise CouldNotDeletePodException("status_code: {}".format(result.status_code))


def main():
    settings = load_settings(sys.argv[1])
    pod_name = "php-apache-59cdc7978b-ztj8d"
    delete_pod(pod_name, settings["project_namespace"], settings)


if __name__ == '__main__':
    main()