from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from builtins import open
from future import standard_library
standard_library.install_aliases()
from builtins import object

import re
from datetime import datetime


class FritzStats(object):
    """
    Manages statistics for a FRITZ!Box router.
    """

    def __init__(self, args, logs):
        self.args = args
        self.logs = logs
        self.patterns = args.fritz_detection_rules.split(',')


    def get_downtime(self, fritz_logs):
        """
        Get the times when the error events occurred
        :return: list of patter and events
        """
        return self._filter(fritz_logs)

    def check_event(self, event_time):
        now = datetime.now().strftime("%d.%m.%y %H:%M:%S")
        result =  datetime.strptime(now, "%d.%m.%y %H:%M:%S") - event_time
        # map error events happened in the last 120s to current publish cycle   
        return int(result.seconds) > 120 #seconds
    
    def _filter(self, fritz_logs):
        # TODO: remove, added only for testing purposes
        fritz_logs += '\n16.08.24 15:44:10 PPPoE error: Timeout.'
        fritz_logs += '\n16.08.24 15:52:12 PPPoE error: Timeout.'
        fritz_logs += '\n16.08.24 15:52:12 PPPoE error: Timeout.'
        fritz_logs += '\n16.08.24 15:52:12 PPPoE error: Timeout.'
        fritz_logs += '\n27.08.24 15:56:12 Timeout during PPP negotiation.'

        timestamp_data = []
        for pattern in self.patterns:
            lines = re.split('\n', fritz_logs)
            regex = re.compile("^(.*) %s." % pattern)
            self.logs.info(f"checking against rule: {regex}")
            for line in lines:
                if line:
                    try:
                        ts_str = regex.search(line).group(1)  # timestamp when the event occurred
                        timestamp = datetime.strptime(ts_str, "%d.%m.%y %H:%M:%S")  # format "30.07.19 23:59:12" 
                        if not self.check_event(timestamp):
                            timestamp_data.append((timestamp.isoformat(), pattern))
                        else:
                            self.logs.info(f"skipping error published in the past {timestamp.isoformat(), pattern}")
                    except AttributeError:
                        pass

        self.logs.info(timestamp_data)
        return timestamp_data
    