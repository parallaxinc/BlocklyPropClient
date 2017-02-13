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

    # Set NullHandler as a default
    try:  # Python 2.7+
        from logging import NullHandler
    except ImportError:
        class NullHandler(logging.Handler):
            def emit(self, record):
                pass

    logging.getLogger(__name__).addHandler(NullHandler())

    # Set a default log file name
    logfile_name = filename
    disable_filelogging = False

    # Set correct log file location
    if platform == PLATFORM_MACOS:
        logfile_name = __set_macos_logpath(filename)
        if logfile_name is None:
            disable_filelogging = True
        else:
            # Set the module-level path
            path = logfile_name

    # Create a logger
    logger = logging.getLogger('blockly')
    logger.setLevel(logging.DEBUG)

    # create a file handler to log events to the debug level. Log file
    # is overwritten each time the app runs.
    if not disable_filelogging:
        handler = logging.FileHandler(logfile_name, mode='w')
        handler.setLevel(logging.DEBUG)

    # create a console handler for error-level events
    console = logging.StreamHandler()
    console.setLevel(logging.ERROR)

    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    if not disable_filelogging:
        handler.setFormatter(formatter)

    console.setFormatter(formatter)

    # add the handlers to the logger
    if not disable_filelogging:
        logger.addHandler(handler)

    logger.addHandler(console)
    logger.info("Logger has been started.")


def __set_macos_logpath(filename):
    user_home = os.path.expanduser('~')
    log_path = user_home + '/Library/Logs/Parallax'

    # Does the log directory exist
    try:
        result = __verify_macos_logpath(log_path)
        if result is None and __create_macos_logpath(log_path) is None:
        # Try to create the directory
            log_path = '/tmp'
            result = __verify_macos_logpath(log_path)
            if result is None:
                return 1

        return log_path + '/' + filename
    except OSError:
        return 2


def __verify_macos_logpath(file_path):
    try:
        info = os.stat(file_path)
        return info
    except OSError as ex:
        print ex.message
        return None


def __create_macos_logpath(file_path):
    try:
        os.makedirs(file_path)
        return path
    except OSError as ex:
        print ex.message
        return None
