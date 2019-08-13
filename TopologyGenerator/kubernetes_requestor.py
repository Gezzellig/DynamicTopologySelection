import subprocess
import time

import requests
from subprocess import Popen

from urllib3.exceptions import MaxRetryError

from log import log

kubernetes_connection_process = None


def kubernetes_request(query):
    for i in range(0, 100):
        try:
            result = requests.get(query)
            return result
        except requests.exceptions.RequestException as e:
            print(e)
            log.info("Kubernetes API connection died, reconnecting")
            global prometheus_connection_process
            prometheus_connection_process = Popen(["kubectl", "proxy", "--port=8080"])
            time.sleep(1)
