""""
BlocklyPropLogger manages the application logging process.


"""

import os
import logging
from sys import platform

__author__ = 'Jim Ewald'

# Constants
PLATFORM_MACOS = 'darwin'
PLATFORM_WINDOWS = 'win32'

DEFAULT_PATH_MACOS = '/Library/Logs/Parallax'
DEFAULT_PATH_WINDOWS = '/AppData/Local/Parallax'
DEFAULT_PATH_LINUX = '/tmp/'

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
    elif platform == PLATFORM_WINDOWS:
        logfile_name = __set_windows_logpath(filename)

    # Create a logger
    logger = logging.getLogger('blockly')
    logger.setLevel(logging.DEBUG)

    # create a console handler for error-level events
    console = logging.StreamHandler()
    console.setLevel(logging.ERROR)

    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)

    # create a file handler to log events to the debug level if disk logging is active.
    #  Log file is overwritten each time the app runs.
    if not disable_filelogging:
        handler = logging.FileHandler(logfile_name, mode='w')
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # add the handlers to the logger
    logger.addHandler(console)
    logger.info("Logger has been started.")


def __set_macos_logpath(filename):
    user_home = os.path.expanduser('~')
    log_path = user_home + DEFAULT_PATH_MACOS

    # Does the log directory exist
    try:
        result = __verify_logpath(log_path)
        if result is None and __create_logpath(log_path) is None:
            # Try to create the directory in the tmp directory
            log_path = '/tmp'
            result = __verify_logpath(log_path)
            if result is None:
                return 1

        return log_path + '/' + filename
    except OSError:
        return 2


def __set_windows_logpath(filename):
    user_home = os.path.expanduser('~')
    log_path = user_home + DEFAULT_PATH_WINDOWS

    # Does the log directory exist
    try:
        result = __verify_logpath(log_path)

        if result is None and __create_logpath(log_path) is None:
            # try to create the log file in the user's home directory
            log_path = user_home
            result = __verify_logpath(log_path)

            if result is None:
                return 1

        return log_path + '/' + filename
    except OSError:
        return 2


# Create a file path for the log file
def __create_logpath(file_path):
    try:
        os.makedirs(file_path)
        return path
    except OSError as ex:
        print ex.message
        return None


# Verify that the file for the log file exists
def __verify_logpath(file_path):
    try:
        info = os.stat(file_path)
        return info
    except OSError as ex:
        print ex.message
        return None
