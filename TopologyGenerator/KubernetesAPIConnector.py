import os

from kubernetes import config, client


class KubernetesAPIConnector:
    class __KubernetesAPIConnector:
        def __init__(self):
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.abspath('/media/thijs/SSD2/University/2018-2019/Thesis/re-kube-2c9b18fda5f3.json')
            config.load_kube_config()
            self.k8s_client = client

    instance = None

    def __init__(self):
        if not KubernetesAPIConnector.instance:
            KubernetesAPIConnector.instance = KubernetesAPIConnector.__KubernetesAPIConnector()


def get_k8s_client():
    return KubernetesAPIConnector().instance.k8s_client


def get_k8s_api():
    return KubernetesAPIConnector().instance.k8s_client.CoreV1Api()

