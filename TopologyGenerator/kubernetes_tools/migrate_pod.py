import subprocess
import time

from SmartKubernetesSchedular import extract_pods


class PodMigrationException(Exception):
    pass


class PodScheduledOnWrongNodeException(PodMigrationException):
    def __init__(self, destination, result):
        PodMigrationException("Destination: {}, ended up in: {}".format(destination, result))


class VerificationTookTooLongException(PodMigrationException):
    pass


def get_individual_pod_info(pod_name, state):
    for pod_info in state:
        print(pod_info["pod_name"])
        if pod_info["pod_name"] == pod_name:
            return pod_info


def get_deployment_from_generate_name(pod_info):
    generate_name = pod_info["pod_generate_name"]
    parts = generate_name.rsplit("-", 2)
    return generate_name, parts[0]


def get_pods_of_one_generate(generate_name, state):
    one_deployment = {}
    for pod in state:
        if pod["pod_generate_name"] == generate_name:
            one_deployment[pod["pod_name"]] = pod
    return one_deployment


def verify_migration(destination_node, removed_pod_name, generate_name, initial_state):
    current_state = extract_pods.extract_all_pods()
    print(len(current_state), len(initial_state))
    if len(current_state) == len(initial_state):
        initial_deployment_pods = get_pods_of_one_generate(generate_name, initial_state)
        current_deployment_pods = get_pods_of_one_generate(generate_name, current_state)
        if len(initial_deployment_pods) == len(current_deployment_pods):
            for current_pod_name, info in current_deployment_pods.items():
                if current_pod_name not in initial_deployment_pods:
                    if info["node_name"] == destination_node:
                        print("MOVEMENT SUCCEEEDED")
                        return True
                    else:
                        print("FAILED")
                        raise PodScheduledOnWrongNodeException(destination_node, info["node_name"])
    return False


def migrate_pod(destination_node, pod_name, namespace, prestart=False):
    initial_state = extract_pods.extract_all_pods()
    #todo remove, so it each time automatically selects a pod to move
    for pod in initial_state:
        if pod["pod_generate_name"] == "php-apache-85546b856f-":
            pod_name = pod["pod_name"]

            node1 = "gke-develop-cluster-larger-pool-9ecdadbf-l786"
            node2 = "gke-develop-cluster-larger-pool-9ecdadbf-vvdj"

            if node1 == pod["node_name"]:
                destination_node = node2
            else:
                destination_node = node1

    #destination_node = "gke-develop-cluster-larger-pool-9ecdadbf-pnsb"
    migrating_pod_info = get_individual_pod_info(pod_name, initial_state)
    print(migrating_pod_info)
    generate_name, deployment_name = get_deployment_from_generate_name(migrating_pod_info)



    print("moving: {} to {}".format(pod_name, destination_node))
    try:
        subprocess.run(["kubectl", "label", "node", destination_node, "node-preference={}".format(deployment_name)])
        time.sleep(2)
        subprocess.run(["kubectl", "delete", "pod", pod_name, "-n", namespace])


        print("deleted")
        counter = 0
        while not verify_migration(destination_node, pod_name, generate_name, initial_state):
            time.sleep(2)
            print("retry")
            if counter > 5:
                raise VerificationTookTooLongException()
            counter += 1
        #time.sleep(30)
    except PodMigrationException as e:
        raise e
    finally:
        subprocess.run(["kubectl", "label", "node", destination_node, "node-preference-"])


def main():
    print("migrating pod")
    node1="gke-develop-cluster-larger-pool-9ecdadbf-1qcw"
    node2="gke-develop-cluster-larger-pool-9ecdadbf-w9bw"
    migrate_pod(node2, "php-apache-85546b856f-2cl9s", "demo")



if __name__ == '__main__':
    main()
