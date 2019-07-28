#https://console.cloud.google.com/logs/viewer
#NOT logName ="projects/quixotic-dynamo-243708/logs/cloudaudit.googleapis.com%2Factivity"



for path in projects/quixotic-dynamo-243708/logs/docker projects/quixotic-dynamo-243708/logs/kubelet projects/quixotic-dynamo-243708/logs/fluentd-gcp projects/quixotic-dynamo-243708/logs/events projects/quixotic-dynamo-243708/logs/grafana projects/quixotic-dynamo-243708/logs/prometheus-alertmanager projects/quixotic-dynamo-243708/logs/prometheus-server projects/quixotic-dynamo-243708/logs/php-apache projects/quixotic-dynamo-243708/logs/default-http-backend projects/quixotic-dynamo-243708/logs/manager projects/quixotic-dynamo-243708/logs/kube-state-metrics projects/quixotic-dynamo-243708/logs/autoscaler projects/quixotic-dynamo-243708/logs/heapster projects/quixotic-dynamo-243708/logs/metrics-server-nanny projects/quixotic-dynamo-243708/logs/event-exporter projects/quixotic-dynamo-243708/logs/kube-proxy projects/quixotic-dynamo-243708/logs/metrics-server projects/quixotic-dynamo-243708/logs/addon-resizer projects/quixotic-dynamo-243708/logs/heapster-nanny projects/quixotic-dynamo-243708/logs/node-problem-detector projects/quixotic-dynamo-243708/logs/fluentd-gcp-scaler projects/quixotic-dynamo-243708/logs/prometheus-node-exporter projects/quixotic-dynamo-243708/logs/prometheus-to-sd projects/quixotic-dynamo-243708/logs/prometheus-to-sd-exporter projects/quixotic-dynamo-243708/logs/sidecar projects/quixotic-dynamo-243708/logs/dnsmasq projects/quixotic-dynamo-243708/logs/prom-to-sd
do
  gcloud -q logging logs delete $path
done

