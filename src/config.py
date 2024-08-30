from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from future import standard_library
standard_library.install_aliases()

import os 

class Args(object):
    """
    Manage arguments passed by docker .env file
    """
    topic_rules = None
    tz = None
    logs_level = None
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
        self.topic_rules = "tele/fritzbox/monitor/rule"
        self.topic_connectivity = "tele/fritzbox/monitor/connectivity"
        self.logs_level = os.environ["LOG_LEVEL"]
        self.fetch_attempts = 20
        self.publish_frequency = int(os.environ["MQTT_PUBLISH_INTERVAL"])
        self.fetch_frequency = self.publish_frequency - 10 if (self.publish_frequency - 10) >= 5 else 5
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
        if self.topic_rules == None\
            or self.topic_connectivity == None\
            or self.logs_level == None\
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
        
        if self.publish_frequency < 30:
            raise Exception("Set publish frequency >= 30s")
