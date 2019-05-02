import datetime
import json
import sys

import requests

from initializer.neo4j_queries import execute_query_function


def retreive_executions_on_load_command(tx, load, load_delta):
    return tx.run("MATCH (e:Execution) WHERE $load_min <= e.load < $load_max return timestamp(e.start_time) as start_time, timestamp(e.end_time) as end_time", load_min=load-load_delta, load_max=load+load_delta)


def retrieve_price(settings, end_time):
    request_url = "http://{prometheus}/api/v1/query?query=sum(machine_cpu_cores)*{price_cpu}%2B(sum(machine_memory_bytes)/2^30)*{price_mem}&time={time}".format(prometheus=settings["prometheus_address"], price_cpu=settings["price_per_core"], price_mem=settings["price_per_gb"], time=end_time.timestamp())
    print(request_url)
    result = requests.get(request_url).json()
    print(result)
    return result["data"]["result"][0]["value"][1]


def retrieve_executions_on_load(settings, load):
    load_delta = 100000
    result = execute_query_function(retreive_executions_on_load_command, load, load_delta)
    for execution in result:
        start_time = datetime.datetime.fromtimestamp(execution["start_time"]/1000)
        end_time = datetime.datetime.fromtimestamp(execution["end_time"] / 1000)
        print(start_time)
        print(end_time)
        print(retrieve_price(settings, end_time))



def main():
    print("Time to select most efficient execution!")
    settings_file_name = sys.argv[1]
    print("Settings: {}".format(settings_file_name))
    with open(settings_file_name) as file:
        settings = json.load(file)
    #retrieve_price(settings, datetime.datetime.now())
    retrieve_executions_on_load(settings, 100000)


if __name__ == '__main__':
    main()
