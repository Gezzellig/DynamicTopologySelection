import unittest

from kubernetes_tools.migrate_pod import migrate_pod


class TestMigratePod(unittest.TestCase):
    def test_delete_pod_deployment(self):
        destination_node = "gke-develop-cluster-larger-pool-9ecdadbf-w9bw"
        pod_name = "php-apache-85546b856f-2cl9s"
        namespace = "demo"
        migrate_pod(destination_node, pod_name, namespace)
