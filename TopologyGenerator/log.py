"""
Declare some logging configuration, such that it prints pretty
"""
import datetime
import logging
import sys
import os

def get_log_total_name():
    for i in range(1, len(sys.argv)):
        if sys.argv[i] == "-l":
            return sys.argv[i+1]
    file_name = "log_{}".format(datetime.datetime.now()).replace(" ", "_")
    log_path = "/media/thijs/SSD2/University/2018-2019/Thesis/DynamicTopologySelection/TopologyGenerator/logs"
    return "{0}/{1}.log".format(log_path, file_name)


log = logging.getLogger()
#format_str = '%(asctime)s\t%(levelname)s -- %(filename)s:%(lineno)s -- %(message)s'
format_str = '%(asctime)s\t%(levelname)s -- %(message)s'


total_log_name = get_log_total_name()
print("total log name:", total_log_name)
if os.path.exists(total_log_name):
  os.remove(total_log_name)
fileHandler = logging.FileHandler(total_log_name)
fileHandler.setFormatter(logging.Formatter(format_str))
log.addHandler(fileHandler)

console = logging.StreamHandler(sys.stdout)
console.setFormatter(logging.Formatter(format_str))
log.addHandler(console)
log.setLevel(logging.INFO)





def remove_file_handler():
    log.removeHandler(fileHandler)
