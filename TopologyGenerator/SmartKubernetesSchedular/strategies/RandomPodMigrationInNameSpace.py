import random

from SmartKubernetesSchedular import extract_pods, extract_nodes, deployment
from SmartKubernetesSchedular.strategies.AbstractStratagy import AbstractStratagy, CouldNotGenerateImprovementException


class RandomPodMigrationInNameSpace(AbstractStratagy):
    def generate_improvement(self, settings):
        counter = 0
        migrations = []
        found_change = False
        while not found_change:
            namespace = settings["project_namespace"]
            pods = extract_pods.extract_pods_namespace(namespace)
            nodes = extract_nodes.extract_all_nodes()
            selected_pod = random.sample(pods, 1)[0]
            target_node = random.sample(nodes.keys(), 1)[0]
            if target_node == selected_pod["node_name"]:
                continue

            nodes = extract_nodes.extract_all_nodes()
            pods = extract_pods.extract_all_pods_dict()
            new_deployment = deployment.extract_deployment(pods, nodes)

            print(selected_pod, target_node)
            print(new_deployment)

            new_deployment[selected_pod["node_name"]].remove(selected_pod["pod_name"])
            new_deployment[target_node].append(selected_pod["pod_name"])

            print(new_deployment)

            found_change, migrations = deployment.construct_deployment_sequence(new_deployment)
            counter += 1

            if counter >= 10:
                raise CouldNotGenerateImprovementException("Tried 10 times, but no improvement was possible")
        return migrations





