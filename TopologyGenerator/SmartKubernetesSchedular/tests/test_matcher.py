import unittest

from SmartKubernetesSchedular.matcher import calc_score_per_node, get_scores, find_highest_score_mapping, \
    find_transitions_execution_change


class TestEnforcer(unittest.TestCase):
    def setUp(self):
        self.current_state = {
            "d": {"cpu": 0.9,
                  "memory": 2.0,
                  "pods": {
                    "1-1": {
                            "node_name": "d",
                            "pod_generate_name": "1-",
                            "deployment_name": "1",
                            "kind": "StatefulSet",
                            "namespace": "test",
                            "total_requested": 0.2,
                            "containers": ["testie"]
                        },
                    "2-1": {
                            "node_name": "d",
                            "pod_generate_name": "2-",
                            "deployment_name": "2",
                            "kind": None,
                            "namespace": "test",
                            "total_requested": 0.2,
                            "containers": ["testie"]
                        }
                    }
                  },
            "e": {"cpu": 0.5,
                  "memory": 2.0,
                  "pods": {
                        "1-3": {
                            "node_name": "e",
                            "pod_generate_name": "1-",
                            "deployment_name": "1",
                            "kind": "StatefulSet",
                            "namespace": "test",
                            "total_requested": 0.2,
                            "containers": ["testie"]
                        },
                        "3-2": {
                            "node_name": "e",
                            "pod_generate_name": "3-",
                            "deployment_name": "3",
                            "kind": "ReplicaSet",
                            "namespace": "test",
                            "total_requested": 0.2,
                            "containers": ["testie"]
                        }
                    }
                  },
            "f": {"cpu": 0.5,
                  "memory": 2.0,
                  "pods": {
                        "1-2": {
                            "node_name": "f",
                            "pod_generate_name": "1-",
                            "deployment_name": "1",
                            "kind": "StatefulSet",
                            "namespace": "test",
                            "total_requested": 0.2,
                            "containers": ["testie"]
                        },
                        "3-1": {
                            "node_name": "f",
                            "pod_generate_name": "3-",
                            "deployment_name": "3",
                            "kind": "ReplicaSet",
                            "namespace": "test",
                            "total_requested": 0.2,
                            "containers": ["testie"]
                        }
                    }
                  },
            "g": {"cpu": 0.5,
                  "memory": 2.0,
                  "pods": {

                  }
                }
        }
        self.desired_state = {
            "d": {"cpu": 0.9,
                  "memory": 2.0,
                  "pods": {
                      "1-1": {
                          "node_name": "d",
                          "pod_generate_name": "1-",
                          "deployment_name": "1",
                          "kind": "StatefulSet",
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      },
                      "2-1": {
                          "node_name": "d",
                          "pod_generate_name": "2-",
                          "deployment_name": "2",
                          "kind": None,
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      },
                      "3-2": {
                          "node_name": "e",
                          "pod_generate_name": "3-",
                          "deployment_name": "3",
                          "kind": "ReplicaSet",
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      }
                  }
                  },
            "e": {"cpu": 0.5,
                  "memory": 2.0,
                  "pods": {
                      "1-3": {
                          "node_name": "e",
                          "pod_generate_name": "1-",
                          "deployment_name": "1",
                          "kind": "StatefulSet",
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      }
                    }
                  },
            "f": {"cpu": 0.5,
                  "memory": 2.0,
                  "pods": {
                      "1-2": {
                          "node_name": "f",
                          "pod_generate_name": "1-",
                          "deployment_name": "1",
                          "kind": "StatefulSet",
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      },
                      "3-1": {
                          "node_name": "f",
                          "pod_generate_name": "3-",
                          "deployment_name": "3",
                          "kind": "ReplicaSet",
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      }
                    }
                },
        }
        self.scores = {'d': {'d': 99, 'e': 101, 'f': 101, 'g': -101}, 'e': {'d': 100, 'e': 99, 'f': 99, 'g': -100}, 'f': {'d': 99, 'e': 101, 'f': 101, 'g': -101}}
        self.transitions = {'d': {'add': ['2-'], 'remove': []}, 'e': {'add': [], 'remove': ['2-1']}, 'f': {'add': [], 'remove': []}}
        self.current_state_b = {
            "d": {"cpu": 0.9,
                  "memory": 2.0,
                  "pods": {
                      "1-1": {
                          "node_name": "d",
                          "pod_generate_name": "1-",
                          "deployment_name": "1",
                          "kind": "ReplicaSet",
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      },
                      "2-1": {
                          "node_name": "d",
                          "pod_generate_name": "2-",
                          "deployment_name": "2",
                          "kind": "StatefulSet",
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      }
                  }
                  },
            "e": {"cpu": 0.5,
                  "memory": 2.0,
                  "pods": {
                      "1-3": {
                          "node_name": "e",
                          "pod_generate_name": "1-",
                          "deployment_name": "1",
                          "kind": "ReplicaSet",
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      },
                      "3-2": {
                          "node_name": "e",
                          "pod_generate_name": "3-",
                          "deployment_name": "3",
                          "kind": "ReplicaSet",
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      }
                  }
                  },
            "f": {"cpu": 0.5,
                  "memory": 2.0,
                  "pods": {
                      "1-2": {
                          "node_name": "f",
                          "pod_generate_name": "1-",
                          "deployment_name": "1",
                          "kind": "ReplicaSet",
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      },
                      "3-1": {
                          "node_name": "f",
                          "pod_generate_name": "3-",
                          "deployment_name": "3",
                          "kind": "ReplicaSet",
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      }
                  }
                  },
            "g": {"cpu": 0.5,
                  "memory": 2.0,
                  "pods": {

                  }
                  }
        }
        self.desired_state_b = {
            "d": {"cpu": 0.9,
                  "memory": 2.0,
                  "pods": {
                      "1-1": {
                          "node_name": "d",
                          "pod_generate_name": "1-",
                          "deployment_name": "1",
                          "kind": "ReplicaSet",
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      },
                      "2-1": {
                          "node_name": "d",
                          "pod_generate_name": "2-",
                          "deployment_name": "2",
                          "kind": "StatefulSet",
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      },
                      "3-2": {
                          "node_name": "e",
                          "pod_generate_name": "3-",
                          "deployment_name": "3",
                          "kind": "ReplicaSet",
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      }
                  }
                  },
            "e": {"cpu": 0.5,
                  "memory": 2.0,
                  "pods": {
                      "1-3": {
                          "node_name": "e",
                          "pod_generate_name": "1-",
                          "deployment_name": "1",
                          "kind": "ReplicaSet",
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      }
                  }
                  },
            "f": {"cpu": 0.5,
                  "memory": 2.0,
                  "pods": {
                      "1-2": {
                          "node_name": "f",
                          "pod_generate_name": "1-",
                          "deployment_name": "1",
                          "kind": "ReplicaSet",
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      },
                      "3-1": {
                          "node_name": "f",
                          "pod_generate_name": "3-",
                          "deployment_name": "3",
                          "kind": "ReplicaSet",
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      }
                  }
                  },
        }
        self.scores_b = {'d': {'d': 100, 'e': -98, 'f': -98, 'g': -102}, 'e': {'d': -99, 'e': 0, 'f': 0, 'g': -1}, 'f': {'d': -100, 'e': 2, 'f': 2, 'g': -2}}
        self.transitions_b = {'d': {'add': ['3-'], 'remove': []}, 'e': {'add': [], 'remove': ['3-1']}, 'f': {'add': [], 'remove': []}}
    def test_calc_score_per_node(self):
        self.assertEqual(100, calc_score_per_node(self.current_state["d"], self.current_state["d"]))
        self.assertEqual(101, calc_score_per_node(self.current_state["e"], self.current_state["e"]))
        self.assertEqual(99, calc_score_per_node(self.current_state["d"], self.desired_state["d"]))
        self.assertEqual(100, calc_score_per_node(self.current_state["d"], self.desired_state["e"]))
        self.assertEqual(-101, calc_score_per_node(self.current_state["e"], self.current_state["g"]))

    def test_get_scores(self):
        self.assertEqual(self.scores, get_scores(self.current_state, self.desired_state))
        self.assertEqual(self.scores_b, get_scores(self.current_state_b, self.desired_state_b))

    def test_find_highest_score_mapping(self):
        self.assertEqual({'d': 'f', 'e': 'd', 'f': 'e'}, find_highest_score_mapping(self.scores))
        self.assertEqual({'d': 'd', 'e': 'f', 'f': 'e'}, find_highest_score_mapping(self.scores_b))

    def test_find_transitions_execution_change(self):
        #self.assertEqual(self.transitions, find_transitions_execution_change(self.current_state, self.desired_state))
        #self.assertEqual(self.transitions_b, find_transitions_execution_change(self.current_state_b, self.desired_state_b))
        current_state = {'gke-demo-cluster-1-default-pool-6f471531-6t13': {'cpu': 2.0, 'memory': 7.303501129150391, 'pods': {'fluentd-gcp-v3.2.0-tjrkc': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-6t13', 'namespace': 'kube-system', 'total_requested': 0.1, 'containers': ['fluentd-gcp', 'prometheus-to-sd-exporter'], 'pod_generate_name': 'fluentd-gcp-v3.2.0-', 'kind': 'DaemonSet', 'deployment_name': None}, 'kube-proxy-gke-demo-cluster-1-default-pool-6f471531-6t13': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-6t13', 'namespace': 'kube-system', 'total_requested': 0.1, 'containers': ['kube-proxy'], 'pod_generate_name': 'kube-proxy-gke-demo-cluster-1-default-pool-6f471531-', 'kind': 'DaemonSet', 'deployment_name': None}, 'prometheus-to-sd-8dckb': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-6t13', 'namespace': 'kube-system', 'total_requested': 0.001, 'containers': ['prometheus-to-sd'], 'pod_generate_name': 'prometheus-to-sd-', 'kind': 'DaemonSet', 'deployment_name': None}, 'prometheus-1-node-exporter-k6p6q': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-6t13', 'namespace': 'monitoring', 'total_requested': 0.01, 'containers': ['prometheus-node-exporter'], 'pod_generate_name': 'prometheus-1-node-exporter-', 'kind': 'DaemonSet', 'deployment_name': None}}}, 'gke-demo-cluster-1-default-pool-6f471531-b933': {'cpu': 2.0, 'memory': 7.303501129150391, 'pods': {'php-apache-5f657688bc-4zrbn': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-b933', 'namespace': 'demo', 'total_requested': 0.2, 'containers': ['php-apache'], 'pod_generate_name': 'php-apache-5f657688bc-', 'kind': 'ReplicaSet', 'deployment_name': 'php-apache'}, 'php-apache-5f657688bc-mzlb2': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-b933', 'namespace': 'demo', 'total_requested': 0.2, 'containers': ['php-apache'], 'pod_generate_name': 'php-apache-5f657688bc-', 'kind': 'ReplicaSet', 'deployment_name': 'php-apache'}, 'php-apache-5f657688bc-nddvx': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-b933', 'namespace': 'demo', 'total_requested': 0.2, 'containers': ['php-apache'], 'pod_generate_name': 'php-apache-5f657688bc-', 'kind': 'ReplicaSet', 'deployment_name': 'php-apache'}, 'fluentd-gcp-v3.2.0-8qdm6': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-b933', 'namespace': 'kube-system', 'total_requested': 0.1, 'containers': ['fluentd-gcp', 'prometheus-to-sd-exporter'], 'pod_generate_name': 'fluentd-gcp-v3.2.0-', 'kind': 'DaemonSet', 'deployment_name': None}, 'heapster-v1.6.0-beta.1-66f866bd4f-dz28z': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-b933', 'namespace': 'kube-system', 'total_requested': 0.063, 'containers': ['heapster', 'prom-to-sd', 'heapster-nanny'], 'pod_generate_name': 'heapster-v1.6.0-beta.1-66f866bd4f-', 'kind': 'ReplicaSet', 'deployment_name': None}, 'kube-dns-autoscaler-76fcd5f658-9f9mq': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-b933', 'namespace': 'kube-system', 'total_requested': 0.02, 'containers': ['autoscaler'], 'pod_generate_name': 'kube-dns-autoscaler-76fcd5f658-', 'kind': 'ReplicaSet', 'deployment_name': None}, 'kube-dns-b46cc9485-4lv6h': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-b933', 'namespace': 'kube-system', 'total_requested': 0.26, 'containers': ['kubedns', 'dnsmasq', 'sidecar', 'prometheus-to-sd'], 'pod_generate_name': 'kube-dns-b46cc9485-', 'kind': 'ReplicaSet', 'deployment_name': None}, 'kube-proxy-gke-demo-cluster-1-default-pool-6f471531-b933': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-b933', 'namespace': 'kube-system', 'total_requested': 0.1, 'containers': ['kube-proxy'], 'pod_generate_name': 'kube-proxy-gke-demo-cluster-1-default-pool-6f471531-', 'kind': 'DaemonSet', 'deployment_name': None}, 'metrics-server-v0.3.1-5b4d6d8d98-fx78m': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-b933', 'namespace': 'kube-system', 'total_requested': 0.047999999999999994, 'containers': ['metrics-server', 'metrics-server-nanny'], 'pod_generate_name': 'metrics-server-v0.3.1-5b4d6d8d98-', 'kind': 'ReplicaSet', 'deployment_name': None}, 'prometheus-to-sd-z6x4m': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-b933', 'namespace': 'kube-system', 'total_requested': 0.001, 'containers': ['prometheus-to-sd'], 'pod_generate_name': 'prometheus-to-sd-', 'kind': 'DaemonSet', 'deployment_name': None}, 'prometheus-1-alertmanager-1': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-b933', 'namespace': 'monitoring', 'total_requested': 0.01, 'containers': ['prometheus-alertmanager'], 'pod_generate_name': 'prometheus-1-alertmanager-', 'kind': 'StatefulSet', 'deployment_name': None}, 'prometheus-1-node-exporter-fmq4v': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-b933', 'namespace': 'monitoring', 'total_requested': 0.01, 'containers': ['prometheus-node-exporter'], 'pod_generate_name': 'prometheus-1-node-exporter-', 'kind': 'DaemonSet', 'deployment_name': None}, 'prometheus-1-prometheus-0': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-b933', 'namespace': 'monitoring', 'total_requested': 0.2, 'containers': ['prometheus-server'], 'pod_generate_name': 'prometheus-1-prometheus-', 'kind': 'StatefulSet', 'deployment_name': None}}}, 'gke-demo-cluster-1-default-pool-6f471531-k0kc': {'cpu': 2.0, 'memory': 7.303501129150391, 'pods': {'application-controller-manager-0': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'namespace': 'application-system', 'total_requested': 0.1, 'containers': ['manager'], 'pod_generate_name': 'application-controller-manager-', 'kind': 'StatefulSet', 'deployment_name': None}, 'php-apache-5f657688bc-fnjlp': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'namespace': 'demo', 'total_requested': 0.2, 'containers': ['php-apache'], 'pod_generate_name': 'php-apache-5f657688bc-', 'kind': 'ReplicaSet', 'deployment_name': 'php-apache'}, 'event-exporter-v0.2.4-5f7d5d7dd4-qhqmw': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'namespace': 'kube-system', 'total_requested': 0.0, 'containers': ['event-exporter', 'prometheus-to-sd-exporter'], 'pod_generate_name': 'event-exporter-v0.2.4-5f7d5d7dd4-', 'kind': 'ReplicaSet', 'deployment_name': None}, 'fluentd-gcp-scaler-7b895cbc89-5pc89': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'namespace': 'kube-system', 'total_requested': 0.0, 'containers': ['fluentd-gcp-scaler'], 'pod_generate_name': 'fluentd-gcp-scaler-7b895cbc89-', 'kind': 'ReplicaSet', 'deployment_name': None}, 'fluentd-gcp-v3.2.0-sx5vm': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'namespace': 'kube-system', 'total_requested': 0.1, 'containers': ['fluentd-gcp', 'prometheus-to-sd-exporter'], 'pod_generate_name': 'fluentd-gcp-v3.2.0-', 'kind': 'DaemonSet', 'deployment_name': None}, 'kube-dns-b46cc9485-q6m76': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'namespace': 'kube-system', 'total_requested': 0.26, 'containers': ['kubedns', 'dnsmasq', 'sidecar', 'prometheus-to-sd'], 'pod_generate_name': 'kube-dns-b46cc9485-', 'kind': 'ReplicaSet', 'deployment_name': None}, 'kube-proxy-gke-demo-cluster-1-default-pool-6f471531-k0kc': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'namespace': 'kube-system', 'total_requested': 0.1, 'containers': ['kube-proxy'], 'pod_generate_name': 'kube-proxy-gke-demo-cluster-1-default-pool-6f471531-', 'kind': 'DaemonSet', 'deployment_name': None}, 'l7-default-backend-6f8697844f-8vgxb': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'namespace': 'kube-system', 'total_requested': 0.01, 'containers': ['default-http-backend'], 'pod_generate_name': 'l7-default-backend-6f8697844f-', 'kind': 'ReplicaSet', 'deployment_name': None}, 'prometheus-to-sd-lpmzg': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'namespace': 'kube-system', 'total_requested': 0.001, 'containers': ['prometheus-to-sd'], 'pod_generate_name': 'prometheus-to-sd-', 'kind': 'DaemonSet', 'deployment_name': None}, 'prometheus-1-alertmanager-0': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'namespace': 'monitoring', 'total_requested': 0.01, 'containers': ['prometheus-alertmanager'], 'pod_generate_name': 'prometheus-1-alertmanager-', 'kind': 'StatefulSet', 'deployment_name': None}, 'prometheus-1-grafana-0': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'namespace': 'monitoring', 'total_requested': 0.05, 'containers': ['grafana'], 'pod_generate_name': 'prometheus-1-grafana-', 'kind': 'StatefulSet', 'deployment_name': None}, 'prometheus-1-kube-state-metrics-66cfd5684-555zl': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'namespace': 'monitoring', 'total_requested': 0.1, 'containers': ['kube-state-metrics', 'addon-resizer'], 'pod_generate_name': 'prometheus-1-kube-state-metrics-66cfd5684-', 'kind': 'ReplicaSet', 'deployment_name': None}, 'prometheus-1-node-exporter-8df9p': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'namespace': 'monitoring', 'total_requested': 0.01, 'containers': ['prometheus-node-exporter'], 'pod_generate_name': 'prometheus-1-node-exporter-', 'kind': 'DaemonSet', 'deployment_name': None}, 'prometheus-1-prometheus-1': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-k0kc', 'namespace': 'monitoring', 'total_requested': 0.2, 'containers': ['prometheus-server'], 'pod_generate_name': 'prometheus-1-prometheus-', 'kind': 'StatefulSet', 'deployment_name': None}}}, 'gke-demo-cluster-1-default-pool-6f471531-m4rj': {'cpu': 2.0, 'memory': 7.303501129150391, 'pods': {'php-apache-5f657688bc-tntcn': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-m4rj', 'namespace': 'demo', 'total_requested': 0.2, 'containers': ['php-apache'], 'pod_generate_name': 'php-apache-5f657688bc-', 'kind': 'ReplicaSet', 'deployment_name': 'php-apache'}, 'fluentd-gcp-v3.2.0-vbhbk': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-m4rj', 'namespace': 'kube-system', 'total_requested': 0.1, 'containers': ['fluentd-gcp', 'prometheus-to-sd-exporter'], 'pod_generate_name': 'fluentd-gcp-v3.2.0-', 'kind': 'DaemonSet', 'deployment_name': None}, 'kube-proxy-gke-demo-cluster-1-default-pool-6f471531-m4rj': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-m4rj', 'namespace': 'kube-system', 'total_requested': 0.1, 'containers': ['kube-proxy'], 'pod_generate_name': 'kube-proxy-gke-demo-cluster-1-default-pool-6f471531-', 'kind': 'DaemonSet', 'deployment_name': None}, 'prometheus-to-sd-njgpd': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-m4rj', 'namespace': 'kube-system', 'total_requested': 0.001, 'containers': ['prometheus-to-sd'], 'pod_generate_name': 'prometheus-to-sd-', 'kind': 'DaemonSet', 'deployment_name': None}, 'prometheus-1-node-exporter-jsbdb': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-m4rj', 'namespace': 'monitoring', 'total_requested': 0.01, 'containers': ['prometheus-node-exporter'], 'pod_generate_name': 'prometheus-1-node-exporter-', 'kind': 'DaemonSet', 'deployment_name': None}}}}
        desired_state = {'gke-demo-cluster-1-default-pool-6f471531-nk90': {'cpu': 2.0, 'memory': 7.303493499755859, 'pods': {'kube-dns-b46cc9485-kqgbm': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-nk90', 'pod_generate_name': 'kube-dns-b46cc9485-', 'kind': 'ReplicaSet'}, 'php-apache-5f657688bc-2lz9f': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-nk90', 'pod_generate_name': 'php-apache-5f657688bc-', 'kind': 'ReplicaSet'}, 'heapster-v1.6.0-beta.1-66f866bd4f-4x62z': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-nk90', 'pod_generate_name': 'heapster-v1.6.0-beta.1-66f866bd4f-', 'kind': 'ReplicaSet'}, 'prometheus-1-prometheus-0': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-nk90', 'pod_generate_name': 'prometheus-1-prometheus-', 'kind': 'StatefulSet'}, 'application-controller-manager-0': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-nk90', 'pod_generate_name': 'application-controller-manager-', 'kind': 'StatefulSet'}, 'prometheus-1-node-exporter-8xcb2': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-nk90', 'pod_generate_name': 'prometheus-1-node-exporter-', 'kind': 'DaemonSet'}, 'prometheus-1-alertmanager-1': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-nk90', 'pod_generate_name': 'prometheus-1-alertmanager-', 'kind': 'StatefulSet'}, 'prometheus-to-sd-8kpfz': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-nk90', 'pod_generate_name': 'prometheus-to-sd-', 'kind': 'DaemonSet'}, 'kube-dns-autoscaler-76fcd5f658-dpws8': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-nk90', 'pod_generate_name': 'kube-dns-autoscaler-76fcd5f658-', 'kind': 'ReplicaSet'}, 'php-apache-5f657688bc-vqmq9': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-nk90', 'pod_generate_name': 'php-apache-5f657688bc-', 'kind': 'ReplicaSet'}, 'event-exporter-v0.2.4-5f7d5d7dd4-dqlsb': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-nk90', 'pod_generate_name': 'event-exporter-v0.2.4-5f7d5d7dd4-', 'kind': 'ReplicaSet'}, 'fluentd-gcp-v3.2.0-52l6m': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-nk90', 'pod_generate_name': 'fluentd-gcp-v3.2.0-', 'kind': 'DaemonSet'}, 'prometheus-1-kube-state-metrics-66cfd5684-nzgmm': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-nk90', 'pod_generate_name': 'prometheus-1-kube-state-metrics-66cfd5684-', 'kind': 'ReplicaSet'}, 'metrics-server-v0.3.1-5b4d6d8d98-gn8rs': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-nk90', 'pod_generate_name': 'metrics-server-v0.3.1-5b4d6d8d98-', 'kind': 'ReplicaSet'}, 'l7-default-backend-6f8697844f-kbxwg': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-nk90', 'pod_generate_name': 'l7-default-backend-6f8697844f-', 'kind': 'ReplicaSet'}, 'kube-proxy-gke-demo-cluster-1-default-pool-6f471531-nk90': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-nk90', 'pod_generate_name': 'kube-proxy-gke-demo-cluster-1-default-pool-6f471531-', 'kind': 'DaemonSet'}, 'fluentd-gcp-scaler-7b895cbc89-vn5m5': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-nk90', 'pod_generate_name': 'fluentd-gcp-scaler-7b895cbc89-', 'kind': 'ReplicaSet'}, 'prometheus-1-grafana-0': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-nk90', 'pod_generate_name': 'prometheus-1-grafana-', 'kind': 'StatefulSet'}, 'kube-dns-b46cc9485-x2tzq': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-nk90', 'pod_generate_name': 'kube-dns-b46cc9485-', 'kind': 'ReplicaSet'}}}, 'gke-demo-cluster-1-default-pool-6f471531-4xrb': {'cpu': 2.0, 'memory': 7.303501129150391, 'pods': {'php-apache-5f657688bc-qpbm7': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-4xrb', 'pod_generate_name': 'php-apache-5f657688bc-', 'kind': 'ReplicaSet'}, 'prometheus-to-sd-xwqbz': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-4xrb', 'pod_generate_name': 'prometheus-to-sd-', 'kind': 'DaemonSet'}, 'prometheus-1-alertmanager-0': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-4xrb', 'pod_generate_name': 'prometheus-1-alertmanager-', 'kind': 'StatefulSet'}, 'prometheus-1-prometheus-1': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-4xrb', 'pod_generate_name': 'prometheus-1-prometheus-', 'kind': 'StatefulSet'}, 'fluentd-gcp-v3.2.0-29mdd': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-4xrb', 'pod_generate_name': 'fluentd-gcp-v3.2.0-', 'kind': 'DaemonSet'}, 'prometheus-1-node-exporter-z4fl5': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-4xrb', 'pod_generate_name': 'prometheus-1-node-exporter-', 'kind': 'DaemonSet'}, 'kube-proxy-gke-demo-cluster-1-default-pool-6f471531-4xrb': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-4xrb', 'pod_generate_name': 'kube-proxy-gke-demo-cluster-1-default-pool-6f471531-', 'kind': 'DaemonSet'}, 'php-apache-5f657688bc-mxr29': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-4xrb', 'pod_generate_name': 'php-apache-5f657688bc-', 'kind': 'ReplicaSet'}, 'php-apache-5f657688bc-6qk8c': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-4xrb', 'pod_generate_name': 'php-apache-5f657688bc-', 'kind': 'ReplicaSet'}, 'php-apache-5f657688bc-6lfpk': {'node_name': 'gke-demo-cluster-1-default-pool-6f471531-4xrb', 'pod_generate_name': 'php-apache-5f657688bc-', 'kind': 'ReplicaSet'}}}}

        print(find_transitions_execution_change(current_state, desired_state))



