import subprocess

from log import log
class NodeException(Exception):
    pass


class NodeCouldNotBeDrainedException(NodeException):
    pass

def cordon_node(node_name):
    subprocess.run(["kubectl", "cordon", node_name])


def uncordon_node(node_name):
    subprocess.run(["kubectl", "uncordon", node_name])


def ensure_preliminary_replacement(node_name):
    cordon_node(node_name)


def drain_node(node_name):
    result = subprocess.run(["kubectl", "drain", node_name, "--ignore-daemonsets"])
    if not result.returncode == 0:
        raise NodeCouldNotBeDrainedException()


def soft_taint_node(node_name):
    subprocess.run(["kubectl", "taint", "nodes", node_name, "no_pod=no_pod:PreferNoSchedule"])


def remove_soft_taint_node(node_name):
    subprocess.run(["kubectl", "taint", "nodes", node_name, "no_pod:NoSchedule-"])


def delete_node(node_name):
    log.info("Deleting node: {}".format(node_name))
    drain_node(node_name)
    subprocess.run(["kubectl", "delete", "node", node_name])
    log.info("Deletion successful, node: {}".format(node_name))


def evict_node(node_name, preliminary_replacement=False):
    if preliminary_replacement:
        ensure_preliminary_replacement(node_name)
    drain_node(node_name)
    uncordon_node(node_name)
    soft_taint_node(node_name)


def main():
    delete_node("gke-demo-cluster-1-default-pool-6f471531-1sq8")

if __name__ == '__main__':
    main()