import logging as _logging
import os
import sys
from pathlib import Path

from appdirs import AppDirs

cache_dir = AppDirs('fprime-extras', 'SterlingPeet').user_cache_dir

log_levels_dict = {
    'DEBUG': _logging.DEBUG,
    'INFO': _logging.INFO,
    'WARNING': _logging.WARNING,
    'ERROR': _logging.ERROR,
    'CRITICAL': _logging.CRITICAL
}

log_levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')

log_file = Path(cache_dir + os.sep + 'fprime_extras.log')
# This is greater than python 3.5, Path support comes in 3.6
if sys.version_info[1] < 6:
    log_file = str(log_file)

log_file_format_str = '%(asctime)s.%(msecs)03d %(levelname)s %(name)s::%(funcName)s:L%(lineno)s - %(message)s'

# TODO: Add formatter class to output legit ISO8601 strings:
#       https://stackoverflow.com/questions/6290739/python-logging-use-milliseconds-in-time-format
#       Else we don't have the timezone in the log line.
