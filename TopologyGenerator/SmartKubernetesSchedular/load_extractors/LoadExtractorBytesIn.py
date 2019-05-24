import datetime
import json
import sys

import requests

from SmartKubernetesSchedular.load_extractors import AbstractLoadExtractor


class LoadExtractorBytesIn(AbstractLoadExtractor):
    def extract_load(self, start_time, window, settings):
        #pod_name = "web-5d46fb6ff7-bp77b" #Minikube
        pod_name = "front-end-.*" #CLOUD
        request = 'http://{prom_address}/api/v1/query?query=sum(rate(container_network_receive_bytes_total{{interface="eth0",pod_name=~"{pod_name}"}}[{window}s]))&time={start_time}'.format(prom_address=settings["prometheus_address"], pod_name=pod_name, start_time=start_time.timestamp(), window=window.seconds)
        print(request)
        result = requests.get(request).json()
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
    load_extractor.extract_load(datetime.datetime.now()-window, window, settings)


if __name__ == '__main__':
    main()
