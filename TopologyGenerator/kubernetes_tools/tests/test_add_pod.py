import unittest

from kubernetes_tools.add_pod import add_pod_deployment


class TestAddPod(unittest.TestCase):
    def test_add_pod_deployment(self):
        destination_node = "gke-develop-cluster-larger-pool-9ecdadbf-dlkp"
        deployment_name = "php-apache"
        namespace = "demo"
        add_pod_deployment(destination_node, deployment_name, namespace)
