import unittest

from SmartKubernetesSchedular.enforcer import state_to_generate_name_count


class TestEnforcer(unittest.TestCase):
    def test_state_to_generate_name_count(self):
        state = [{'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-ssnl', 'pod_generate_name': 'php-apache-85546b856f-', 'pod_name': 'php-apache-85546b856f-zg5hd', 'containers': ['php-apache']},
                 {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-rl2w', 'pod_generate_name': 'event-exporter-v0.2.3-85644fcdf-', 'pod_name': 'event-exporter-v0.2.3-85644fcdf-tvwwr', 'containers': ['event-exporter', 'prometheus-to-sd-exporter']},
                 {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-rl2w', 'pod_generate_name': 'fluentd-gcp-scaler-8b674f786-', 'pod_name': 'fluentd-gcp-scaler-8b674f786-vqlrp', 'containers': ['fluentd-gcp-scaler']},
                 {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-ssnl', 'pod_generate_name': 'fluentd-gcp-v3.2.0-', 'pod_name': 'fluentd-gcp-v3.2.0-4bkln', 'containers': ['fluentd-gcp', 'prometheus-to-sd-exporter']},
                 {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-rl2w', 'pod_generate_name': 'fluentd-gcp-v3.2.0-', 'pod_name': 'fluentd-gcp-v3.2.0-wrgfm', 'containers': ['fluentd-gcp', 'prometheus-to-sd-exporter']},
                 {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-ssnl', 'pod_generate_name': 'heapster-v1.6.0-beta.1-7fd7df66d-', 'pod_name': 'heapster-v1.6.0-beta.1-7fd7df66d-vr2jd', 'containers': ['heapster', 'prom-to-sd', 'heapster-nanny']},
                 {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-rl2w', 'pod_generate_name': 'kube-dns-76dbb796c5-', 'pod_name': 'kube-dns-76dbb796c5-99hnn', 'containers': ['kubedns', 'dnsmasq', 'sidecar', 'prometheus-to-sd']},
                 {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-rl2w', 'pod_generate_name': 'kube-dns-76dbb796c5-', 'pod_name': 'kube-dns-76dbb796c5-vfrnv', 'containers': ['kubedns', 'dnsmasq', 'sidecar', 'prometheus-to-sd']},
                 {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-rl2w', 'pod_generate_name': 'kube-dns-autoscaler-67c97c87fb-', 'pod_name': 'kube-dns-autoscaler-67c97c87fb-fgsdz', 'containers': ['autoscaler']},
                 {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-rl2w', 'pod_generate_name': None, 'pod_name': 'kube-proxy-gke-develop-cluster-larger-pool-9ecdadbf-rl2w', 'containers': ['kube-proxy']},
                 {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-ssnl', 'pod_generate_name': None, 'pod_name': 'kube-proxy-gke-develop-cluster-larger-pool-9ecdadbf-ssnl', 'containers': ['kube-proxy']},
                 {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-rl2w', 'pod_generate_name': 'l7-default-backend-7ff48cffd7-', 'pod_name': 'l7-default-backend-7ff48cffd7-wzx2m', 'containers': ['default-http-backend']},
                 {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-rl2w', 'pod_generate_name': 'metrics-server-75b8d78f76-', 'pod_name': 'metrics-server-75b8d78f76-smhfn', 'containers': ['metrics-server']},
                 {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-rl2w', 'pod_generate_name': 'metrics-server-v0.2.1-fd596d746-', 'pod_name': 'metrics-server-v0.2.1-fd596d746-fmnm7', 'containers': ['metrics-server', 'metrics-server-nanny']},
                 {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-rl2w', 'pod_generate_name': 'prometheus-to-sd-', 'pod_name': 'prometheus-to-sd-q47jm', 'containers': ['prometheus-to-sd']},
                 {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-ssnl', 'pod_generate_name': 'prometheus-to-sd-', 'pod_name': 'prometheus-to-sd-wstft', 'containers': ['prometheus-to-sd']},
                 {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-rl2w', 'pod_generate_name': 'prometheus-1-alertmanager-', 'pod_name': 'prometheus-1-alertmanager-0', 'containers': ['prometheus-alertmanager']},
                 {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-ssnl', 'pod_generate_name': 'prometheus-1-alertmanager-', 'pod_name': 'prometheus-1-alertmanager-1', 'containers': ['prometheus-alertmanager']},
                 {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-rl2w', 'pod_generate_name': 'prometheus-1-grafana-', 'pod_name': 'prometheus-1-grafana-0', 'containers': ['grafana']},
                 {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-ssnl', 'pod_generate_name': 'prometheus-1-grafana-', 'pod_name': 'prometheus-1-grafana-1', 'containers': ['grafana']},
                 {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-rl2w', 'pod_generate_name': 'prometheus-1-kube-state-metrics-7f785c4cb9-', 'pod_name': 'prometheus-1-kube-state-metrics-7f785c4cb9-sjg4x', 'containers': ['kube-state-metrics', 'addon-resizer']},
                 {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-rl2w', 'pod_generate_name': 'prometheus-1-node-exporter-', 'pod_name': 'prometheus-1-node-exporter-pvzrj', 'containers': ['prometheus-node-exporter']},
                 {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-ssnl', 'pod_generate_name': 'prometheus-1-node-exporter-', 'pod_name': 'prometheus-1-node-exporter-vplm2', 'containers': ['prometheus-node-exporter']},
                 {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-ssnl', 'pod_generate_name': 'prometheus-1-prometheus-', 'pod_name': 'prometheus-1-prometheus-0', 'containers': ['prometheus-server']},
                 {'node_name': 'gke-develop-cluster-larger-pool-9ecdadbf-rl2w', 'pod_generate_name': 'prometheus-1-prometheus-', 'pod_name': 'prometheus-1-prometheus-1', 'containers': ['prometheus-server']}]
        answer_count = {
            'php-apache-85546b856f-': 1,
            'event-exporter-v0.2.3-85644fcdf-': 1,
            'fluentd-gcp-scaler-8b674f786-': 1,
            'fluentd-gcp-v3.2.0-': 2,
            'heapster-v1.6.0-beta.1-7fd7df66d-': 1,
            'kube-dns-76dbb796c5-': 2,
            'kube-dns-autoscaler-67c97c87fb-': 1,
            None: 2,
            'l7-default-backend-7ff48cffd7-': 1,
            'metrics-server-75b8d78f76-': 1,
            'metrics-server-v0.2.1-fd596d746-': 1,
            'prometheus-to-sd-': 2,
            'prometheus-1-alertmanager-': 2,
            'prometheus-1-grafana-': 2,
            'prometheus-1-kube-state-metrics-7f785c4cb9-': 1,
            'prometheus-1-node-exporter-': 2,
            'prometheus-1-prometheus-': 2
        }
        state_count = state_to_generate_name_count(state)
        self.assertEqual(answer_count, state_count)
