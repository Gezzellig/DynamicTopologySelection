import datetime
import json
import sys

from SmartKubernetesSchedular.LoadExtractorBytesIn import LoadExtractorBytesIn
from SmartKubernetesSchedular.strategies import random_pod_redeployment
from SmartKubernetesSchedular.time_window import create_time_window


def improvement_iteration(settings, time_window, load_extractor):
    end_time = datetime.datetime.now()
    load = load_extractor.extract_load(end_time-time_window, time_window, settings)
    create_time_window(end_time, load, settings, time_window)

    print(load)
    random_pod_redeployment.redeploy(settings)


def main():
    print("starting add_time_window")
    settings_file_name = sys.argv[1]
    print("Settings: {}".format(settings_file_name))
    with open(settings_file_name) as file:
        settings = json.load(file)
    print("Improvement iteration")

    load_extractor = LoadExtractorBytesIn()
    time_window = datetime.timedelta(minutes=2)
    improvement_iteration(settings, time_window, load_extractor)


if __name__ == '__main__':
    main()
