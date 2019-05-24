from kubernetes import config, client


class KubernetesAPIConnector:
    class __KubernetesAPIConnector:
        def __init__(self):
            config.load_kube_config()
            self.k8s_api = client.CoreV1Api()

    instance = None

    def __init__(self):
        if not KubernetesAPIConnector.instance:
            KubernetesAPIConnector.instance = KubernetesAPIConnector.__KubernetesAPIConnector()


def get_k8s_api():
    return KubernetesAPIConnector().instance.k8s_api
