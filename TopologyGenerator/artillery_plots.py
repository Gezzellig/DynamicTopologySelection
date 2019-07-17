import csv
import datetime
import json
import math
import matplotlib.pyplot as plt
import seaborn as sns

import requests

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


def get_cost(start_time, end_time):
    step_per_hour = 14
    step = math.floor(((end_time - start_time).seconds / 3600) * step_per_hour)
    print(step)
    cpu_cost = 0.0280
    memory_cost = 0.0038
    query = "http://localhost:9090/api/v1/query_range?query=sum(node%3Anode_num_cpu%3Asum)*{cpu}%2Bsum(node%3Anode_memory_bytes_total%3Asum)*({memory}%2F2%5E30)&start={start}&end={end}&step={step}"
    filled_query = query.format(start=start_time.timestamp(), end=end_time.timestamp(), step=step, cpu=cpu_cost, memory=memory_cost)
    print(filled_query)
    result = requests.get(filled_query).json()
    print(result)
    cost = []
    for value in result["data"]["result"][0]["values"]:
        cost.append(float(value[1]))
    return cost


def get_latency(start_time, artillery_file):
    latency_median = []
    latency_p95 = []
    for measurement in artillery_file["intermediate"]:
        if datetime_artillery(measurement["timestamp"])+artillery_time_correction >= start_time:
            latency_median.append(measurement["latency"]["median"])
            latency_p95.append(measurement["latency"]["p95"])
    return latency_median, latency_p95


def artillery_to_structure(artillery_file):
    start_time, end_time, warmup = get_start_end_time_warmup(artillery_file)
    print("start time: {}".format(start_time))
    print("end time: {}".format(end_time))
    cost = get_cost(start_time, end_time)
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
    for i in range(1,len(structures)):
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
        with open(folder + artillery_file_name) as file:
            artillery_file = json.load(file)
        structures.append(artillery_to_structure(artillery_file))
    return average_structures(structures)


def plot_cost(pattern_length, with_cost, without_cost):
    timestep = pattern_length.seconds / float(len(with_cost))
    time_axis = [x*timestep/time_scale for x in range(0, len(with_cost))]

    plt.figure(figsize=(plot_width, plot_height))
    plt.title("Cost Tuner vs Normal")
    plt.ylabel("Cost (Euro)")
    plt.xlabel("Time (minutes)")
    plt.plot(time_axis, without_cost, color="red", label="Normal")
    plt.legend()
    plt.savefig('plots/cost_normal.png', bbox_inches='tight')
    plt.plot(time_axis, with_cost, color="blue", label="Tuner")
    plt.legend()
    plt.savefig('plots/cost_tuner.png', bbox_inches='tight')
    plt.legend()


def plot_latency(pattern_length, with_median, with_p95, without_median, without_p95):
    timestep = pattern_length.seconds / float(len(with_median))
    time_axis = [x*timestep/time_scale for x in range(0, len(with_median))]

    plt.figure(figsize=(plot_width, plot_height))
    plt.title("Latency Tuner vs Normal")
    plt.ylabel("Latency (milliseconds)")
    plt.xlabel("Time (minutes)")
    plt.plot(time_axis, without_median, color="blue", label="Normal, median")
    plt.legend()
    plt.savefig('plots/normal_median.png', bbox_inches='tight')
    plt.plot(time_axis, without_p95, color="blue", linestyle='dotted', label="Normal, 95th percentile")
    plt.legend()
    plt.savefig('plots/normal_p95.png', bbox_inches='tight')
    plt.plot(time_axis, with_median, color="red", label="Tuner, median")
    plt.legend()
    plt.savefig('plots/tuner_median.png', bbox_inches='tight')
    plt.plot(time_axis, with_p95, color="red", linestyle='dotted', label="Tuner, 95th percentile")
    plt.legend()
    plt.savefig('plots/tuner_p95.png', bbox_inches='tight')

    plt.figure(figsize=(plot_width, plot_height))
    plt.title("Latency Tuner vs Normal")
    plt.ylabel("Latency (milliseconds)")
    plt.xlabel("Time (minutes)")

    plt.yscale("log")
    #plt.ylim(0, 3000)

    plt.plot(time_axis, without_median, color="blue", label="Normal, median")
    plt.legend()
    plt.savefig('plots/log_normal_median.png', bbox_inches='tight')
    plt.plot(time_axis, without_p95, color="blue", linestyle='dotted', label="Normal, 95th percentile")
    plt.legend()
    plt.savefig('plots/log_normal_p95.png', bbox_inches='tight')
    plt.plot(time_axis, with_median, color="red", label="Tuner, median")
    plt.legend()
    plt.savefig('plots/log_tuner_median.png', bbox_inches='tight')
    plt.plot(time_axis, with_p95, color="red", linestyle='dotted', label="Tuner, 95th percentile")
    plt.legend()
    plt.savefig('plots/log_tuner_p95.png', bbox_inches='tight')


