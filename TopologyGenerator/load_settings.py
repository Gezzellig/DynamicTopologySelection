import json


def load_settings(settings_file_name):
    print("Settings: {}".format(settings_file_name))
    with open(settings_file_name) as file:
        settings = json.load(file)
    return settings
