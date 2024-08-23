from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from builtins import open
from future import standard_library
standard_library.install_aliases()
from builtins import object
import glob
import re
from datetime import datetime, timedelta, timezone

import pandas as pd


class FritzStats(object):
    """
    Manages statistics for a FRITZ!Box router.
    """

    def __init__(self, logs, fritz_logs, fritz_detection_rules, publish_frequency):
        self.logs = logs
        self.fritz_logs = fritz_logs
        self.fritz_detection_rules = fritz_detection_rules
        self.publish_frequency = publish_frequency
        # TODO: remove, added only for testing purposes
        self.fritz_logs += '\n16.08.24 15:44:10 PPPoE error: Timeout.'
        self.fritz_logs += '\n16.08.24 15:52:12 PPPoE error: Timeout.'
        self.fritz_logs += '\n16.08.24 15:52:12 PPPoE error: Timeout.'
        self.fritz_logs += '\n16.08.24 15:52:12 PPPoE error: Timeout.'
        self.fritz_logs += '\n16.08.24 15:52:12 Timeout during PPP negotiation.'

    def get_downtime(self):
        """
        Get the times when the router did not have an internet connection.
        :return: dataframe of the form timestamp, event (event is always 1)
        """
        # TODO: make rules list configurable
        return self._read_logs(self.fritz_detection_rules.split(','))

    def check_event(self, event_time):
        now = datetime.now().strftime("%d.%m.%y %H:%M:%S")
        result =  datetime.strptime(now, "%d.%m.%y %H:%M:%S") - event_time
        # map error events happened in the last 300 secs (30s (default) * 10) to current publish cycle   
        return int(result.seconds) > self.publish_frequency * 10
    
    def _read_logs(self, patterns):
        timestamp_data = []
        for pattern in patterns:
            lines = re.split('\n', self.fritz_logs)
            regex = re.compile("^(.*) %s." % pattern)
            self.logs.info(f"checking against rule: {regex}")
            for line in lines:
                if line:
                    try:
                        ts_str = regex.search(line).group(1)  # timestamp when the event occurred
                        timestamp = datetime.strptime(ts_str, "%d.%m.%y %H:%M:%S")  # format "30.07.19 23:59:12" 
                        self.logs.info(f"pattern match: {ts_str}") 
                        if not self.check_event(timestamp):
                            timestamp_data.append((timestamp.isoformat(), pattern))
                        else:
                            self.logs.info(f"skipping error published in the past {timestamp.isoformat(), pattern}")
                    except AttributeError:
                        pass

        self.logs.info(timestamp_data)
        return timestamp_data
 # type: ignore