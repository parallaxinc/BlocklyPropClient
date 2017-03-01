""""
BlocklyPropLogger manages the application logging process.


"""

import os
import logging
import platform


__author__ = 'Jim Ewald'


# Platform constants
PLATFORM_POSIX = "posix"
PLATFORM_LINUX = 'Linux'
PLATFORM_MACOS = 'MacOS'
PLATFORM_DARWIN = 'Darwin'
PLATFORM_WINDOWS = 'Windows'

# Default log path for each platform
DEFAULT_PATH_MACOS = 'Library/Logs/Parallax'
DEFAULT_PATH_WINDOWS = 'AppData/Local/Parallax'
DEFAULT_PATH_LINUX = 'tmp'

# Resulting path for log file
path = None

loglevel = logging.DEBUG


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
    system = platform.system()
    print("Platform detected is: %", system)

    # A posix system could be a MacOS or a Linux variety
    if system == PLATFORM_POSIX:
        is_mac = platform.mac_ver()
        if is_mac[0] == "":
            # This must be a Linux platform
            system = PLATFORM_LINUX
        else:
            system = PLATFORM_MACOS

    if (system == PLATFORM_MACOS) or (system == PLATFORM_DARWIN):
        logfile_name = __set_macos_logpath(filename)
    elif system == PLATFORM_WINDOWS:
        logfile_name = __set_windows_logpath(filename)
    elif system == PLATFORM_LINUX:
        logfile_name = __set_linux_logpath(filename)

    # Verify that we have a valid location
    if logfile_name is None:
        disable_filelogging = True
    else:
        # Set the module-level path
        path = logfile_name
        print("Sending file logging output to: ", path)

    # Create a logger
    logger = logging.getLogger('blockly')
    logger.setLevel(loglevel)

    # create a console handler for error-level events
    console = logging.StreamHandler()
    console.setLevel(loglevel)

    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)

    # create a file handler to log events to the debug level if disk logging is active.
    #  Log file is overwritten each time the app runs.
    if not disable_filelogging:
        handler = logging.FileHandler(logfile_name, mode='w')
        handler.setLevel(loglevel)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # add the handlers to the logger
    logger.addHandler(console)
    logger.info("Logger has been started.")


# Set the default log file location on a Linux system
def __set_linux_logpath(filename):
    user_home = os.path.expanduser('~')
    print("User home directory is: %s", user_home)
    log_path = user_home + "/" + DEFAULT_PATH_LINUX
    print("Logfile path is %s", log_path)

    # Does the log directory exist
    try:
        result = __verify_logpath(log_path)
        if result is None and __create_logpath(log_path) is None:
            return None
        else:
            return log_path + '/' + filename

    except OSError:
        return None


# Set the default log file location on a MacOS system
def __set_macos_logpath(filename):
    user_home = os.path.expanduser('~')
    print("User home directory is: %s", user_home)
    log_path = user_home + "/" + DEFAULT_PATH_MACOS
    print("Logfile path is %s", log_path)

    # Does the log directory exist
    try:
        result = __verify_logpath(log_path)
        if result is None and __create_logpath(log_path) is None:
            # Try to create the directory in the tmp directory
            log_path = '/tmp'
            result = __verify_logpath(log_path)
            if result is None:
                return None

        return log_path + '/' + filename
    except OSError:
        return None


# Set the default log file location on a Windows system
def __set_windows_logpath(filename):
    user_home = os.path.expanduser('~')
    print("User home directory is: %s", user_home)
    log_path = user_home + "/" + DEFAULT_PATH_WINDOWS
    print("Log file path is: %s", log_path)

    # Does the log directory exist
    try:
        result = __verify_logpath(log_path)

        if result is None and __create_logpath(log_path) is None:
            # try to create the log file in the user's home directory
            log_path = user_home
            result = __verify_logpath(log_path)

            if result is None:
                return None

        return log_path + '/' + filename
    except OSError:
        return None


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
        print("Testing access to: %s", file_path)
        info = os.access(file_path, os.W_OK)
        return info
    except OSError as ex:
        print ex.message
        return None
    except Exception as ex:
        print ex.message
        return None
