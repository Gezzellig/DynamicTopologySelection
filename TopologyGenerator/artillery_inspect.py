import csv
import datetime
import json
import math
import pickle

import matplotlib.pyplot as plt
import seaborn as sns

import requests

from artillery_pickle import load_cost

time_scale = 60.0
plot_width = 7
plot_height = 4

def datetime_artillery(date_string):
    no_micro = date_string.split(".")[0]
    return datetime.datetime.strptime(no_micro, "%Y-%m-%dT%H:%M:%S")


def get_start_end_time_warmup(artillery_file):
    aggregate = artillery_file["aggregate"]
    warmup = datetime.timedelta(seconds=aggregate["phases"][0]["duration"])
    script_start_time = datetime_artillery(artillery_file["intermediate"][0]["timestamp"])+artillery_time_correction
    start_time = script_start_time + warmup

    total_phase_time = 0
    for phase in aggregate["phases"]:
        total_phase_time += phase["duration"]
    total_phase_time = datetime.timedelta(seconds=total_phase_time)

    end_time = script_start_time + total_phase_time
    return start_time, end_time, warmup


def inspect(name, pattern_length, folder_path):
    cost = load_cost(folder_path)


    timestep = pattern_length.seconds / float(len(cost))
    time_axis = [x * timestep / time_scale for x in range(0, len(cost))]

    plt.figure(figsize=(plot_width, plot_height))
    plt.title(name)
    plt.ylabel("Cost (Euro)")
    plt.xlabel("Time (minutes)")
    plt.plot(time_axis, cost, color="red", label="Normal")
    plt.legend()
    plt.show()


def main():
    sns.set()
    main_folder = "/media/thijs/SSD2/University/2018-2019/Thesis/DynamicTopologySelection/results2/"
    patterns = {
        "long_equal/": {
            "with_tuner/":
                ["run2/", "run3/", "run5/"],
            "without_tuner/":
                ["run2/", "run3/", "run5/"],
            "with_tuner_no_node_removal/":
                ["run2/", "run3/", "run5/"]
        },
        "peaks/": {
            "with_tuner/":
                ["run2/", "run3/", "run5/"],
            "without_tuner/":
                ["run2/", "run3/", "run5/"],
            "with_tuner_no_node_removal/":
                ["run2/", "run3/", "run4/", "run5/"]
        },
        "small_equal/": {
            "with_tuner/":
                ["run1/", "run3/", "run5/"],
            "without_tuner/":
                ["run1/", "run2/", "run3/", "run5/"],
            "with_tuner_no_node_removal/":
                ["run2/", "run3/", "run5/"]
        }
    }

    artillery_file_name_extension = "artillery.out"
    pickle_file_name_extension = "cost.pck"

    for pattern, types in patterns.items():
        for type, runs in types.items():
            for run in runs:
                folder_path = main_folder+pattern+type+run
                with open(folder_path + artillery_file_name_extension) as file:
                    artillery_file = json.load(file)
                start_time, end_time, warmup = get_start_end_time_warmup(artillery_file)
                try:
                    inspect(pattern+type+run, end_time-start_time, folder_path+pickle_file_name_extension)
                except IndexError:
                    print("UNSUITABLE: {}".format(folder_path))



artillery_time_correction = datetime.timedelta(hours=2)

if __name__ == '__main__':
    main()
