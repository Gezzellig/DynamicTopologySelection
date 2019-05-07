import datetime
import json
import sys

from SmartKubernetesSchedular.LoadExtractorBytesIn import LoadExtractorBytesIn
from SmartKubernetesSchedular.extract_pods import extract_pods
from initializer.neo4j_queries import execute_query_function


def add_time_window_command(tx, load, pods, start_time, end_time):
    return tx.run("CREATE (e:Execution {load:$load, start_time:datetime({ epochMillis: $start_time }), end_time:datetime({ epochMillis: $end_time})}) \
                    with e \
                    UNWIND $pods as pod \
                    MERGE (e)-[:HasNode]->(n:NODE {name:pod.node_name}) \
                    WITH n, pod.pod_generate_name as pod_generate_name, pod.pod_name as pod_name \
                    MERGE (p:Pod{generate_name:pod_generate_name}) \
                    WITH n, p, pod_name \
                    CREATE (n)-[:Ran{name:pod_name}]->(p)",
                  load=load, pods=pods, start_time=int(start_time.timestamp()*1000), end_time=int(end_time.timestamp()*1000))


def create_time_window(end_time, load, settings, time_window):
    pods = extract_pods(settings)
    execute_query_function(add_time_window_command, load, pods, end_time-time_window, end_time)
    return load


def main():
    print("starting add_time_window")
    settings_file_name = sys.argv[1]
    print("Settings: {}".format(settings_file_name))
    with open(settings_file_name) as file:
        settings = json.load(file)
    create_time_window(datetime.datetime.now(), 10000, settings, datetime.timedelta(minutes=5))


if __name__ == '__main__':
    main()
