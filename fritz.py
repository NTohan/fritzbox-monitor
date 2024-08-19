#!/usr/bin/env python3

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from future import standard_library
from paho.mqtt import client as mqtt_client

standard_library.install_aliases()
import argparse

import os
import re
import time
import json
import random
import schedule 
import threading
import datetime
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from monitor import FritzBox
from statistics import FritzStats

class Args():
    topic = None
    logs_dir = None
    publish_frequency = None
    mqtt_broker = None
    mqtt_port = None
    mqtt_username = None
    mqtt_password = None
    fritz_ip = None
    fritz_username = None
    fritz_password = None
    fritz_detection_rules = None
    
    def __init__(self):
        self.topic = "tele/fritzbox/monitor/error"
        self.logs_dir = os.environ["LOG_DIR"]
        self.publish_frequency = int(os.environ["MQTT_PUBLISH_INTERVAL"])
        self.mqtt_broker = os.environ["MQTT_BROKER_IP"]
        self.mqtt_port = int(os.environ["MQTT_BROKER_PORT"])
        self.mqtt_username = os.environ["MQTT_USERNAME"]
        self.mqtt_password = os.environ["MQTT_PASSWORD"]
        self.fritz_ip = os.environ["FRITZ_IP"]
        self.fritz_username = os.environ["FRITZ_USERNAME"]
        self.fritz_password = os.environ["FRITZ_PASSWORD"]
        self.fritz_detection_rules = os.environ["FRITZ_DETECTION_RULES"]
        self._check()
    
    def _check(self):
        if self.topic == None\
            or self.logs_dir == None\
            or self.publish_frequency == None\
            or self.mqtt_broker == None\
            or self.mqtt_port == None\
            or self.mqtt_username == None\
            or self.mqtt_password == None\
            or self.fritz_ip == None\
            or self.fritz_username == None\
            or self.fritz_password == None\
            or self.fritz_detection_rules == None:
                raise Exception("Problem occurred while reading .env variables")
        
        if self.publish_frequency < 10:
            raise Exception("Set publish frequency >= 10s")
        

class Logs():
    logs_dir = None
    fritz_logs = None
    is_job_running = False

    def __init__(self, args):
        self.logs_dir = args.logs_dir

    def timestamp(self):
        return datetime.datetime.now().isoformat()

    # schedule before the publish call
    def fetch(self, args):
        if self.is_job_running:
            self.info("Fritzbox logs status: pending")    
            return
        
        self.is_job_running = True

        self.info("Fritzbox logs status: fetching")
        fritz = FritzBox(
            address=args.fritz_ip,
            port=None,
            user=args.fritz_username,
            password=args.fritz_password,
        )

        self.fritz_logs = fritz.get_system_log()
        self.info("Fritzbox logs status: collected")
        self.is_job_running = False


    def clear_fritbox_logs(self):
        self.fritz_logs = None

    def get_fritzbox_logs(self):
        if self.fritz_logs is None:
            raise Exception("Fritzbox logs status: not available")
        return self.fritz_logs

    def info(self, str):
        print(self.timestamp(), str)

    
def connect_mqtt(args, logs):

    client_id = f'fritzbox-{random.randint(0, 1000)}'

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            logs.info(f"Connected to MQTT Broker at {args.mqtt_broker}:{args.mqtt_port}")
        else:
            logs.info(f"Failed to connect, return code {rc}\n")

    client = mqtt_client.Client(client_id)
    client.username_pw_set(args.mqtt_username, args.mqtt_password)
    client.on_connect = on_connect
    logs.info("Connecting to mqtt broker...")
    client.connect(args.mqtt_broker, args.mqtt_port)
    return client

def _prepare_msg(args, logs, downtime):
    msg = []
    timestamp = datetime.datetime.now().isoformat()
    for pattern in args.fritz_detection_rules.split(','):
        err = [(ts, er) for ts, er in downtime if re.match(pattern, er)]
        d = {}
        for ts, er in err:
            d[ts] = d.get(ts, 0) + 1
        logs.info(d)
        data = {}
        data['name'] = "fritzbox-monitor"
        data['tag'] = pattern.replace(" ", "_")
        data['time'] = timestamp
        data['downtime'] = []
        for ts, cnt in d.items():
            data['downtime'].append({"timestamp": ts, "value": cnt})
        msg.append((pattern, json.dumps(data)))
    logs.info(msg)
    return msg


def _publish(args, logs):
    fritz_logs = logs.get_fritzbox_logs()
    fritz = FritzStats(logs, fritz_logs, args.fritz_detection_rules)
    downtime = fritz.get_downtime()
    print(downtime)
    msgs = _prepare_msg(args, logs, downtime)
    for err_type, msg in msgs:
        topic = f"{args.topic}/{err_type}".replace(" ", "_")
        result = client.publish(topic, msg)
        status = result[0]
        if status == 0:
            logs.info(f"Send `{msg}` to topic `{topic}`")
        else:
            logs.info(f"Failed to send message to topic {topic}")

    # fetch job should be completed before next publish cycle
    logs.clear_fritbox_logs()

def deploy(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()

def _start(schedule):
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':

    args = Args()
    logs = Logs(args)

    client = connect_mqtt(args, logs)
    client.loop_start()

    # fetching fritzbox logs job
    schedule.every(5).seconds.do(deploy, lambda: logs.fetch(args))
    
    # publishing job
    schedule.every(args.publish_frequency).seconds.do(deploy, lambda: _publish(args, logs))
    _start(schedule)
