import sys

import load_settings
from SmartKubernetesSchedular import enforcer
from SmartKubernetesSchedular.deployment import state_transition_plan
from SmartKubernetesSchedular.strategies.TryEmptyOneNode import TryEmptyOneNode
from kubernetes_tools import extract_pods, extract_nodes
from SmartKubernetesSchedular.strategies.RandomPodMigrationInNameSpace import RandomPodMigrationInNameSpace


def transition_state(transitions, pods, nodes):
    print(transitions)
    down, migrate, up = state_transition_plan(transitions, pods, nodes)
    print(down)
    print(migrate)
    print(up)
    enforcer.enforce(down, migrate, up)


def main():
    settings = load_settings.load_settings(sys.argv[1])
    algorithm = TryEmptyOneNode()

    initial_pods = extract_pods.extract_all_pods()
    initial_nodes = extract_nodes.extract_all_nodes_cpu()
    success, transitions = algorithm.generate_improvement(settings)
    if success:
        transition_state(transitions, initial_pods, initial_nodes)


if __name__ == '__main__':
    main()
