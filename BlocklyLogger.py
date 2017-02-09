import logging
from sys import platform
from subprocess import Popen, PIPE, check_output


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
    if platform == 'linux2':
        is_module_loaded()
        check_system_messages()


def is_module_loaded():

    process = Popen(['cat', '/proc/modules'], stdout=PIPE, stderr=PIPE)
    output = check_output(('grep', 'ftdi'), stdin=process.stdout)
    logger.debug('FTDI module load state')
    logger.debug(output)


def check_system_messages():
    process = Popen(['dmesg', '-H', '-x'], stdout=PIPE, stderr=PIPE)
    output = check_output(('grep', 'ftdi'), stdin=process.stdout)
    process.wait()
    logger.debug(output)
