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

    # fetching fritzbox logs job
    fetch = FritzBox(args, logs)
    schedule.every(args.fetch_frequency).seconds.do(deploy, lambda: fetch.start())

    # publishing job
    publish = FritzPublish(args, logs, fetch)
    schedule.every(args.publish_frequency).seconds.do(deploy, lambda: publish.start())
    start(schedule)
