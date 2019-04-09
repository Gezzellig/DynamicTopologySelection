import base64

from locust import HttpLocust, TaskSet, task
import random


class UserBehavior(TaskSet):
    @task
    def action(self):
        #base64string = base64.encodestring('%s:%s' % ('jo', 'oj')).replace('\n', '')
        catalogue = self.client.get("/catalogue").json()
        product = random.choice(catalogue)
        item_id = product["id"]
        self.client.get("/")
        self.client.get("/login", auth=("user", "password"))
        self.client.get("/category.html")
        self.client.get("/detail.html?id={}".format(item_id))
        self.client.delete("/cart")
        self.client.post("/cart", json={"id": item_id, "quantity": 1})
        self.client.get("/basket.html")
        self.client.post("/orders")


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000
