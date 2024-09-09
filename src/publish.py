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
from datetime import datetime
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from paho.mqtt import client as mqtt_client
from statistics import FritzStats

class FritzPublish(object):
    """
    Publishes FRITZ!Box errors to MQTT Broker.
    """

    def __init__(self, args, logs, monitor, stats):
        self.logs = logs
        self.args = args
        self.monitor = monitor
        self.last_msg_status = False

        self.create_client()
        
        self.stats = stats

    def create_client(self):
        if self.args.protocol == 'JSON':
            client_id = f'fritzbox-{random.randint(0, 1000)}'

            def on_connect(client, userdata, flags, rc):
                if rc == 0:
                    self.logs.info(f"Connected to MQTT Broker at {self.args.mqtt_broker}:{self.args.mqtt_port}")
                else:
                    self.logs.info(f"Failed to connect, return code {rc}\n")

            client = mqtt_client.Client(client_id)
            client.username_pw_set(self.args.mqtt_username, self.args.mqtt_password)
            client.on_connect = on_connect
            self.logs.info("Connecting to MQTT broker")
            client.connect(self.args.mqtt_broker, self.args.mqtt_port)
            client.loop_start()
            self.client = client
        elif self.args.protocol == 'LINE':
            self.logs.info("Connecting to InfluxDB")
            influx_url=f"http://{self.args.influxdb_ip}:{self.args.influxdb_port}"
            self.client = InfluxDBClient(url="http://172.28.150.205:8086", token=self.args.influxdb_token, org=self.args.influxdb_org)
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
            self.logs.info(f"Connected to InfluxDB at {influx_url}")
        else:
            os.exit("-1")
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

            data = []
            data.append( 
            {
                    "measurement": "fritzbox-monitor",
                    "tags": {
                            "rule": pattern.replace(" ", "_")
                    },
                    "fields": {
                            "count": max(events.values()) if events else 0
                    },
                    #"time": max(events, key=events.get) if events else datetime.now().isoformat()
                    }
            )    
            msg.append((pattern, data))
        return msg

    def prepare_msg(self):
        data = []
        data.append( 
        {
                "measurement": "fritzbox-monitor",
                "tags": {
                        "rule": "connectivity"
                },
                "fields": {
                        "state": 'ON' if self.is_connected() and self.last_msg_status  else 'OFF'
                },
                #"time": datetime.now().isoformat()
                }
        )
        return data


    def send(self, topic, msg):
        if self.args.protocol == 'JSON':
            result = self.client.publish(topic, json.dumps(msg))
            status = result[0]
            if status == 0:
                self.last_msg_status = True
                self.logs.info(f"Sent `{msg}` to topic `{topic}`")
            else:
                self.last_msg_status = False
                self.logs.info(f"Failed to send `{msg}` to topic {topic}")
        elif self.args.protocol == 'LINE':
            try:
                self.write_api.write(bucket=self.args.influxdb_bucket, record=msg, time_precision='ms', batch_size=10000, protocol='json')
                self.last_msg_status = True
                self.logs.info(f"Sent `{msg}` to InfluxDB")
            except Exception as e:
                self.logs.error(f"Failed to send `{msg}` to InfluxDB with error msg {e}")
        else:
            self.logs.critical(f"Protocol not supported: {self.args.protocol}")
            os._exit(1)

    def start(self, event):
        event.wait()
        fritz_logs = self.monitor.get_fritzbox_logs()
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
        self.monitor.clear_fritzbox_logs()
        event.clear()