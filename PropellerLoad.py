import sys
import platform
import os
import subprocess
from serial.tools import list_ports
import logging

__author__ = 'Michel'

module_logger = logging.getLogger('blockly.loader')


class PropellerLoad:
    loading = False
    # COM & WiFi-Name ports list
    ports = []
    # Full WiFi ports list
    wports = []


    def __init__(self):
        self.logger = logging.getLogger('blockly.loader')
        self.logger.info('Creating loader logger.')

        # Find the path from which application was launched
        # realpath expands to full path if __file__ or sys.argv[0] contains just a filename
        self.appdir = os.path.dirname(os.path.realpath(__file__))
        if self.appdir == "" or self.appdir == "/":
            # launch path is blank; try extracting from argv
            self.appdir = os.path.dirname(os.path.realpath(sys.argv[0]))
        self.logger.debug("Application running from: %s", self.appdir)

        self.loaderExe = {
            "Windows":  "/propeller-tools/windows/proploader.exe",
            "Linux":    "/propeller-tools/linux/proploader",
            "MacOS":    "/propeller-tools/mac/proploader",
            "Darwin":   "/propeller-tools/mac/proploader"
        }

        self.loaderAction = {
            "RAM":    {"compile-options": ""},
            "EEPROM": {"compile-options": "-e"}
        }

        if not platform.system() in self.loaderExe:
            self.logger.error('The %s platform is not supported at this time.', platform.system())
            print(platform.system() + " is currently unsupported")
            exit(1)


    def get_ports(self):
        self.logger.info('Get ports')

        # Return last results if we're currently downloading
        if self.loading:
            return self.ports

        self.logger.info("Generating ports list")

        # Get COM ports
        success, out, err = loader(self, ["-P"])
        if success:
            self.ports = out.splitlines()
        else:
            self.logger.debug('COM Port request returned %s', err)
 
        # Get Wi-Fi ports
        success, out, err = loader(self, ["-W"])
        if success:
            self.wports = out.splitlines()
            # Extract Wi-Fi module names and sort them
            wnames = []
            for i in range(len(self.wports)):
              wnames.extend([getWiFiName(self.wports[i])])
            wnames.sort(None, None, False)
        else:
            self.logger.debug('WiFi Port request returned %s', err)

        self.ports.extend(wnames)
        self.logger.debug('Port count: %s', len(self.ports))

        return self.ports


    def download(self, action, file_to_load, com_port):
        self.loading = True

        # Patch until we figure out why the __init__ is not getting called
        if not self.appdir or self.appdir == "" or self.appdir == "/":
            # realpath expands to full path if __file__ or sys.argv[0] contains just a filename
            self.appdir = os.path.dirname(os.path.realpath(__file__))
            if self.appdir == "" or self.appdir == "/":
                # launch path is blank; try extracting from argv
                self.appdir = os.path.dirname(os.path.realpath(sys.argv[0]))

        # Set command download to RAM or EEPROM and run afterwards
        command = []
        if self.loaderAction[action]["compile-options"] != "":
            # if RAM/EEPROM compile-option not empty, add it to the list
            command.extend([self.loaderAction[action]["compile-options"]])
        command.extend(["-r"])

        # Add requested port
        if com_port is not None:
            targetWiFi = [l for l in self.wports if isWiFiName(l, com_port)]
            if len(targetWiFi) == 1:
                self.logger.debug('Requested port %s is at %s', com_port, getWiFiIP(targetWiFi[0]))            
                command.extend(["-i"])
                command.extend([getWiFiIP(targetWiFi[0]).encode('ascii', 'ignore')])
            else:
                self.logger.debug('Requested port is %s', com_port)
                command.extend(["-p"])
                command.extend([com_port.encode('ascii', 'ignore')])

        # Add target file
        command.extend([file_to_load.name.encode('ascii', 'ignore').replace('\\', '/')])

        # Download
        success, out, err = loader(self, command)

        # Return results
        return success, out or '', err or ''


def loader(self, cmdOptions):
    # Launch Propeller Loader with cmdOptions and return True/False, output and error string
    # cmdOptions must be a list
    try:
        # Form complete command line as a list: [path+exe, option {,more_options...} {, filename}]
        cmdLine = [self.appdir + self.loaderExe[platform.system()]]
        cmdLine.extend(cmdOptions)

        self.logger.info('Running loader command: %s', cmdLine)

        # Run command
        if platform.system() == "Windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            process = subprocess.Popen(cmdLine, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
        else:
            process = subprocess.Popen(cmdLine, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        out, err = process.communicate()

        # If error, log extra error detail
        if process.returncode:
            self.logger.error("Error result: %s - %s", process.returncode, err)
        self.logger.debug("Loader response: %s", out)

        if process.returncode == 0:
            success = True
        else:
            success = False

        return success, out or '', err or ''

    except OSError as ex:
        # Exception; log error and return fail status
        self.logger.error("%s", ex.message)
        return False, '', 'Exception: OSError'




def resource_path(relative):
    return os.path.join(
        os.environ.get(
            "_MEIPASS2",
            os.path.abspath(".")
        ),
        relative
    )




def isWiFiName(string, wifiName):
# Return True if string contains Wi-Fi Module record named wifiName
    return getWiFiName(string) == wifiName


def getWiFiName(string):
# Return Wi-Fi Module Name from string, or None if not found
    return strBetween(string, "Name: '", "', IP: ")


def getWiFiIP(string):
# Return Wi-Fi Module IP address from string, or None if not found
    return strBetween(string, "', IP: ", ", MAC: ")


def getWiFiMAC(string):
# Return Wi-Fi Module MAC address from string, or None if not found
    return strAfter(string, ", MAC: ")


def strBetween(string, startStr, endStr):
# Return substring from string in between startStr and endStr, or None if no match
    # Find startStr
    sPos = string.find(startStr)
    if sPos == -1: return None
    sPos += len(startStr)
    # Find endStr
    ePos = string.find(endStr, sPos)
    if ePos == -1: return None
    # Return middle
    return string[sPos:ePos]


def strAfter(string, startStr):
# Return substring from string after startStr, or None if no match
    # Find startStr
    sPos = string.find(startStr)
    if sPos == -1: return None
    sPos += len(startStr)
    # Return string after
    return string[sPos:-1]
