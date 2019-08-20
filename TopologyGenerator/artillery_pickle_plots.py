import csv
import datetime
import json
import math
import matplotlib.pyplot as plt
import seaborn as sns

import requests

from artillery_pickle import load_cost
from artillery_pickle_per_node import get_data_simulating_proper_node_removal

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


def get_latency(start_time, artillery_file):
    latency_median = []
    latency_p95 = []
    for measurement in artillery_file["intermediate"]:
        if datetime_artillery(measurement["timestamp"])+artillery_time_correction >= start_time:
            latency_median.append(measurement["latency"]["median"])
            latency_p95.append(measurement["latency"]["p95"])
    return latency_median, latency_p95


def artillery_to_structure(artillery_file, cost_pickle_path):
    start_time, end_time, warmup = get_start_end_time_warmup(artillery_file)
    cost = load_cost(cost_pickle_path)
    latency_median, latency_p95 = get_latency(start_time, artillery_file)

    structure = {
        "start_time": start_time,
        "end_time": end_time,
        "cost": cost,
        "latency_median": latency_median,
        "latency_p95": latency_p95
    }
    return structure


def average_parameter(structures, parameter):
    sum = structures[0][parameter]
    for i in range(1, len(structures)):
        sum = [x + y for x, y in zip(sum, structures[i][parameter])]
    average = [x/len(structures) for x in sum]
    return average


def average_structures(structures):
    average_cost = average_parameter(structures, "cost")
    average_latency_median = average_parameter(structures, "latency_median")
    average_latency_p95 = average_parameter(structures, "latency_p95")
    average_structure = {
        "cost": average_cost,
        "latency_median": average_latency_median,
        "latency_p95": average_latency_p95
    }
    pattern_length = structures[0]["end_time"] - structures[0]["start_time"]
    return pattern_length, average_structure

def average_artillery_files(folder, artillery_file_names):
    structures = []
    for artillery_file_name in artillery_file_names:
        with open(folder + artillery_file_name+artillery_file_name_extension) as file:
            artillery_file = json.load(file)
        structures.append(artillery_to_structure(artillery_file, folder + artillery_file_name+pickle_file_name_extension))
    return average_structures(structures)


def plot_cost(pattern_length, with_cost, without_cost, with_no_node_removal_cost, av_with_node_removal_simulated, output_file_name):
    timestep = pattern_length.seconds / float(len(with_cost))
    time_axis = [x*timestep/time_scale for x in range(0, len(with_cost))]

    fig, ax = plt.subplots(1, 1, figsize=(plot_width, plot_height))
    plt.title("Cost Tuner vs Normal")
    plt.ylabel("Cost (Euro)")
    plt.xlabel("Time (minutes)")
    plt.plot(time_axis, without_cost, color="red", label="Normal")
    plt.plot(time_axis, with_cost, color="blue", label="Tuner with node removal")
    plt.plot(time_axis, with_no_node_removal_cost, color="green", label="Tuner without node removal")
    plt.plot(time_axis, av_with_node_removal_simulated, color="black", label="Tuner simulated node removal")
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.20), ncol=2)
    #plt.subplots_adjust(bottom=0.20)
    fig.savefig(output_file_name, bbox_inches='tight')
    plt.close()


def plot_cost_per_type(title, pattern_length, with_cost, color, without_cost, output_file_name):
    timestep = pattern_length.seconds / float(len(with_cost))
    time_axis = [x*timestep/time_scale for x in range(0, len(with_cost))]

    fig, ax = plt.subplots(1, 1, figsize=(plot_width, plot_height))
    plt.title(title)
    plt.ylabel("Cost (Euro)")
    plt.xlabel("Time (minutes)")
    plt.plot(time_axis, without_cost, color="red", label="Normal")
    plt.plot(time_axis, with_cost, color=color, label="Tuner")
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.20), ncol=2)
    #plt.subplots_adjust(bottom=0.20)
    fig.savefig(output_file_name, bbox_inches='tight')
    plt.close()


