import unittest

from kubernetes_tools.delete_pod import delete_pod_deployment


class TestDeletePod(unittest.TestCase):
    def test_delete_pod_deployment(self):
        pod_name = "php-apache-85546b856f-gbm46"
        deployment_name = "php-apache"
        namespace = "demo"
        delete_pod_deployment(pod_name, deployment_name, namespace)
