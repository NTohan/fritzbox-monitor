from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from future import standard_library
standard_library.install_aliases()

import datetime
import logging

class Logger(object):
    """
    Logger class
    """
    logs_dir = None

    def __init__(self, args):
        self.logs_dir = "/logs"

        if args.logs_level == "DEBUG":
            self.logs_level = logging.DEBUG
        elif args.logs_level == "INFO":
            self.logs_level = logging.INFO
        elif args.logs_level == "WARNING":
            self.logs_level = logging.WARNING
        elif args.logs_level == "ERROR":
            self.logs_level = logging.ERROR
        elif args.logs_level == "CRITICAL":
            self.logs_level = logging.CRITICAL
        else:
            self.logs_level = logging.INFO

        self.filename = f"{datetime.datetime.now().isoformat()}-fritzbox-monitor"
        logging.Formatter()
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(encoding='utf-8', 
                            level=self.logs_level,
                            format="%(asctime)s [%(filename)s] [%(levelname)s]  %(message)s",
                            handlers=[
                                logging.FileHandler("{0}/{1}.log".format(self.logs_dir, self.filename)),
                                logging.StreamHandler()
                            ]
                            )
    
    def get_logger(self):
        return self.logger