def plot_latency(pattern_length, with_median, with_p95, without_median, without_p95, with_no_node_median, with_no_node_p95, output_folder):
    timestep = pattern_length.seconds / float(len(with_median))
    time_axis = [x*timestep/time_scale for x in range(0, len(with_median))]

    plt.figure(figsize=(plot_width, plot_height))
    plt.title("Latency Tuner vs Normal")
    plt.ylabel("Latency (milliseconds)")
    plt.xlabel("Time (minutes)")
    plt.plot(time_axis, without_median, color="blue", label="Normal, median")
    plt.plot(time_axis, without_p95, color="blue", linestyle='dotted', label="Normal, 95th percentile")
    plt.plot(time_axis, with_median, color="red", label="Tuner, median")
    plt.plot(time_axis, with_p95, color="red", linestyle='dotted', label="Tuner, 95th percentile")
    plt.plot(time_axis, with_no_node_median, color="green", label="Tuner without node removal, median")
    plt.plot(time_axis, with_no_node_p95, color="green", linestyle='dotted', label="Tuner without node removal, 95th percentile")
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.20), ncol=2)
    plt.savefig(output_folder+'latency.png', bbox_inches='tight')
    plt.close()

    plt.figure(figsize=(plot_width, plot_height))
    plt.title("Latency Tuner vs Normal")
    plt.ylabel("Latency (milliseconds)")
    plt.xlabel("Time (minutes)")

    plt.yscale("log")
    #plt.ylim(0, 3000)

    plt.plot(time_axis, without_median, color="blue", label="Normal, median")
    plt.plot(time_axis, without_p95, color="blue", linestyle='dotted', label="Normal, 95th percentile")
    plt.plot(time_axis, with_median, color="red", label="Tuner, median")
    plt.plot(time_axis, with_p95, color="red", linestyle='dotted', label="Tuner, 95th percentile")
    plt.plot(time_axis, with_no_node_median, color="green", label="Tuner without node removal, median")
    plt.plot(time_axis, with_no_node_p95, color="green", linestyle='dotted', label="Tuner without node removal, 95th percentile")
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.20), ncol=2)
    plt.savefig(output_folder+"log_latency.png", bbox_inches='tight')
    plt.close()


def plot_latency_per_type(title, pattern_length, with_median, with_p95, color, without_median, without_p95, output_file_name):
    timestep = pattern_length.seconds / float(len(with_median))
    time_axis = [x*timestep/time_scale for x in range(0, len(with_median))]

    plt.figure(figsize=(plot_width, plot_height))
    plt.title(title)
    plt.ylabel("Latency (milliseconds)")
    plt.xlabel("Time (minutes)")
    plt.plot(time_axis, without_median, color="blue", label="Normal, median")
    plt.plot(time_axis, without_p95, color="blue", linestyle='dotted', label="Normal, 95th percentile")
    plt.plot(time_axis, with_median, color=color, label="Tuner, median")
    plt.plot(time_axis, with_p95, color=color, linestyle='dotted', label="Tuner, 95th percentile")
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.20), ncol=2)
    plt.savefig(output_file_name+".png", bbox_inches='tight')
    plt.close()

    plt.figure(figsize=(plot_width, plot_height))
    plt.title(title)
    plt.ylabel("Latency (milliseconds)")
    plt.xlabel("Time (minutes)")

    plt.yscale("log")
    #plt.ylim(0, 3000)

    plt.plot(time_axis, without_median, color="blue", label="Normal, median")
    plt.plot(time_axis, without_p95, color="blue", linestyle='dotted', label="Normal, 95th percentile")
    plt.plot(time_axis, with_median, color=color, label="Tuner, median")
    plt.plot(time_axis, with_p95, color=color, linestyle='dotted', label="Tuner, 95th percentile")
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.20), ncol=2)
    plt.savefig(output_file_name+"_log.png", bbox_inches='tight')
    plt.close()


def plot_with_without(pattern_length, av_with, av_without, av_with_no_node_removal, av_with_node_removal_simulated, output_folder):
    plot_cost(pattern_length, av_with["cost"], av_without["cost"], av_with_no_node_removal["cost"], av_with_node_removal_simulated, output_folder+"cost.png")
    plot_cost_per_type("Cost with node removal", pattern_length, av_with["cost"], "blue", av_without["cost"], output_folder+"cost_normal.png")
    plot_cost_per_type("Cost without node removal", pattern_length, av_with_no_node_removal["cost"], "green", av_without["cost"], output_folder+"cost_no_node_removal.png")
    plot_cost_per_type("Cost simulated node removal", pattern_length, av_with_node_removal_simulated, "black", av_without["cost"], output_folder+"cost_simulated_node_removal.png")




    plot_latency(pattern_length, av_with["latency_median"], av_with["latency_p95"], av_without["latency_median"], av_without["latency_p95"], av_with_no_node_removal["latency_median"], av_with_no_node_removal["latency_p95"], output_folder)
    plot_latency_per_type("Latency with node removal", pattern_length, av_with["latency_median"], av_with["latency_p95"], "red", av_without["latency_median"], av_without["latency_p95"], output_folder+"latency_with")
    plot_latency_per_type("Latency without node removal", pattern_length, av_with_no_node_removal["latency_median"], av_with_no_node_removal["latency_p95"], "green", av_without["latency_median"], av_without["latency_p95"], output_folder+"latency_without")
    #

