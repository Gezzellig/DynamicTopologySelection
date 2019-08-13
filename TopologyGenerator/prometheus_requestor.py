import subprocess
import time

import requests
from subprocess import Popen

from urllib3.exceptions import MaxRetryError

from log import log

prometheus_connection_process = None


def prometheus_request(query):
    for i in range(0, 100):
        try:
            result = requests.get(query)
            return result
        except requests.exceptions.RequestException as e:
            print(e)
            log.info("Prometheus connection died, reconnecting")
            global prometheus_connection_process
            prometheus_connection_process = Popen(["kubectl", "port-forward", "-n", "monitoring", "prometheus-1-prometheus-0", "9090"])
            time.sleep(1)
