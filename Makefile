up:
	@gcloud container clusters get-credentials develop-cluster
	@gcloud -q container clusters resize develop-cluster --size=3	
	@gcloud container clusters update develop-cluster --enable-autoscaling --min-nodes 1 --max-nodes 8 --node-pool larger-pool	
	#@gcloud -q container clusters resize test-cluster --size=6	
	@docker-compose -f docker-compose.yml up -d
	@gnome-terminal --tab -- kubectl proxy --port=8080
	@gnome-terminal --tab -- locust -f demo/loadGenerator/load.py --host=http://35.198.110.237/
	@sleep 5
	@firefox https://console.cloud.google.com/home/dashboard?project=re-kube
	@gnome-terminal --tab -- kubectl port-forward -n monitoring prometheus-1-prometheus-0 9090
	@gnome-terminal --tab -- kubectl port-forward --namespace monitoring prometheus-1-grafana-0 3000
	@echo "Ports open:"
	@kubectl get svc --all-namespaces -o go-template='{{range .items}}{{range.spec.ports}}{{if .nodePort}}{{.nodePort}}{{"\n"}}{{end}}{{end}}{{end}}'
	
down:
	@gcloud container clusters update develop-cluster --no-enable-autoscaling --node-pool larger-pool
	@gcloud -q container clusters resize develop-cluster --size=0
	@docker stop $(shell docker ps -q)

support-up:
	@docker-compose -f docker-compose.yml up -d
	@gnome-terminal --tab -- kubectl proxy --port=8080
	@gnome-terminal --tab -- locust -f demo/loadGenerator/load.py --host=http://35.198.110.237/
	@sleep 5
	@firefox https://console.cloud.google.com/home/dashboard?project=re-kube
	@gnome-terminal --tab -- kubectl port-forward -n monitoring prometheus-1-prometheus-0 9090
	@gnome-terminal --tab -- kubectl port-forward --namespace monitoring prometheus-1-grafana-0 3000
	@echo "Ports open:"
	@kubectl get svc --all-namespaces -o go-template='{{range .items}}{{range.spec.ports}}{{if .nodePort}}{{.nodePort}}{{"\n"}}{{end}}{{end}}{{end}}'
