#Stateful set check.

# Check if the node is allowed to be removed, can be blocked by for example a stateful set
import asyncio
import subprocess
import sys

import load_settings


# Ensures that no pods can be scheduled on this node.
def cordon_node(node_name):
    subprocess.run(["kubectl", "cordon", node_name])


def uncordon_node(node_name):
    subprocess.run(["kubectl", "uncordon", node_name])


def ensure_preliminary_replacement(node_name):
    cordon_node(node_name)

    #Duplicate pods on the node


def drain_node(node_name):
    subprocess.run(["kubectl", "drain", node_name, "--ignore-daemonsets"])


def soft_taint_node(node_name):
    subprocess.run(["kubectl", "taint", "nodes", node_name, "no_pod=no_pod:PreferNoSchedule"])


def remove_soft_taint_node(node_name):
    subprocess.run(["kubectl", "taint", "nodes", node_name, "no_pod:NoSchedule-"])


async def node_removed_timeout(node_name):
    await asyncio.sleep(6)
    print("untaint if node still exists")



def evict_node(node_name, preliminary_replacement=False):
    if preliminary_replacement:
        ensure_preliminary_replacement(node_name)
    drain_node(node_name)
    uncordon_node(node_name)
    soft_taint_node(node_name)


def main():
    settings = load_settings.load_settings(sys.argv[1])
    node_name = "gke-develop-cluster-larger-pool-9ecdadbf-gc9n"
    #evict_node(node_name)
    asyncio.run(node_removed_timeout(node_name))
    print("jljlefj")



if __name__ == '__main__':
    main()