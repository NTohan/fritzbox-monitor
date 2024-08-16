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
import random
import schedule 
import datetime
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from monitor import FritzBox
from statistics import FritzStats

class Args():
    topic = None
    logsdir = None
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
        self.topic = "tele/fritzbox/SENSOR"
        self.logsdir = os.environ["LOG_DIR"]
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
            or self.logsdir == None\
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

def _fetch_logs(args):
    fritz = FritzBox(
        address=args.fritz_ip,
        port=None,
        user=args.fritz_username,
        password=args.fritz_password,
    )

    return fritz.get_system_log()

    
def connect_mqtt(args):

    client_id = f'fritzbox-{random.randint(0, 1000)}'

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(args.mqtt_username, args.mqtt_password)
    client.on_connect = on_connect
    print ("Connecting to mqtt broker...")
    client.connect(args.mqtt_broker, args.mqtt_port)
    return client

def _prepare_msg(args, downtime):
    msg = []
    timestamp = datetime.datetime.now().isoformat()
    for pattern in args.fritz_detection_rules.split(','):
        err = [(ts, er) for ts, er in downtime if re.match(pattern, er)]
    #for ts, er in downtime:
        d = {}
        for ts, er in err:
            d[ts] = d.get(ts, 0) + 1
        print(d)
        msg.append(f"Time: {timestamp}, type: {pattern}, downtime: {str(d)}")
    #print(d)
    print(msg)
    return msg


def _publish(args):
    if not hasattr(_publish, "count"):
        _publish.count = 1  # it doesn't exist yet, so initialize it
    logs = _fetch_logs(args)
    fritz = FritzStats(logs, args.fritz_detection_rules)
    downtime = fritz.get_downtime()
    print(downtime)
    msgs = _prepare_msg(args, downtime)
    for msg in msgs:
        result = client.publish(args.topic, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{args.topic}`")
        else:
            print(f"Failed to send message to topic {args.topic}")
    _publish.count += 1

def _start(schedule):
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':

    args = Args()

    client = connect_mqtt(args)
    client.loop_start()

    schedule.every(args.publish_frequency).seconds.do(lambda: _publish(args))
    _start(schedule)
