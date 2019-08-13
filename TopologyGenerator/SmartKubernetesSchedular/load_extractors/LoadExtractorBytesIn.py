import datetime
import json
import sys

import requests

from SmartKubernetesSchedular.load_extractors.AbstractLoadExtractor import AbstractLoadExtractor
from prometheus_requestor import prometheus_request


class LoadExtractorBytesIn(AbstractLoadExtractor):
    def extract_load(self, end_time, window, settings):
        #pod_name = "php-apache-.*" #CLOUD
        pod_name = settings["load_pod_name"]
        request = 'http://{prom_address}/api/v1/query?query=sum(rate(container_network_receive_bytes_total{{interface="eth0",pod_name=~"{pod_name}"}}[{window}s]))&time={start_time}'.format(prom_address=settings["prometheus_address"], pod_name=pod_name, start_time=(end_time-window).timestamp(), window=window.seconds)
        result = prometheus_request(request).json()
        try:
            return float(result["data"]["result"][0]["value"][1])
        except IndexError:
            print("There was no load measurement for:")
            print(request)
            print("shutting down")
            exit(0)


def main():
    print("starting add_time_window")
    settings_file_name = sys.argv[1]
    print("Settings: {}".format(settings_file_name))
    with open(settings_file_name) as file:
        settings = json.load(file)
    load_extractor = LoadExtractorBytesIn()
    window = datetime.timedelta(minutes=5)
    print(load_extractor.extract_load(datetime.datetime.now(), window, settings))


if __name__ == '__main__':
    main()
