from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import super

from future import standard_library

standard_library.install_aliases()
from builtins import object

import os
import fritzconnection


class FritzBox(object):
    """
    Accesses FRITZ!Box system logs 
    """
    fc = None
    agrs = None
    logs = None
    attempts = 0
    fritz_logs = None

    def __init__(self, args, logs):
        super(FritzBox, self).__init__()

        self.args = args
        self.logs = logs
        self.fc = fritzconnection.FritzConnection(
            address=self.args.fritz_ip,
            port=None,
            user=self.args.fritz_username,
            password=self.args.fritz_password,
        )
        self.logs.info(f"Connected to {self.fc}")
        
    def get_system_log(self):
        """
        Get the current system log in text format showing device internet events
        :return: system log as a text string
        """
        self.logs.info("Fritzbox logs status: fetching")
        resp = self.fc.call_action('DeviceInfo', 'GetDeviceLog')
        logs = resp["NewDeviceLog"]
        self.logs.debug(f"Fritzbox logs: {logs}")
        self.logs.info("Fritzbox logs status: collected")
        return logs if bool(logs and logs.strip()) else None

    
    # schedule before the publish call
    def start(self, event):
        if self.attempts >= self.args.fetch_attempts:
            # Try reconnecting to Fritzbox
            self.logs.critical(f"Fritzbox logs status after {self.attempts} attempts: failed! fritzbox-monitor will be restarted.")
            os._exit(1)

        self.fritz_logs = self.get_system_log()
        event.set()

    def clear_fritzbox_logs(self):
        self.fritz_logs = None

    def get_fritzbox_logs(self):
        if self.fritz_logs is None:
            self.attempts += 1
            raise Exception("Fritzbox logs status: not available")
        self.attempts = 0
        return self.fritz_logs