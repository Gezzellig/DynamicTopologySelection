import json
import subprocess
import time

from kubernetes_tools import extract_pods
from log import log


def load_settings(settings_file_name):
    log.info("Settings: {}".format(settings_file_name))
    with open(settings_file_name) as file:
        settings = json.load(file)
    return settings

