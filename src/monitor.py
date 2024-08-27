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
    fritz_logs = None
    attempts = 0
    is_job_running = False

    def __init__(self, args, logs):
        super(FritzBox, self).__init__()

        self.args = args
        self.logs = logs

    def get_system_log(self):
        """
        Get the current system log in text format showing device internet events
        :return: system log as a text string
        """
        resp = self.fc.call_action('DeviceInfo', 'GetDeviceLog')
        return resp["NewDeviceLog"]

    
    # schedule before the publish call
    def start(self):
        if self.attempts >= self.args.fetch_attempts:
            # Try reconnecting to Fritzbox
            self.logs.info(f"Fritzbox logs status after {self.attempts} attempts: failed! fritzbox-monitor will be restarted.")
            os._exit(1)

        if self.is_job_running:
            self.attempts += 1
            self.logs.info("Fritzbox logs status: pending")    
            return

        self.attempts = 0
        self.is_job_running = True

        self.logs.info("Fritzbox logs status: fetching")
        fc = fritzconnection.FritzConnection(
            address=self.args.fritz_ip,
            port=None,
            user=self.args.fritz_username,
            password=self.args.fritz_password,
        )
        self.fc = fc

        self.fritz_logs = self.get_system_log()
        self.logs.info("Fritzbox logs status: collected")
        self.is_job_running = False


    def clear_fritzbox_logs(self):
        self.fritz_logs = None

    def get_fritzbox_logs(self):
        if self.fritz_logs is None:
            raise Exception("Fritzbox logs status: not available")
        return self.fritz_logs