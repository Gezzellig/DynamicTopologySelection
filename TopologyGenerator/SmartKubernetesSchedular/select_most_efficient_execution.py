import datetime
import json
import sys

import requests

from initializer.neo4j_queries import execute_query_function






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
