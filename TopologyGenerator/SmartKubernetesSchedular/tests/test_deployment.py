import unittest

from SmartKubernetesSchedular.deployment import verify_deployment, find_migrations, extract_deployment, \
    simulate_migration, helper_recursive_construction, recursive_construction


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
        result, steps = recursive_construction([], self.cur_deployment, self.pods, self.nodes)
        self.assertTrue(result)
        self.assertEqual([], steps)
        result, steps = recursive_construction([self.migrations[0]], self.cur_deployment, self.pods, self.nodes)
        self.assertFalse(result)
        self.assertEqual([], steps)
        result, steps = recursive_construction([self.migrations[1]], self.cur_deployment, self.pods, self.nodes)
        self.assertTrue(result)
        self.assertEqual([self.migrations[1]], steps)
        result, steps = recursive_construction(self.migrations, self.cur_deployment, self.pods, self.nodes)
        solution_migration = [{'pod_name': '1-2', 'source': 'a', 'destination': 'c'}, {'pod_name': '2-1', 'source': 'b', 'destination': 'a'}]
        self.assertTrue(result)
        self.assertEqual(solution_migration, steps)






