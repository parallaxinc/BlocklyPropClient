import os
import logging
from sys import platform
from subprocess import Popen, PIPE, check_output, CalledProcessError

# Define error constants

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
handler = logging.FileHandler('BlocklyPropClient.log', mode='w')
#handler = logging.FileHandler('BlocklyPropClient.log')
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


def init():
    logger.info("Logger has been started.")

    # Debian linux
    if platform == 'linux2':
        if is_module_loaded() != 0:
            return

        if check_system_messages() != 0:
            return

     # MacOS
    if platform == 'darwin':
        if is_macos_ftdi_module_installed() != 0:
            return 101

        if is_macos_ftdi_module_loaded != 0:
            return 102


def is_module_loaded():
    try:
        process = Popen(['cat', '/proc/modules'], stdout=PIPE, stderr=PIPE)
        output = check_output(('grep', 'ftdi'), stdin=process.stdout)
        logger.debug('FTDI module load state')
        logger.debug(output)
        return 0
    except CalledProcessError:
        logger.warning('No FTDI modules detected.')
        return 1


def check_system_messages():
    try:
        process = Popen(['dmesg', '-H', '-x'], stdout=PIPE, stderr=PIPE)
        output = check_output(('grep', 'ftdi'), stdin=process.stdout)
        process.wait()
        logger.debug(output)
        return 0
    except CalledProcessError:
        logger.warning('Serial port is not assigned.')
        return 1


def check_macos_logpath():
    user_home = os.path.expanduser('~')
    log_path = user_home + '/Library/Logs/BlocklyProp'

    # Does the log directory exist
    try:
        os.stat(log_path)
        return 0

    except OSError:
        # Create a new log path
        try:
            os.mkdirs(log_path)

        except OSError:
            return 1

    return 0


def is_macos_ftdi_module_loaded():
    try:
        process = Popen(['kextstat'], stdout=PIPE, stderr=PIPE)
        output = check_output(('grep', 'FTDI'), stdin=process.stdout)
        logger.debug('FTDI module load state')
        logger.debug(output)
        return 0
    except CalledProcessError:
        logger.warning('No FTDI modules detected.')
        return 1


def is_macos_ftdi_module_installed():
    return 0
