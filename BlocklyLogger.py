""""
BlocklyPropLogger manages the application logging process.


"""

import os
import logging
from sys import platform

__author__ = 'Jim Ewald'

# Constants
PLATFORM_MACOS = 'darwin'

path = None

def init(filename = 'BlocklyPropClient.log'):
    global path

    # Set a default log file name
    logfile_name = filename

    # Set correct log file location
    if platform == PLATFORM_MACOS:
        logfile_name = __set_macos_logpath(filename)
        if logfile_name is None:
            return 1

    path = logfile_name

    # Logging path
    try:  # Python 2.7+
        from logging import NullHandler
    except ImportError:
        class NullHandler(logging.Handler):
            def emit(self, record):
                pass

    logging.getLogger(__name__).addHandler(NullHandler())

    # Create a logger
    logger = logging.getLogger('blockly')
    logger.setLevel(logging.DEBUG)

    # create a file handler to log events to the debug level. Log file
    # is overwritten each time the app runs.
    __log_file_location = logfile_name
    handler = logging.FileHandler(logfile_name, mode='w')
    handler.setLevel(logging.DEBUG)

    # create a console handler for error-level events
    console = logging.StreamHandler()
    console.setLevel(logging.ERROR)

    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    console.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(handler)
    logger.addHandler(console)

    logger.info("Logger has been started.")


def __set_macos_logpath(filename):
    user_home = os.path.expanduser('~')
    log_path = user_home + '/Library/Logs/Parallax'

    # Does the log directory exist
    try:
        os.stat(log_path)
        return log_path + '/' + filename

    except OSError:
        # Create a new log path
        try:
            os.makedirs(log_path)

        except OSError:
            return None

    return log_path + '/' + filename
