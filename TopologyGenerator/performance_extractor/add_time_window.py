import json
import sys

from kubernetes import client, config


def main():
    print("starting add_time_window")
    config.load_kube_config()
    k8s_api = client.CoreV1Api()
    settings_file_name = sys.argv[1]
    print("Settings: {}".format(settings_file_name))
    with open(settings_file_name) as file:
        settings = json.load(file)
    name_space = settings["kubernetes_project_namespace"]
    print(k8s_api.list_namespaced_pod(name_space))



if __name__ == '__main__':
    main()
