#!/usr/bin/env python3

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from future import standard_library

standard_library.install_aliases()

import time
import schedule 
import threading

from config import Args
from logger import Logger
from monitor import FritzBox
from publish import FritzPublish
from statistics import FritzStats

def deploy(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()

def start(schedule):
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':

    args = Args()
    logs = Logger(args).get_logger()

    stats = FritzStats(args, logs)
    monitor = FritzBox(args, logs)
    publish = FritzPublish(args, logs, monitor, stats)

    fritz_logs = monitor.get_system_log()
    downtimes = stats.get_downtime(fritz_logs, True)
    logs.warning(f"Errors reported in the past are not published!") 
    logs.info(f"Errors reported in the past: {downtimes}") 
    
    
    # fetching fritzbox logs job
    schedule.every(args.fetch_frequency).seconds.do(deploy, lambda: monitor.start())
    # publishing job
    schedule.every(args.publish_frequency).seconds.do(deploy, lambda: publish.start())
    start(schedule)
