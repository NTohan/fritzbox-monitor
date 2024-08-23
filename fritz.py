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
    tz = None
    logs_dir = None
    fetch_attempts = None
    fetch_frequency = None
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
        self.tz = os.environ["TIMEZONE"]
        self.logs_dir = os.environ["LOG_DIR"]
        self.fetch_attempts = 20
        self.publish_frequency = int(os.environ["MQTT_PUBLISH_INTERVAL"])
        self.fetch_frequency = self.publish_frequency - 10 if self.publish_frequency <= 5 else 5
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
            or self.tz == None\
            or self.fetch_attempts == None\
            or self.fetch_frequency == None\
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
    attempts = 0
    is_job_running = False

    def __init__(self, args):
        self.logs_dir = args.logs_dir

    def timestamp(self):
        return datetime.datetime.now().isoformat()

    # schedule before the publish call
    def fetch(self, args, logs):
        if self.attempts >= args.fetch_attempts:
            # Try reconnecting to Fritzbox
            logs.info(f"Fritzbox logs status after {self.attempts} attempts: failed! fritzbox-monitor will be restarted.")
            os._exit(1)

        if self.is_job_running:
            self.attempts += 1
            self.info("Fritzbox logs status: pending")    
            return

        self.attempts = 0
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


    def clear_fritzbox_logs(self):
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
    logs.info("Connecting to MQTT broker")
    client.connect(args.mqtt_broker, args.mqtt_port)
    return client

def is_connected(args):
    return os.system(f"ping -c 1 {args.fritz_ip} > /dev/null 2>&1") != 0


def prepare_msgs(args, downtime):
    msg = []
    for pattern in args.fritz_detection_rules.split(','):
        err = [(ts, er) for ts, er in downtime if re.match(pattern, er)]
        events = {}
        for ts, _ in err:
            # sum up the events reported at the same time
            events[ts] = events.get(ts, 0) + 1
        data = {}
        data['name'] = "fritzbox-monitor"
        data['tags'] = []
        data['tags'].append({"rule": pattern.replace(" ", "_")})
        data['time'] = max(events, key=events.get) if events else 0
        data['value'] = max(events.values()) if events else 0
        data['connectivity'] = 'on' if is_connected(args) else 'off'
        msg.append((pattern, json.dumps(data)))
    return msg


def publish(args, logs):
    fritz_logs = logs.get_fritzbox_logs()
    fritz = FritzStats(logs, fritz_logs, args.fritz_detection_rules, args.publish_frequency)
    downtime = fritz.get_downtime()
    if downtime is None:
        logs.info("No error to publish")
        return
    msgs = prepare_msgs(args, downtime)
    for err_type, msg in msgs:
        topic = f"{args.topic}/{err_type}".replace(" ", "_")
        result = client.publish(topic, msg)
        status = result[0]
        if status == 0:
            logs.info(f"Sent `{msg}` to topic `{topic}`")
        else:
            logs.info(f"Failed to send `{msg}` to topic {topic}")

    # fetch job should be completed before next publish cycle
    logs.clear_fritzbox_logs()

def deploy(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()

def start(schedule):
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':

    args = Args()

    # set TZ from .env
    os.environ["TZ"] = args.tz
    time.tzset()

    logs = Logs(args)

    client = connect_mqtt(args, logs)
    client.loop_start()

    # fetching fritzbox logs job
    schedule.every(args.fetch_frequency).seconds.do(deploy, lambda: logs.fetch(args, logs))
    
    # publishing job
    schedule.every(args.publish_frequency).seconds.do(deploy, lambda: publish(args, logs))
    start(schedule)
