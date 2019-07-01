"""
Declare some logging configuration, such that it prints pretty
"""
import datetime
import logging
import sys

log = logging.getLogger()
#format_str = '%(asctime)s\t%(levelname)s -- %(filename)s:%(lineno)s -- %(message)s'
format_str = '%(asctime)s\t%(levelname)s -- %(message)s'


logPath = "/media/thijs/SSD2/University/2018-2019/Thesis/DynamicTopologySelection/TopologyGenerator/logs"
fileName = "log_{}".format(datetime.datetime.now()).replace(" ", "_")
fileHandler = logging.FileHandler("{0}/{1}.log".format(logPath, fileName))
fileHandler.setFormatter(logging.Formatter(format_str))
log.addHandler(fileHandler)

console = logging.StreamHandler(sys.stdout)
console.setFormatter(logging.Formatter(format_str))
log.addHandler(console)
log.setLevel(logging.INFO)


def remove_file_handler():
    log.removeHandler(fileHandler)
