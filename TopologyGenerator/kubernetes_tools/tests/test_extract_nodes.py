import unittest

from kubernetes_tools.extract_nodes import node_request_fits, node_sum_requested


class TestExtractNodes(unittest.TestCase):
    def setUp(self):
        self.node_true = {
            "cpu": 1,
            "pods": [
                {
                    "pod_name": "1-1",
                    "node_name": "d",
                    "pod_generate_name": "2-",
                    "deployment_name": "2",
                    "namespace": "test",
                    "total_requested": 0.2,
                    "containers": ["testie"]
                },
                {
                    "pod_name": "2-1",
                    "node_name": "d",
                    "pod_generate_name": "2-",
                    "deployment_name": "2",
                    "namespace": "test",
                    "total_requested": 0.2,
                    "containers": ["testie"]
                },
                {
                    "pod_name": "2-2",
                    "node_name": "d",
                    "pod_generate_name": "2-",
                    "deployment_name": "2",
                    "namespace": "test",
                    "total_requested": 0.2,
                    "containers": ["testie"]
                }
            ]
        }
        self.node_false = {
            "cpu": 0.7,
            "pods": [
                {
                    "pod_name": "1-1",
                    "node_name": "d",
                    "pod_generate_name": "2-",
                    "deployment_name": "2",
                    "namespace": "test",
                    "total_requested": 0.2,
                    "containers": ["testie"]
                },
                {
                    "pod_name": "2-1",
                    "node_name": "d",
                    "pod_generate_name": "2-",
                    "deployment_name": "2",
                    "namespace": "test",
                    "total_requested": 0.2,
                    "containers": ["testie"]
                },
                {
                    "pod_name": "2-2",
                    "node_name": "d",
                    "pod_generate_name": "2-",
                    "deployment_name": "2",
                    "namespace": "test",
                    "total_requested": 0.2,
                    "containers": ["testie"]
                }
                ,
                {
                    "pod_name": "3-1",
                    "node_name": "d",
                    "pod_generate_name": "2-",
                    "deployment_name": "2",
                    "namespace": "test",
                    "total_requested": 0.15,
                    "containers": ["testie"]
                }
            ]
        }

    def test_node_sum_requested(self):
        self.assertAlmostEqual(0.6, node_sum_requested(self.node_true), 5)
        self.assertAlmostEqual(0.75, node_sum_requested(self.node_false), 5)

    def test_node_request_fits(self):
        self.assertTrue(node_request_fits(self.node_true))
        self.assertFalse(node_request_fits(self.node_false))
