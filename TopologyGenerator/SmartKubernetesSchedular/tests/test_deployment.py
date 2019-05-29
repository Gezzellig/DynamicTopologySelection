import unittest

from SmartKubernetesSchedular.deployment import verify_deployment, find_migrations, extract_deployment, \
    simulate_migration, recursive_construction_migration_order, find_all_migrations_sets, \
    remove_non_migrated_remove_pods, find_suitable_migrations, scale_actions


class TestEnforcer(unittest.TestCase):

    def setUp(self):
        self.nodes = {
            "a": {"cpu": 0.5},
            "b": {"cpu": 0.5},
            "c": {"cpu": 0.5}
        }
        self.pods = {
            "1-1": {
                "node_name": "a",
                "pod_generate_name": "1",
                "namespace": "test",
                "total_requested": 0.2,
                "containers": ["testie"]
            },
            "1-2": {
                "node_name": "a",
                "pod_generate_name": "1",
                "namespace": "test",
                "total_requested": 0.2,
                "containers": ["testie"]
            },
            "2-1": {
                "node_name": "b",
                "pod_generate_name": "2",
                "namespace": "test",
                "total_requested": 0.2,
                "containers": ["testie"]
            }
        }
        self.cur_deployment = {
            "a": ["1-1", "1-2"],
            "b": ["2-1"],
            "c": []
        }
        self.goal_deployment = {
            "a": ["1-1", "2-1"],
            "b": [],
            "c": ["1-2"]
        }
        self.migrations = [
            {'pod_name': '2-1', 'source': 'b', 'destination': 'a'},
            {'pod_name': '1-2', 'source': 'a', 'destination': 'c'}
        ]

        self.nodes2 = {
            "d": {"cpu": 0.9},
            "e": {"cpu": 0.5},
            "f": {"cpu": 0.5}
        }
        self.pods2 = {
            "1-1": {
                "node_name": "d",
                "pod_generate_name": "1-",
                "deployment_name": "1",
                "namespace": "test",
                "total_requested": 0.2,
                "containers": ["testie"]
            },
            "2-1": {
                "node_name": "d",
                "pod_generate_name": "2-",
                "deployment_name": "2",
                "namespace": "test",
                "total_requested": 0.2,
                "containers": ["testie"]
            },
            "1-3": {
                "node_name": "e",
                "pod_generate_name": "1-",
                "deployment_name": "1",
                "namespace": "test",
                "total_requested": 0.2,
                "containers": ["testie"]
            },
            "3-2": {
                "node_name": "e",
                "pod_generate_name": "3-",
                "deployment_name": "3",
                "namespace": "test",
                "total_requested": 0.2,
                "containers": ["testie"]
            },
            "1-2": {
                "node_name": "f",
                "pod_generate_name": "1-",
                "deployment_name": "1",
                "namespace": "test",
                "total_requested": 0.2,
                "containers": ["testie"]
            },
            "3-1": {
                "node_name": "f",
                "pod_generate_name": "3-",
                "deployment_name": "3",
                "namespace": "test",
                "total_requested": 0.2,
                "containers": ["testie"]
            },
        }

        self.cur_deployment2 = {
            "d": ["1-1", "2-1"],
            "e": ["1-3", "3-2"],
            "f": ["1-2", "3-1"]
        }
        self.transitions2 = {
            "d": {
                "add": ["1-", "1-", "3-"],
                "remove": ["2-1"]
            },
            "e": {
                "add": ["2-"],
                "remove": ["3-2"]
            },
            "f": {
                "add": [],
                "remove": ["1-2", "3-1"]
            }
        }

    def test_verify_deployment(self):
        self.assertTrue(verify_deployment(self.cur_deployment, self.pods, self.nodes))
        pods = self.pods
        pods["2-2"] = {
            "node_name": "a",
            "pod_generate_name": "2",
            "namespace": "test",
            "total_requested": 0.4,
            "containers": ["testie"]
        }
        cur_deployment = self.cur_deployment
        cur_deployment["b"].append("2-2")
        self.assertFalse(verify_deployment(cur_deployment, pods, self.nodes))

    def test_find_migrations(self):
        self.assertEqual(self.migrations, find_migrations(self.cur_deployment, self.goal_deployment))

    def test_extract_deployment(self):
        self.assertEqual(self.cur_deployment, extract_deployment(self.pods, self.nodes))

    def test_simulate_migration(self):
        compare = {'a': ['1-1', '1-2', '2-1'], 'b': [], 'c': []}
        res_deployment = simulate_migration(self.cur_deployment, self.migrations[0])
        self.assertEqual(compare, res_deployment)
        res_deployment = simulate_migration(self.cur_deployment, self.migrations[1])
        self.assertEqual(self.goal_deployment, res_deployment)

    def test_recursive_construction(self):
        result, steps = recursive_construction_migration_order([], self.cur_deployment, self.pods, self.nodes)
        self.assertTrue(result)
        self.assertEqual([], steps)
        result, steps = recursive_construction_migration_order([self.migrations[0]], self.cur_deployment, self.pods, self.nodes)
        self.assertFalse(result)
        self.assertEqual([], steps)
        result, steps = recursive_construction_migration_order([self.migrations[1]], self.cur_deployment, self.pods, self.nodes)
        self.assertTrue(result)
        self.assertEqual([self.migrations[1]], steps)
        result, steps = recursive_construction_migration_order(self.migrations, self.cur_deployment, self.pods, self.nodes)
        solution_migration = [{'pod_name': '1-2', 'source': 'a', 'destination': 'c'}, {'pod_name': '2-1', 'source': 'b', 'destination': 'a'}]
        self.assertTrue(result)
        self.assertEqual(solution_migration, steps)
        migrations = {'pod_name': '3-2', 'source': 'e', 'destination': 'f'}, {'pod_name': '1-2', 'source': 'f', 'destination': 'e'}
        print(recursive_construction_migration_order(migrations, self.cur_deployment2, self.pods2, self.nodes2))

    def test_find_all_migration_sets(self):
        empty_transitions = {
            "d": {
                "add": [],
                "remove": ["2-1"]
            },
            "e": {
                "add": [],
                "remove": ["3-2"]
            },
            "f": {
                "add": [],
                "remove": ["1-2", "3-1"]
            }
        }

        self.assertEqual([[]], find_all_migrations_sets(empty_transitions))
        small_transitions = {
            "d": {
                "add": ["3-"],
                "remove": ["2-1"]
            },
            "e": {
                "add": [],
                "remove": ["3-2"]
            },
            "f": {
                "add": [],
                "remove": ["1-2", "3-1"]
            }
        }
        self.assertEqual([[{'pod_name': '3-2', 'source': 'e', 'destination': 'd'}], [{'pod_name': '3-1', 'source': 'f', 'destination': 'd'}], []], find_all_migrations_sets(small_transitions))
        small_transitions = {
            "d": {
                "add": ["3-", "3-"],
                "remove": ["2-1"]
            },
            "e": {
                "add": [],
                "remove": ["3-2"]
            },
            "f": {
                "add": [],
                "remove": ["1-2"]
            }
        }
        self.assertEqual([[{'pod_name': '3-2', 'source': 'e', 'destination': 'd'}], [{'pod_name': '3-2', 'source': 'e', 'destination': 'd'}], []], find_all_migrations_sets(small_transitions))
        small_transitions = {
            "d": {
                "add": ["3-"],
                "remove": ["2-1"]
            },
            "e": {
                "add": ["1-"],
                "remove": ["3-2"]
            },
            "f": {
                "add": [],
                "remove": ["1-2", "3-1"]
            }
        }
        self.assertEqual([[{'pod_name': '1-2', 'source': 'f', 'destination': 'e'}, {'pod_name': '3-2', 'source': 'e', 'destination': 'd'}], [{'pod_name': '3-2', 'source': 'e', 'destination': 'd'}], [{'pod_name': '1-2', 'source': 'f', 'destination': 'e'}, {'pod_name': '3-1', 'source': 'f', 'destination': 'd'}], [{'pod_name': '3-1', 'source': 'f', 'destination': 'd'}], [{'pod_name': '1-2', 'source': 'f', 'destination': 'e'}], []], find_all_migrations_sets(small_transitions))

    def test_remove_non_migrated_remove_pods(self):
        migration_set = [{'pod_name': '1-2', 'source': 'f', 'destination': 'e'}, {'pod_name': '3-2', 'source': 'e', 'destination': 'd'}]
        self.assertEqual({'1-1': {'node_name': 'd', 'pod_generate_name': '1-', 'namespace': 'test', 'total_requested': 0.2, 'containers': ['testie']}, '1-3': {'node_name': 'e', 'pod_generate_name': '1-', 'namespace': 'test', 'total_requested': 0.2, 'containers': ['testie']}, '3-2': {'node_name': 'e', 'pod_generate_name': '3-', 'namespace': 'test', 'total_requested': 0.2, 'containers': ['testie']}, '1-2': {'node_name': 'f', 'pod_generate_name': '1-', 'namespace': 'test', 'total_requested': 0.2, 'containers': ['testie']}}, remove_non_migrated_remove_pods(self.transitions2, migration_set, self.pods2))

    def test_find_suitable_migrations(self):
        small_transitions = {
            "d": {
                "add": [],
                "remove": []
            },
            "e": {
                "add": ["1-"],
                "remove": ["3-2"]
            },
            "f": {
                "add": ["3-"],
                "remove": ["1-2"]
            }
        }
        migration_sets = find_all_migrations_sets(small_transitions)
        print(migration_sets)
        self.assertEqual([{'pod_name': '1-2', 'source': 'f', 'destination': 'e'}], find_suitable_migrations(small_transitions, migration_sets, self.pods2, self.nodes2))

    def test_scale_actions(self):
        small_transitions = {
            "d": {
                "add": [],
                "remove": []
            },
            "e": {
                "add": ["1-"],
                "remove": ["3-2"]
            },
            "f": {
                "add": ["3-"],
                "remove": ["1-2"]
            }
        }
        migration_orders = []
        downscalers, upscalers = scale_actions(small_transitions, migration_orders, self.pods2)
        self.assertEqual([{'pod_name': '3-2', 'pod_generate_name': '3-', 'deployment_name': '3', 'namespace': 'test'}, {'pod_name': '1-2', 'pod_generate_name': '1-', 'deployment_name': '1', 'namespace': 'test'}], downscalers)
        self.assertEqual([{'node_name': 'e', 'pod_generate_name': '1-', 'deployment_name': "1", 'namespace': "test"}, {'node_name': 'f', 'pod_generate_name': '3-', 'deployment_name': "3", 'namespace': "test"}], upscalers)
        migration_orders = [{'pod_name': '3-2', 'source': 'e', 'destination': 'f'}, {'pod_name': '1-2', 'source': 'f', 'destination': 'e'}]
        downscalers, upscalers = scale_actions(small_transitions, migration_orders, self.pods2)
        self.assertEqual([], downscalers)
        self.assertEqual([], upscalers)
        migration_orders = [{'pod_name': '3-2', 'source': 'e', 'destination': 'f'}]
        downscalers, upscalers = scale_actions(small_transitions, migration_orders, self.pods2)
        self.assertEqual([{'pod_name': '1-2', 'pod_generate_name': '1-', 'deployment_name': '1', 'namespace': 'test'}], downscalers)
        self.assertEqual([{'node_name': 'e', 'pod_generate_name': '1-', 'deployment_name': '1', 'namespace': 'test'}], upscalers)