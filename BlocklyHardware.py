import os
import logging
from sys import platform
from subprocess import Popen, PIPE, check_output, CalledProcessError

# Define platform constants
PLATFORM_MACOS = 'darwin'
PLATFORM_UBUNTU = 'linux2'

# Define error constants
FTDI_DRIVER_NOT_INSTALLED = 201
FTDI_DRIVER_NOT_LOADED = 202
PLATFORM_UNKNOWN = 2

# Enable logging
__module_logger = logging.getLogger('blockly')


def init():
    result = is_module_installed()
    if result != 0:
        return result

    result = is_module_loaded()
    if result != 0:
        return result


def is_module_installed():
    if platform == PLATFORM_MACOS:
        return __is_module_installed_macos()
    elif platform == PLATFORM_UBUNTU:
        return __is_module_installed_ubuntu()
    else:
        return PLATFORM_UNKNOWN


def is_module_loaded():
    if platform == PLATFORM_MACOS:
        return __is_module_loaded_macos()
    elif platform == PLATFORM_UBUNTU:
        return __is_module_loaded_ubuntu()
    else:
        return PLATFORM_UNKNOWN


# Ubuntu implementation
def __is_module_installed_ubuntu():
    try:
        process = Popen(['cat', '/proc/modules'], stdout=PIPE, stderr=PIPE)
        output = check_output(('grep', 'ftdi'), stdin=process.stdout)
        __module_logger.debug('FTDI module load state')
        __module_logger.debug(output)
        return 0
    except CalledProcessError:
        __module_logger.warning('No FTDI modules detected.')
        return FTDI_DRIVER_NOT_INSTALLED


def __is_module_loaded_ubuntu():
    try:
        process = Popen(['dmesg', '-H', '-x'], stdout=PIPE, stderr=PIPE)
        output = check_output(('grep', 'ftdi'), stdin=process.stdout)
        process.wait()
        __module_logger.debug(output)
        return 0
    except CalledProcessError:
        __module_logger.warning('Serial port is not assigned.')
        return FTDI_DRIVER_NOT_LOADED


# MacOS implementation
def __is_module_installed_macos():
    try:
        # Does the log directory exist
        os.stat('/Library/Extensions/FTDIUSBSerialDriver.kext')
        __module_logger.info('FTDI driver is installed')
        return 0

    except OSError:
        __module_logger.error('Cannot find FTDI installation')
        return FTDI_DRIVER_NOT_INSTALLED


def __is_module_loaded_macos():
    try:
        process = Popen(['kextstat'], stdout=PIPE, stderr=PIPE)
        output = check_output(('grep', 'FTDI'), stdin=process.stdout)
        __module_logger.debug('FTDI module load state')
        __module_logger.debug(output)
        return 0
    except CalledProcessError:
        __module_logger.warning('No FTDI modules detected.')
        return 1