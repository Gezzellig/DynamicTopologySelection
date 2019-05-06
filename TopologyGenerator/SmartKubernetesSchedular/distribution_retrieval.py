import datetime

import requests

from initializer.neo4j_queries import execute_query_function


def retreive_executions_on_load_command(tx, load, load_delta):
    return tx.run("MATCH (e:Execution) WHERE $load_min <= e.load < $load_max return timestamp(e.start_time) as start_time, timestamp(e.end_time) as end_time", load_min=load-load_delta, load_max=load+load_delta)


def retrieve_executions_on_load(load, settings):
    executions = []
    load_delta = settings["load_delta"]
    result = execute_query_function(retreive_executions_on_load_command, load, load_delta)
    for execution in result:
        start_time = datetime.datetime.fromtimestamp(execution["start_time"]/1000)
        end_time = datetime.datetime.fromtimestamp(execution["end_time"] / 1000)
        print(start_time)
        executions.append({"start_time": start_time,
                           "end_time": end_time})
    return executions


def retrieve_price(end_time, settings):
    request_url = "http://{prometheus}/api/v1/query?query=sum(machine_cpu_cores)*{price_cpu}%2B(sum(machine_memory_bytes)/2^30)*{price_mem}&time={time}".format(prometheus=settings["prometheus_address"], price_cpu=settings["price_per_core"], price_mem=settings["price_per_gb"], time=end_time.timestamp())
    print(request_url)
    result = requests.get(request_url).json()
    print(result)
    return result["data"]["result"][0]["value"][1]


def select_cheapest_executions(executions, settings):
    cheapest = []
    min_cost = float("+inf")
    for execution in executions:
        end_time = execution["start_time"]
        cur_cost = float(retrieve_price(end_time, settings))
        if cur_cost < min_cost:
            cheapest = []
            min_cost = cur_cost
        if cur_cost == min_cost:
            cheapest.append(execution)
    print("min cost: {}".format(min_cost))
    return cheapest


def get_cheapest_distributions(load, settings):
    executions = retrieve_executions_on_load(load, settings)
    select_cheapest_executions(executions, settings)

