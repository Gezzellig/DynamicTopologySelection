import datetime
import json
import sys

from SmartKubernetesSchedular.LoadExtractorBytesIn import LoadExtractorBytesIn
from SmartKubernetesSchedular.extract_pods import extract_pods
from initializer.neo4j_queries import execute_query_function


def add_time_window_command(tx, load, pods, start_time, time_window):
    return tx.run("CREATE (e:Execution {load:$load, start_time:$start_time, end_time:$end_time}) \
                    with e \
                    UNWIND $pods as pod \
                    MERGE (e)-[:HasNode]->(n:NODE {name:pod.node_name}) \
                    WITH n, pod.pod_generate_name as pod_generate_name, pod.pod_name as pod_name \
                    MERGE (p:Pod{generate_name:pod_generate_name}) \
                    WITH n, p, pod_name \
                    CREATE (n)-[:Ran{name:pod_name}]->(p)",
                  load=load, pods=pods, start_time=start_time, end_time=start_time+time_window)


def retrieve_times(window_size):
    #TODO: add proper implementation
    end_time = datetime.datetime.now()
    start_time = end_time - window_size
    return start_time, end_time


def create_time_window(settings, time_window, load_extractor):
    start_time, end_time = retrieve_times(time_window)
    load = load_extractor.extract_load(start_time, time_window, settings)
    print(load)
    pods = extract_pods(settings)
    execute_query_function(add_time_window_command, load, pods, start_time, time_window)


def main():
    print("starting add_time_window")
    settings_file_name = sys.argv[1]
    print("Settings: {}".format(settings_file_name))
    with open(settings_file_name) as file:
        settings = json.load(file)
    create_time_window(settings, datetime.timedelta(minutes=5), LoadExtractorBytesIn())


if __name__ == '__main__':
    main()
