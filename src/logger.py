from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from future import standard_library
standard_library.install_aliases()

import datetime

class Logger(object):
    """
    Logger class
    """
    logs_dir = None

    def __init__(self, args):
        self.logs_dir = args.logs_dir

    def timestamp(self):
        return datetime.datetime.now().isoformat()

    def info(self, str):
        print(self.timestamp(), str)
