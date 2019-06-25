import subprocess


def cordon_node(node_name):
    subprocess.run(["kubectl", "cordon", node_name])


def uncordon_node(node_name):
    subprocess.run(["kubectl", "uncordon", node_name])


def ensure_preliminary_replacement(node_name):
    cordon_node(node_name)


def drain_node(node_name):
    subprocess.run(["kubectl", "drain", node_name, "--ignore-daemonsets"])


def soft_taint_node(node_name):
    subprocess.run(["kubectl", "taint", "nodes", node_name, "no_pod=no_pod:PreferNoSchedule"])


def remove_soft_taint_node(node_name):
    subprocess.run(["kubectl", "taint", "nodes", node_name, "no_pod:NoSchedule-"])


def evict_node(node_name, preliminary_replacement=False):
    if preliminary_replacement:
        ensure_preliminary_replacement(node_name)
    drain_node(node_name)
    uncordon_node(node_name)
    soft_taint_node(node_name)
