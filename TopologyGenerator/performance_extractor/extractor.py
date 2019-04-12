import datetime

import requests

from initializer.neo4j_queries import get_start_end_times_executions


def get_combinations_already_ran(load):
    """
    MATCH (c:COMBINATION)<-[:RAN]-(e:EXECUTION{load:5})
    WITH c, {start_time: e.start_time, end_time: e.end_time} AS run_time
    RETURN ID(c) AS id, collect(run_time) AS run_times
    """
    # TODO try to find if the pod matrics can be retrieved from prometheus
    pass

def performance_combinations_not_ran(load):
    times = get_start_end_times_executions(load)
    print(times)

    """
    MATCH (c:COMBINATION)
    WHERE NOT (c)<-[:RAN]-(:EXECUTION{load:5})
    WITH c
    MATCH (c) -[:CONTAINS]-> (n:IMAGE)
    RETURN ID(c) AS id, collect(n.container_name) AS containers
    """
    """
    MATCH (e:EXECUTION{load:5}) RETURN e.start_time AS start_time, e.end_time AS end_time
    """


def main():
    performance_combinations_not_ran(5)


    """
    print("extract performance")

    container_names = retrieve_all_container_names()
    print(container_names)
    container_performance = {}

    # To have duplications separate: sum(rate(container_cpu_usage_seconds_total[30s])) by(name)
    # To have duplications together: sum(rate(container_cpu_usage_seconds_total[30s])) by(image)

    # http://localhost:9090/api/v1/query_range?query=sum(rate(container_cpu_usage_seconds_total[30s]))%20by(name)&start=1554813646.721&end=1554813946.721&step=30
    query = "sum(rate(container_cpu_usage_seconds_total[30s]))by(name)"
    start = datetime.datetime.now() - datetime.timedelta(minutes=5)
    end = datetime.datetime.now()
    step = 5
    # TODO maybe add per machine later to this query
    request_query = "http://localhost:9090/api/v1/query_range?query={query}&start={start}&end={end}&step={step}".format(query=query, start=start.timestamp(), end=end.timestamp(), step=step)
    print(request_query)
    response = requests.get(request_query)
    print(response.json())
"""
    


if __name__ == '__main__':
    main()
