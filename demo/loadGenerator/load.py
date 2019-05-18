import base64

from locust import HttpLocust, TaskSet, task
import random


class Load(TaskSet):
    @task
    def action(self):
        self.client.get("/")


class WebsiteUser(HttpLocust):
    task_set = Load
    min_wait = 5000
    max_wait = 9000
