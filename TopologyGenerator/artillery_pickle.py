import csv
import datetime
import json
import math
import pickle

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


def store_cost(start_time, end_time, pickle_file_name):
    step_per_hour = 14
    step = math.floor(((end_time - start_time).seconds / 3600) * step_per_hour)
    #print(step)
    cpu_cost = 0.0280
    memory_cost = 0.0038
    query = "http://localhost:9090/api/v1/query_range?query=sum(node%3Anode_num_cpu%3Asum)*{cpu}%2Bsum(node%3Anode_memory_bytes_total%3Asum)*({memory}%2F2%5E30)&start={start}&end={end}&step={step}"
    filled_query = query.format(start=start_time.timestamp(), end=end_time.timestamp(), step=step, cpu=cpu_cost,
                                memory=memory_cost)
    #print(filled_query)
    result = requests.get(filled_query).json()
    #print(result)
    with open(pickle_file_name, 'wb') as pickle_file:
        pickle.dump(result, pickle_file)


def store_cost_per_node(start_time, end_time, pickle_file_name):
    step_per_hour = 14
    step = math.floor(((end_time - start_time).seconds / 3600) * step_per_hour)
    # print(step)
    cpu_cost = 0.0280
    memory_cost = 0.0038
    query = "http://localhost:9090/api/v1/query_range?query=node%3Anode_num_cpu%3Asum*{cpu}%2Bnode%3Anode_memory_bytes_total%3Asum*({memory}%2F2%5E30)&start={start}&end={end}&step={step}"
    filled_query = query.format(start=start_time.timestamp(), end=end_time.timestamp(), step=step, cpu=cpu_cost,
                                memory=memory_cost)
    # print(filled_query)
    cost_per_node = requests.get(filled_query).json()

    query = "http://localhost:9090/api/v1/query_range?query=sum(kube_pod_container_resource_requests_cpu_cores)by(node)&start={start}&end={end}&step={step}"
    filled_query = query.format(start=start_time.timestamp(), end=end_time.timestamp(), step=step)

    cpu_requested_per_node = requests.get(filled_query).json()

    """print("cost node")
    for node in cost_per_node["data"]["result"]:
        print(node["metric"]["node"], len(node["values"]))

    print("cpu")
    for node in cpu_requested_per_node["data"]["result"]:
        if "node" in node["metric"]:
            print(node["metric"]["node"], len(node["values"]))
    print("ok")"""

    per_node = {
        "cost": cost_per_node,
        "cpu_requested": cpu_requested_per_node
    }
    with open(pickle_file_name, 'wb') as pickle_file:
        pickle.dump(per_node, pickle_file)


def load_cost(pickle_file_name):
    with open(pickle_file_name, 'rb') as pickle_file:
        result = pickle.load(pickle_file)
    cost = []
    for value in result["data"]["result"][0]["values"]:
        cost.append(float(value[1]))
    return cost


def to_pickle(path_name):
    artillery_file_name_extension = "artillery.out"
    pickle_file_name_extension = "cost.pck"
    pickle_per_node_file_name_extension = "cost_per_node.pck"

    try:
        with open(path_name + artillery_file_name_extension) as file:
            artillery_file = json.load(file)
        start_time, end_time, warmup = get_start_end_time_warmup(artillery_file)
        store_cost(start_time, end_time, path_name + pickle_file_name_extension)
        store_cost_per_node(start_time, end_time, path_name + pickle_per_node_file_name_extension)
    except FileNotFoundError:
        print("NOT FOUND: {}".format(path_name))


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
                ["run1/", "run2/", "run3/", "run5/"]
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
                ["run1/", "run2/", "run3/", "run5/"],
            "without_tuner/":
                ["run1/", "run2/", "run3/", "run5/"],
            "with_tuner_no_node_removal/":
                ["run1/", "run2/", "run3/", "run5/"]
        }
    }

    for pattern, types in patterns.items():
        for type, runs in types.items():
            for run in runs:
                to_pickle(main_folder+pattern+type+run)








artillery_time_correction = datetime.timedelta(hours=2)

if __name__ == '__main__':
    main()
