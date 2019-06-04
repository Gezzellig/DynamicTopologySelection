import unittest

from SmartKubernetesSchedular.strategies.TryEmptyOneNode import recursive_find_new_distributions, \
    least_transitions_removable, find_pods_to_be_rescheduled, select_lowest_max_requested, \
    change_selected_distribution_into_transitions


class TestExtractNodes(unittest.TestCase):
    def setUp(self):
        self.nodes = {
            "a": {
                "cpu": 1,
                "pods": [
                    {
                        "pod_name": "1-1",
                        "node_name": "a",
                        "pod_generate_name": "1-",
                        "deployment_name": "1",
                        "kind": "ReplicaSet",
                        "namespace": "test",
                        "total_requested": 0.2,
                        "containers": ["testie"]
                    },
                    {
                        "pod_name": "1-3",
                        "node_name": "a",
                        "pod_generate_name": "1-",
                        "deployment_name": "1",
                        "kind": "ReplicaSet",
                        "namespace": "test",
                        "total_requested": 0.2,
                        "containers": ["testie"]
                    },
                    {
                        "pod_name": "2-1",
                        "node_name": "a",
                        "pod_generate_name": "2-",
                        "deployment_name": "2",
                        "kind": "ReplicaSet",
                        "namespace": "test",
                        "total_requested": 0.1,
                        "containers": ["testie"]
                    },
                    {
                        "pod_name": "2-2",
                        "node_name": "a",
                        "pod_generate_name": "2-",
                        "deployment_name": "2",
                        "kind": "ReplicaSet",
                        "namespace": "test",
                        "total_requested": 0.1,
                        "containers": ["testie"]
                    }
                ]
            },
            "b": {
                "cpu": 1,
                "pods": [
                    {
                        "pod_name": "1-2",
                        "node_name": "b",
                        "pod_generate_name": "1-",
                        "deployment_name": "1",
                        "kind": "ReplicaSet",
                        "namespace": "test",
                        "total_requested": 0.2,
                        "containers": ["testie"]
                    },
                    {
                        "pod_name": "2-3",
                        "node_name": "b",
                        "pod_generate_name": "2-",
                        "deployment_name": "2",
                        "kind": "ReplicaSet",
                        "namespace": "test",
                        "total_requested": 0.1,
                        "containers": ["testie"]
                    },
                    {
                        "pod_name": "2-4",
                        "node_name": "b",
                        "pod_generate_name": "2-",
                        "deployment_name": "2",
                        "kind": "ReplicaSet",
                        "namespace": "test",
                        "total_requested": 0.1,
                        "containers": ["testie"]
                    },
                    {
                        "pod_name": "3-1",
                        "node_name": "b",
                        "pod_generate_name": "3-",
                        "deployment_name": "3",
                        "kind": "DaemonSet",
                        "namespace": "test",
                        "total_requested": 0.2,
                        "containers": ["testie"]
                    }
                ]
            },
            "c": {
                "cpu": 1,
                "pods": [
                    {
                        "pod_name": "3-2",
                        "node_name": "c",
                        "pod_generate_name": "3-",
                        "deployment_name": "3",
                        "kind": "DaemonSet",
                        "namespace": "test",
                        "total_requested": 0.2,
                        "containers": ["testie"]
                    },
                    {
                        "pod_name": "4-1",
                        "node_name": "c",
                        "pod_generate_name": "4-",
                        "deployment_name": "4",
                        "kind": "ReplicaSet",
                        "namespace": "test",
                        "total_requested": 0.2,
                        "containers": ["testie"]
                    },
                    {
                        "pod_name": "4-2",
                        "node_name": "c",
                        "pod_generate_name": "4-",
                        "deployment_name": "4",
                        "kind": "ReplicaSet",
                        "namespace": "test",
                        "total_requested": 0.2,
                        "containers": ["testie"]
                    }
                ]
            }
        }
        self.reschedule_pods = [
            {
                "pod_name": "4-1",
                "node_name": "c",
                "pod_generate_name": "4-",
                "deployment_name": "4",
                "kind": "ReplicaSet",
                "namespace": "test",
                "total_requested": 0.2,
                "containers": ["testie"]
            },
            {
                "pod_name": "4-2",
                "node_name": "c",
                "pod_generate_name": "4-",
                "deployment_name": "4",
                "kind": "ReplicaSet",
                "namespace": "test",
                "total_requested": 0.2,
                "containers": ["testie"]
            }
        ]
        self.new_distributions = [{'a': {'cpu': 1, 'pods': [{'pod_name': '1-1', 'node_name': 'a', 'pod_generate_name': '1-', 'deployment_name': '1', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.2, 'containers': ['testie']}, {'pod_name': '1-3', 'node_name': 'a', 'pod_generate_name': '1-', 'deployment_name': '1', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.2, 'containers': ['testie']}, {'pod_name': '2-1', 'node_name': 'a', 'pod_generate_name': '2-', 'deployment_name': '2', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.1, 'containers': ['testie']}, {'pod_name': '2-2', 'node_name': 'a', 'pod_generate_name': '2-', 'deployment_name': '2', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.1, 'containers': ['testie']}, {'pod_name': '4-2', 'node_name': 'c', 'pod_generate_name': '4-', 'deployment_name': '4', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.2, 'containers': ['testie']}, {'pod_name': '4-1', 'node_name': 'c', 'pod_generate_name': '4-', 'deployment_name': '4', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.2, 'containers': ['testie']}]}, 'b': {'cpu': 1, 'pods': [{'pod_name': '1-2', 'node_name': 'b', 'pod_generate_name': '1-', 'deployment_name': '1', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.2, 'containers': ['testie']}, {'pod_name': '2-3', 'node_name': 'b', 'pod_generate_name': '2-', 'deployment_name': '2', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.1, 'containers': ['testie']}, {'pod_name': '2-4', 'node_name': 'b', 'pod_generate_name': '2-', 'deployment_name': '2', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.1, 'containers': ['testie']}, {'pod_name': '3-1', 'node_name': 'b', 'pod_generate_name': '3-', 'deployment_name': '3', 'kind': 'DaemonSet', 'namespace': 'test', 'total_requested': 0.2, 'containers': ['testie']}]}}, {'a': {'cpu': 1, 'pods': [{'pod_name': '1-1', 'node_name': 'a', 'pod_generate_name': '1-', 'deployment_name': '1', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.2, 'containers': ['testie']}, {'pod_name': '1-3', 'node_name': 'a', 'pod_generate_name': '1-', 'deployment_name': '1', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.2, 'containers': ['testie']}, {'pod_name': '2-1', 'node_name': 'a', 'pod_generate_name': '2-', 'deployment_name': '2', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.1, 'containers': ['testie']}, {'pod_name': '2-2', 'node_name': 'a', 'pod_generate_name': '2-', 'deployment_name': '2', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.1, 'containers': ['testie']}, {'pod_name': '4-2', 'node_name': 'c', 'pod_generate_name': '4-', 'deployment_name': '4', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.2, 'containers': ['testie']}]}, 'b': {'cpu': 1, 'pods': [{'pod_name': '1-2', 'node_name': 'b', 'pod_generate_name': '1-', 'deployment_name': '1', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.2, 'containers': ['testie']}, {'pod_name': '2-3', 'node_name': 'b', 'pod_generate_name': '2-', 'deployment_name': '2', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.1, 'containers': ['testie']}, {'pod_name': '2-4', 'node_name': 'b', 'pod_generate_name': '2-', 'deployment_name': '2', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.1, 'containers': ['testie']}, {'pod_name': '3-1', 'node_name': 'b', 'pod_generate_name': '3-', 'deployment_name': '3', 'kind': 'DaemonSet', 'namespace': 'test', 'total_requested': 0.2, 'containers': ['testie']}, {'pod_name': '4-1', 'node_name': 'c', 'pod_generate_name': '4-', 'deployment_name': '4', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.2, 'containers': ['testie']}]}}, {'a': {'cpu': 1, 'pods': [{'pod_name': '1-1', 'node_name': 'a', 'pod_generate_name': '1-', 'deployment_name': '1', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.2, 'containers': ['testie']}, {'pod_name': '1-3', 'node_name': 'a', 'pod_generate_name': '1-', 'deployment_name': '1', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.2, 'containers': ['testie']}, {'pod_name': '2-1', 'node_name': 'a', 'pod_generate_name': '2-', 'deployment_name': '2', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.1, 'containers': ['testie']}, {'pod_name': '2-2', 'node_name': 'a', 'pod_generate_name': '2-', 'deployment_name': '2', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.1, 'containers': ['testie']}, {'pod_name': '4-1', 'node_name': 'c', 'pod_generate_name': '4-', 'deployment_name': '4', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.2, 'containers': ['testie']}]}, 'b': {'cpu': 1, 'pods': [{'pod_name': '1-2', 'node_name': 'b', 'pod_generate_name': '1-', 'deployment_name': '1', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.2, 'containers': ['testie']}, {'pod_name': '2-3', 'node_name': 'b', 'pod_generate_name': '2-', 'deployment_name': '2', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.1, 'containers': ['testie']}, {'pod_name': '2-4', 'node_name': 'b', 'pod_generate_name': '2-', 'deployment_name': '2', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.1, 'containers': ['testie']}, {'pod_name': '3-1', 'node_name': 'b', 'pod_generate_name': '3-', 'deployment_name': '3', 'kind': 'DaemonSet', 'namespace': 'test', 'total_requested': 0.2, 'containers': ['testie']}, {'pod_name': '4-2', 'node_name': 'c', 'pod_generate_name': '4-', 'deployment_name': '4', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.2, 'containers': ['testie']}]}}, {'a': {'cpu': 1, 'pods': [{'pod_name': '1-1', 'node_name': 'a', 'pod_generate_name': '1-', 'deployment_name': '1', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.2, 'containers': ['testie']}, {'pod_name': '1-3', 'node_name': 'a', 'pod_generate_name': '1-', 'deployment_name': '1', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.2, 'containers': ['testie']}, {'pod_name': '2-1', 'node_name': 'a', 'pod_generate_name': '2-', 'deployment_name': '2', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.1, 'containers': ['testie']}, {'pod_name': '2-2', 'node_name': 'a', 'pod_generate_name': '2-', 'deployment_name': '2', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.1, 'containers': ['testie']}]}, 'b': {'cpu': 1, 'pods': [{'pod_name': '1-2', 'node_name': 'b', 'pod_generate_name': '1-', 'deployment_name': '1', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.2, 'containers': ['testie']}, {'pod_name': '2-3', 'node_name': 'b', 'pod_generate_name': '2-', 'deployment_name': '2', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.1, 'containers': ['testie']}, {'pod_name': '2-4', 'node_name': 'b', 'pod_generate_name': '2-', 'deployment_name': '2', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.1, 'containers': ['testie']}, {'pod_name': '3-1', 'node_name': 'b', 'pod_generate_name': '3-', 'deployment_name': '3', 'kind': 'DaemonSet', 'namespace': 'test', 'total_requested': 0.2, 'containers': ['testie']}, {'pod_name': '4-2', 'node_name': 'c', 'pod_generate_name': '4-', 'deployment_name': '4', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.2, 'containers': ['testie']}, {'pod_name': '4-1', 'node_name': 'c', 'pod_generate_name': '4-', 'deployment_name': '4', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.2, 'containers': ['testie']}]}}]
        self.selected_distribution = {'a': {'cpu': 1, 'pods': [{'pod_name': '1-1', 'node_name': 'a', 'pod_generate_name': '1-', 'deployment_name': '1', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.2, 'containers': ['testie']}, {'pod_name': '1-3', 'node_name': 'a', 'pod_generate_name': '1-', 'deployment_name': '1', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.2, 'containers': ['testie']}, {'pod_name': '2-1', 'node_name': 'a', 'pod_generate_name': '2-', 'deployment_name': '2', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.1, 'containers': ['testie']}, {'pod_name': '2-2', 'node_name': 'a', 'pod_generate_name': '2-', 'deployment_name': '2', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.1, 'containers': ['testie']}, {'pod_name': '4-2', 'node_name': 'c', 'pod_generate_name': '4-', 'deployment_name': '4', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.2, 'containers': ['testie']}]}, 'b': {'cpu': 1, 'pods': [{'pod_name': '1-2', 'node_name': 'b', 'pod_generate_name': '1-', 'deployment_name': '1', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.2, 'containers': ['testie']}, {'pod_name': '2-3', 'node_name': 'b', 'pod_generate_name': '2-', 'deployment_name': '2', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.1, 'containers': ['testie']}, {'pod_name': '2-4', 'node_name': 'b', 'pod_generate_name': '2-', 'deployment_name': '2', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.1, 'containers': ['testie']}, {'pod_name': '3-1', 'node_name': 'b', 'pod_generate_name': '3-', 'deployment_name': '3', 'kind': 'DaemonSet', 'namespace': 'test', 'total_requested': 0.2, 'containers': ['testie']}, {'pod_name': '4-1', 'node_name': 'c', 'pod_generate_name': '4-', 'deployment_name': '4', 'kind': 'ReplicaSet', 'namespace': 'test', 'total_requested': 0.2, 'containers': ['testie']}]}}
        self.result_transitions = {'c': {'add': [], 'remove': ['4-2', '4-1']}, 'a': {'add': ['4-'], 'remove': []}, 'b': {'add': ['4-'], 'remove': []}}
    def test_find_pods_to_be_rescheduled(self):
        self.assertEqual(self.reschedule_pods, find_pods_to_be_rescheduled(self.nodes["c"]["pods"]))

    def test_recursive_find_new_distributions(self):
        nodes_without_c = self.nodes
        del nodes_without_c["c"]
        result = recursive_find_new_distributions(self.reschedule_pods, nodes_without_c)
        #print(result)
        self.assertEqual(self.new_distributions, result)
        self.nodes["a"]["cpu"] = 0.7
        self.nodes["b"]["cpu"] = 0.7
        self.assertEqual([], recursive_find_new_distributions(self.reschedule_pods, nodes_without_c))

    def test_least_transitions_removable(self):
        self.assertEqual("c", least_transitions_removable(["a", "b", "c"], self.nodes))
        self.assertEqual("b", least_transitions_removable(["a", "b"], self.nodes))

    def test_select_lowest_max_requested(self):
        result = select_lowest_max_requested(self.new_distributions)
        #print(result)
        self.assertEqual(self.selected_distribution, result)

    def test_change_selected_distribution_into_transitions(self):
        result = change_selected_distribution_into_transitions(self.selected_distribution, self.nodes)
        self.assertEqual(self.result_transitions, result)


