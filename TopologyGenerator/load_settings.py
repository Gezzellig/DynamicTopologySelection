import json
import subprocess
import time

from kubernetes_tools import extract_pods


def load_settings(settings_file_name):
    print("Settings: {}".format(settings_file_name))
    with open(settings_file_name) as file:
        settings = json.load(file)
    return settings


def test():
    counter = 0
    while True:
        state = extract_pods.extract_all_pods()
        for pod_name, pod_info in state.items():
            if pod_info["kind"] == "ReplicaSet":
                subprocess.run(["kubectl", "delete", "pod", pod_name, "-n", pod_info["namespace"]])
                break
        counter += 1
        print(counter)
        time.sleep(0.01)


if __name__ == '__main__':
    test()
