import csv
import json


def json_to_csv(csv_file_name, json_file):
    with open(csv_file_name, "w+") as csv_file:
        csv_writer = csv.writer(csv_file)
        for measurement in json_file["intermediate"]:
            print(measurement)
            timestamp = measurement["timestamp"]
            started = measurement["scenariosCreated"]
            completed = measurement["scenariosCompleted"]
            median = measurement["latency"]["median"]
            p95 = measurement["latency"]["p95"]
            csv_writer.writerow([timestamp, started, completed, median, p95])


def main():
    folder = "/media/thijs/SSD2/University/2018-2019/Thesis/DynamicTopologySelection/execution_results/"
    json_file_name = "long_peaks_without_2"
    csv_file_name = folder+json_file_name+".csv"
    with open(folder+json_file_name) as file:
        json_file = json.load(file)
    json_to_csv(csv_file_name, json_file)


if __name__ == '__main__':
    main()
