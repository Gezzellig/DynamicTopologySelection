import sys

import load_settings
from SmartKubernetesSchedular import enforcer
from kubernetes_tools import extract_pods
from SmartKubernetesSchedular.strategies.RandomPodMigrationInNameSpace import RandomPodMigrationInNameSpace


def main():
    settings = load_settings.load_settings(sys.argv[1])
    algorithm = RandomPodMigrationInNameSpace()
    migrations = algorithm.generate_improvement(settings)

    initial_state = extract_pods.extract_all_pods()
    enforcer.enforce_migrations(migrations, initial_state)


if __name__ == '__main__':
    main()
