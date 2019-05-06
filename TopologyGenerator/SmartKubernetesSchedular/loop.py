import datetime
import json
import sys
import time

from SmartKubernetesSchedular import improvement_iteration
from SmartKubernetesSchedular.LoadExtractorBytesIn import LoadExtractorBytesIn


def loop(measure_window, redeploy_window, settings, load_extractor):
    while True:
        print("start measure window time")
        time.sleep(measure_window.seconds)
        print("time to perform improvement iteration")

        improvement_iteration.improvement_iteration(settings, measure_window, load_extractor)

        print("Give the system time to get to rest")
        time.sleep(redeploy_window.seconds)
        print("annnnnd again")

        


def start_loop(settings, load_extractor):
    measure_window = datetime.timedelta(seconds=settings["measure_window"])
    redeploy_window = datetime.timedelta(seconds=settings["redeploy_window"])

    loop(measure_window, redeploy_window, settings, load_extractor)





def main():
    print("starting loop")
    settings_file_name = sys.argv[1]
    print("Settings: {}".format(settings_file_name))
    with open(settings_file_name) as file:
        settings = json.load(file)

    load_extractor = LoadExtractorBytesIn()
    start_loop(settings, load_extractor)

if __name__ == '__main__':
    main()