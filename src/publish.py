from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from future import standard_library
standard_library.install_aliases()

import os
import re
import json
import random
from paho.mqtt import client as mqtt_client

from statistics import FritzStats

class FritzPublish(object):
    """
    Publishes FRITZ!Box errors to MQTT Broker.
    """

    def __init__(self, args, logs, fetch):
        self.logs = logs
        self.args = args
        self.fetch = fetch
        self.last_msg_status = False
        
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
        client.loop_start()
        self.client = client

        self.stats = FritzStats(args, logs)

    def is_connected(self):
        return os.system(f"ping -c 2 -w 2 {self.args.fritz_ip} > /dev/null 2>&1") == 0
    
        
    def prepare_msgs(self, downtime):
        msg = []
        for pattern in self.args.fritz_detection_rules.split(','):
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
            msg.append((pattern, json.dumps(data)))
        return msg

    def prepare_msg(self):
        data = {}
        data['name'] = "fritzbox-monitor"
        data['tags'] = []
        data['tags'].append({"rule": "connectivity"})
        data['value'] = 'ON' if self.is_connected() and self.last_msg_status  else 'OFF'
        return json.dumps(data)


    def send(self, topic, msg):
        result = self.client.publish(topic, msg)
        status = result[0]
        if status == 0:
            self.last_msg_status = True
            self.logs.info(f"Sent `{msg}` to topic `{topic}`")
        else:
            self.last_msg_status = False
            self.logs.info(f"Failed to send `{msg}` to topic {topic}")

    def start(self):
        fritz_logs = self.fetch.get_fritzbox_logs()
        downtime = self.stats.get_downtime(fritz_logs)
        if downtime is None:
            self.logs.info("No error to publish")
            return
        msgs = self.prepare_msgs(downtime)
        for rule, msg in msgs:
            topic_rules = f"{self.args.topic_rules}/{rule}".replace(" ", "_")
            # publish rule status
            self.send(topic_rules, msg)

        # publish connectivity status
        self.send(self.args.topic_connectivity, self.prepare_msg())

        # fetch job should be completed before next publish cycle
        self.fetch.clear_fritzbox_logs()