def plot_with_without(pattern_length, av_with, av_without):
    plot_cost(pattern_length, av_with["cost"], av_without["cost"])
    plot_latency(pattern_length, av_with["latency_median"], av_with["latency_p95"], av_without["latency_median"], av_without["latency_p95"])


def plot_load_pattern(folder, artillery_file_name):
    time = 0
    with open(folder + artillery_file_name) as file:
        artillery_file = json.load(file)
    print(artillery_file)
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
    plt.savefig('plots/load.png', bbox_inches='tight')




def calc_cost(pattern_length, cost_list):
    average_cost = sum(cost_list)/len(cost_list)
    return average_cost*(pattern_length.seconds/3600.0)


def do_everything(with_artillery_files, without_artillery_files, folder):
    plot_load_pattern(folder, with_artillery_files[0])
    pattern_length, av_with = average_artillery_files(folder, with_artillery_files)
    pattern_length, av_without = average_artillery_files(folder, without_artillery_files)
    plot_with_without(pattern_length, av_with, av_without)

    with_cost = calc_cost(pattern_length, av_with["cost"])
    without_cost = calc_cost(pattern_length, av_without["cost"])
    saved = without_cost-with_cost
    percentage_saved = saved/without_cost*100

    with open("plots/cost.txt", "w+") as file:
        file.write("with: {}\n".format(with_cost))
        file.write("without: {}\n".format(without_cost))
        file.write("saved: {}\n".format(saved))
        file.write("percentage saved: {}".format(percentage_saved))
    print("with: {}".format(with_cost))
    print("without: {}".format(without_cost))
    print("saved: {}".format(saved))
    print("percentage saved: {}".format(percentage_saved))


def main():
    sns.set()
    folder = "/media/thijs/SSD2/University/2018-2019/Thesis/DynamicTopologySelection/execution_results/"


    long_peaks_with_artillery_file_names = ["long_peaks_with_1", "long_peaks_with_2"]
    long_peaks_without_artillery_file_names = ["long_peaks_without_1", "long_peaks_without_2", "long_peaks_without_3"]


    small_peaks_with_artillery_file_names = ["small_peaks_with", "small_peaks_with_2"]
    small_peaks_without_artillery_file_names = ["small_peaks_without_2", "small_peaks_without_3"]

    small_peaks_with_no_migration = ["small_peaks_with_no_migration_1", "small_peaks_with_no_migration_2"]

    valley_with_artillery_file_names = ["valley_with_1", "valley_with_2"]
    valley_without_artillery_file_names = ["valley_1", "valley_2", "valley_3"]

    valley_with_node_scaling_disabled_artillery_file_names = ["valley_with_node_deletion_off_1"]



    do_everything(valley_with_artillery_file_names, valley_without_artillery_file_names, folder)




artillery_time_correction = datetime.timedelta(hours=2)

if __name__ == '__main__':
    main()
