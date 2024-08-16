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
from datetime import datetime

import pandas as pd


class FritzStats(object):
    """
    Manages statistics for a FRITZ!Box router.
    """

    def __init__(self, logs, fritz_detection_rules):
        self.logs = logs
        self.fritz_detection_rules = fritz_detection_rules
        # TODO: remove, added only for testing purposes
        self.logs += '\n16.08.24 15:44:10 PPPoE error: Timeout.'
        self.logs += '\n16.08.24 15:52:12 PPPoE error: Timeout.'
        self.logs += '\n16.08.24 15:52:12 PPPoE error: Timeout.'
        self.logs += '\n16.08.24 15:52:12 PPPoE error: Timeout.'
        self.logs += '\n16.08.24 15:52:12 Timeout during PPP negotiation.'

    def get_downtime(self):
        """
        Get the times when the router did not have an internet connection.
        :return: dataframe of the form timestamp, event (event is always 1)
        """
        # TODO: make rules list configurable
        return self._read_logs(self.fritz_detection_rules.split(','))

    def _read_logs(self, patterns):
        timestamp_data = []
        print (self.logs)
        for pattern in patterns:
            lines = re.split('\n', self.logs)
            regex = re.compile("^(.*) %s." % pattern)
            print("checking against rule: ", regex)
            for line in lines:
                if line:
                    try:
                        ts_str = regex.search(line).group(1)  # timestamp when the event occurred
                        timestamp = datetime.strptime(ts_str, "%d.%m.%y %H:%M:%S").isoformat()  # format "30.07.19 23:59:12" 
                        timestamp_data.append((timestamp, pattern))
                        print("pattern match", ts_str)
                    except AttributeError:
                        pass

        # TODO: remove, added for testing only
        print(timestamp_data)
        return timestamp_data
 # type: ignore