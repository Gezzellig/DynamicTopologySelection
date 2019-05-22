import subprocess
import time


def migrate_pod(destination_node, pod_name, deployment_name, namespace, prestart=False):
    subprocess.run(["kubectl", "label", "node", destination_node, "node-preference={}".format(deployment_name)])
    subprocess.run(["kubectl", "delete", "pod", pod_name, "-n", namespace])

    print("deleted")
    time.sleep(30)
    subprocess.run(["kubectl", "label", "node", destination_node, "node-preference-"])



def main():
    print("migrating pod")
    node1="gke-develop-cluster-larger-pool-9ecdadbf-1qcw"
    node2="gke-develop-cluster-larger-pool-9ecdadbf-w9bw"
    migrate_pod(node2, "php-apache-85546b856f-2cl9s", "php-apache", "demo")



if __name__ == '__main__':
    main()