def plot_load_pattern(folder, artillery_file_name, output_file_name):
    time = 0
    with open(folder + artillery_file_name) as file:
        artillery_file = json.load(file)
    times = []
    loads = []
    for i in range(0, len(artillery_file["aggregate"]["phases"])):
        phase = artillery_file["aggregate"]["phases"][i]
        if i == 0:
            pass
            #time += phase["duration"]
        else:
            times.append(time/time_scale)
            loads.append(phase["arrivalRate"])
            time += phase["duration"]
            if "rampTo" in phase:
                times.append(time/time_scale)
                loads.append(phase["rampTo"])
            else:
                times.append(time/time_scale)
                loads.append(phase["arrivalRate"])

    plt.figure(figsize=(plot_width, plot_height))
    plt.title("Load pattern")
    plt.ylabel("Load (requests per second)")
    plt.xlabel("Time (minutes)")
    plt.plot(times, loads, label="load", color="green")
    plt.gca().set_ylim(bottom=0)
    plt.legend()
    plt.savefig(output_file_name, bbox_inches='tight')
    plt.close()



def calc_cost(pattern_length, cost_list):
    average_cost = sum(cost_list)/len(cost_list)
    return average_cost*(pattern_length.seconds/3600.0)


def do_everything(pattern_name, pattern_content, folder):
    output_file_name = folder+pattern_name+"/"
    plot_load_pattern(folder, pattern_name+"with_tuner/run3/"+artillery_file_name_extension, output_file_name+"load.png")
    pattern_length, av_with = average_artillery_files(folder+pattern_name+"with_tuner/", pattern_content["with_tuner/"])
    pattern_length, av_without = average_artillery_files(folder+pattern_name+"without_tuner/", pattern_content["without_tuner/"])
    pattern_length, av_with_no_node_removal = average_artillery_files(folder+pattern_name+"with_tuner_no_node_removal/", pattern_content["with_tuner_no_node_removal/"])
    av_with_node_removal_simulated = get_data_simulating_proper_node_removal(folder+pattern_name+"with_tuner_no_node_removal/", pattern_content["with_tuner_no_node_removal/"])
    plot_with_without(pattern_length, av_with, av_without, av_with_no_node_removal, av_with_node_removal_simulated, output_file_name)

    with_cost = calc_cost(pattern_length, av_with["cost"])
    with_no_node_removal_cost = calc_cost(pattern_length, av_with_no_node_removal["cost"])
    without_cost = calc_cost(pattern_length, av_without["cost"])
    with_simulated_cost = calc_cost(pattern_length, av_with_node_removal_simulated)

    saved = without_cost-with_cost
    saved_no_node_removal = without_cost - with_no_node_removal_cost
    saved_simulated = without_cost - with_simulated_cost
    percentage_saved = saved/without_cost*100
    percentage_saved_no_node_removal = saved_no_node_removal/without_cost*100
    percentage_saved_simulated = saved_simulated/without_cost*100

    with open(output_file_name+"cost.txt", "w+") as file:
        file.write("with: {}\n".format(with_cost))
        file.write("without: {}\n".format(without_cost))
        file.write("saved: {}\n".format(saved))
        file.write("percentage saved: {}\n".format(percentage_saved))
        file.write("\n")
        file.write("with no node removal: {}\n".format(with_no_node_removal_cost))
        file.write("without: {}\n".format(without_cost))
        file.write("saved: {}\n".format(saved_no_node_removal))
        file.write("percentage saved: {}\n".format(percentage_saved_no_node_removal))
        file.write("\n")
        file.write("with node removal simulated: {}\n".format(with_simulated_cost))
        file.write("without: {}\n".format(without_cost))
        file.write("saved: {}\n".format(saved_simulated))
        file.write("percentage saved: {}\n".format(percentage_saved_simulated))
        file.write("\n")

    print(pattern_name)
    with open(output_file_name+"cost.txt", "r") as file:
        print(file.read())


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

    for pattern, pattern_content in patterns.items():
        do_everything(pattern, pattern_content, main_folder)


artillery_file_name_extension = "artillery.out"
pickle_file_name_extension = "cost.pck"

artillery_time_correction = datetime.timedelta(hours=2)

if __name__ == '__main__':
    main()
