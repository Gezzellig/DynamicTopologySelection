import datetime
import pickle


def get_date_time_string(date_string):
    return datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")


def get_node_removals_from_log(log_file_name):
    node_removals = []
    with open(log_file_name, "r") as file:
        lines = file.readlines()
        for line in lines:
            line = line.rstrip()
            split1 = line.split("--")
            if len(split1) > 1 and split1[1].startswith(" NODE_REMOVAL="):
                node_name = split1[1].split("=")[1]
                date_string = split1[0].split(",")[0]
                date = get_date_time_string(date_string)
                node_removals.append((date, node_name))
    return node_removals


def load_pickle_per_node_file(pickle_file_name):
    with open(pickle_file_name, 'rb') as pickle_file:
        result = pickle.load(pickle_file)

    cost_per_node = {}
    for node in result["cost"]["data"]["result"]:
        node_name = node["metric"]["node"]
        cost_per_node[node_name] = [(datetime.datetime.fromtimestamp(value[0]), float(value[1])) for value in node["values"]]

    cpu_request_per_node = {}
    for node in result["cpu_requested"]["data"]["result"]:
        if "node" in node["metric"]:
            node_name = node["metric"]["node"]
            cpu_request_per_node[node_name] = [(datetime.datetime.fromtimestamp(value[0]), float(value[1])) for value in node["values"]]
    return cost_per_node, cpu_request_per_node


def filter_single_node(node_name, cost_per_node, cpu_requested_per_node, node_removals):
    cost = cost_per_node[node_name]
    cpu_requested = cpu_requested_per_node[node_name]
    removals = [time for (time, local_node_name) in node_removals if local_node_name == node_name]
    removing = False
    cpu_requested_counter = 0
    remaining_cost = []
    for (time, single_step_cost) in cost:
        if removing:
            while cpu_requested_counter < len(cpu_requested) and cpu_requested[cpu_requested_counter][0] < time:
                cpu_requested_counter += 1
            if cpu_requested_counter < len(cpu_requested) and cpu_requested[cpu_requested_counter][1] < 0.22:
                continue
            else:
                removing = False
        if removals and time > removals[0]:
            removing = True
            removals.pop()
            continue
        remaining_cost.append((time, single_step_cost))
    return remaining_cost


def filter_cost(cost_per_node, cpu_requested_per_node, node_removals):
    filtered_cost_per_node = {}
    for node_name in cost_per_node.keys():
        filtered_cost_per_node[node_name] = filter_single_node(node_name, cost_per_node, cpu_requested_per_node, node_removals)
    return filtered_cost_per_node


def sum_filtered_cost(cost_per_node_filtered):
    summed_cost = {}
    for filtered_cost in cost_per_node_filtered.values():
        for (time, cost_filtered) in filtered_cost:
            if not time in summed_cost:
                summed_cost[time] = cost_filtered
            else:
                summed_cost[time] += cost_filtered
    return summed_cost


def transform_to_sorted_data(summed_cost):
    return [summed_cost[key] for key in sorted(summed_cost.keys())]


def simulate_node_removal_one_run(run_path):
    node_removals = get_node_removals_from_log(run_path + log_file_name)
    cost_per_node, cpu_requested_per_node = load_pickle_per_node_file(run_path + pickle_per_node_file_name_extension)
    # filter_single_node("gke-demo-cluster-1-default-pool-6f471531-9sbc", cost_per_node, cpu_requested_per_node, node_removals)
    filtered_cost_per_node = filter_cost(cost_per_node, cpu_requested_per_node, node_removals)
    summed_cost = sum_filtered_cost(filtered_cost_per_node)
    return transform_to_sorted_data(summed_cost)


def average_simulated_runs(simulated_runs):
    sum_result = simulated_runs[0]
    for i in range(1, len(simulated_runs)):
        sum_result = [x + y for x, y in zip(sum_result, simulated_runs[i])]
    average = [x/len(simulated_runs) for x in sum_result]
    return average


def get_data_simulating_proper_node_removal(folder, runs):
    simulated_runs = [simulate_node_removal_one_run(folder+run) for run in runs]
    return average_simulated_runs(simulated_runs)


def main():
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

log_file_name = "tuner.log"
pickle_per_node_file_name_extension = "cost_per_node.pck"

if __name__ == '__main__':
    main()