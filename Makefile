up-gitlab:
	@gcloud config set project re-kube	
	@gcloud container clusters get-credentials develop-cluster
	@gcloud -q container clusters resize develop-cluster --size=5
	@gcloud container clusters update develop-cluster --enable-autoscaling --min-nodes 1 --max-nodes 8 --node-pool small-pool	
	#@gcloud -q container clusters resize test-cluster --size=6	
	@docker-compose -f docker-compose.yml up -d
	@gnome-terminal --tab -- kubectl proxy --port=8080
	@sleep 5
	@firefox https://console.cloud.google.com/home/dashboard?project=re-kube
	@gnome-terminal --tab -- kubectl port-forward -n monitoring prometheus-1-prometheus-0 9090
	@gnome-terminal --tab -- kubectl port-forward --namespace monitoring prometheus-1-grafana-0 3000
	@echo "Ports open:"
	@kubectl get svc --all-namespaces -o go-template='{{range .items}}{{range.spec.ports}}{{if .nodePort}}{{.nodePort}}{{"\n"}}{{end}}{{end}}{{end}}'
	
down-gitlab:
	@gcloud config set project re-kube	
	@gcloud container clusters get-credentials develop-cluster
	@gcloud container clusters update develop-cluster --no-enable-autoscaling --node-pool small-pool	
	@gcloud -q container clusters resize develop-cluster --size=0
	@docker stop $(shell docker ps -q)

up-demo:
	@gcloud config set project quixotic-dynamo-243708
	@gcloud container clusters get-credentials demo-cluster-1
	@gcloud -q container clusters resize demo-cluster-1 --size=2	
	@gcloud container clusters update demo-cluster-1 --enable-autoscaling --min-nodes 1 --max-nodes 8 --node-pool default-pool 	
	@docker-compose -f docker-compose.yml up -d
	@gnome-terminal --tab -- kubectl proxy --port=8080
	@gnome-terminal --tab -- locust -f demo/loadGenerator/load.py --host=http://35.234.80.55/
	@sleep 5
	@firefox https://console.cloud.google.com/kubernetes/list?project=quixotic-dynamo-243708
	@gnome-terminal --tab -- kubectl port-forward -n monitoring prometheus-1-prometheus-0 9090
	@gnome-terminal --tab -- kubectl port-forward --namespace monitoring prometheus-1-grafana-0 3000
	@echo "Ports open:"
	@kubectl get svc --all-namespaces -o go-template='{{range .items}}{{range.spec.ports}}{{if .nodePort}}{{.nodePort}}{{"\n"}}{{end}}{{end}}{{end}}'

down-demo:
	@gcloud config set project quixotic-dynamo-243708
	@gcloud container clusters get-credentials demo-cluster-1
	@gcloud container clusters update demo-cluster-1 --no-enable-autoscaling --node-pool default-pool 
	@gcloud -q container clusters resize demo-cluster-1 --size=0
	@docker stop $(shell docker ps -q)

rego:
	@gcloud config set project quixotic-dynamo-243708
	@gcloud container clusters get-credentials demo-cluster-1
	@gcloud -q container clusters resize demo-cluster-1 --size=0
	@gcloud -q container clusters resize demo-cluster-1 --size=3


support-up:
	@gcloud config set project quixotic-dynamo-243708
	@gcloud container clusters get-credentials demo-cluster-1
	@docker-compose -f docker-compose.yml up -d
	@gnome-terminal --tab -- kubectl proxy --port=8080
	@gnome-terminal --tab -- locust -f demo/loadGenerator/load.py --host=http://35.198.110.237/
	@sleep 5
	@firefox https://console.cloud.google.com/home/dashboard?project=re-kube
	@gnome-terminal --tab -- kubectl port-forward -n monitoring prometheus-1-prometheus-0 9090
	@gnome-terminal --tab -- kubectl port-forward --namespace monitoring prometheus-1-grafana-0 3000
	@echo "Ports open:"
	@kubectl get svc --all-namespaces -o go-template='{{range .items}}{{range.spec.ports}}{{if .nodePort}}{{.nodePort}}{{"\n"}}{{end}}{{end}}{{end}}'
