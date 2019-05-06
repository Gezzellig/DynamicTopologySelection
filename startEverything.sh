minikube start --cpus 6 --memory 8192
docker-compose -f docker-compose.yml up -d

#To allow prometheus to reach cAdvisor
minikube ssh 'sudo sed -e "/cadvisor-port=0/d" -i "/etc/systemd/system/kubelet.service.d/10-kubeadm.conf";
if ! sudo grep -q "authentication-token-webhook=true" "/etc/systemd/system/kubelet.service.d/10-kubeadm.conf"; then
  sudo sed -e "s/--authorization-mode=Webhook/--authentication-token-webhook=true --authorization-mode=Webhook/" -i "/etc/systemd/system/kubelet.service.d/10-kubeadm.conf"
fi;
sudo systemctl daemon-reload; 
sudo systemctl restart kubelet;'



#TODO remove, allows for direct API excess for kubectl
gnome-terminal -- kubectl proxy --port=8080
gnome-terminal -- locust -f ../robot-shop/load-gen/robot-shop.py --host=http://192.168.99.101:30080
gnome-terminal -- minikube dashboard

sleep 5
firefox http://localhost:8089
echo "ipaddress:"
minikube ip
echo "Ports open:"
kubectl get svc --all-namespaces -o go-template='{{range .items}}{{range.spec.ports}}{{if .nodePort}}{{.nodePort}}{{"\n"}}{{end}}{{end}}{{end}}'
