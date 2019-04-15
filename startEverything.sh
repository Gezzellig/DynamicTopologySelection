minikube start --cpus 6 --memory 8192
docker-compose -f docker-compose.yml up -d
gnome-terminal -- locust -f ../robot-shop/load-gen/robot-shop.py --host=http://192.168.99.100:30080
gnome-terminal -- minikube dashboard

sleep 5
firefox http://localhost:8089
