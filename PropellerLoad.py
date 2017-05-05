import sys
import platform
import os
import subprocess
from serial.tools import list_ports
import logging

__author__ = 'Michel'

module_logger = logging.getLogger('blockly.loader')


# Elements of WiFi Port Records (wports)
wpUID  = 0
wpName = 1
wpIP   = 2
wpMAC  = 3
wpLife = 4

# Max lifetime+1 for WiFi Port Records to remain without refresh
MaxLife = 4


class PropellerLoad:
    loading = False
    # COM & WiFi-UID (unique name) ports list
    ports = []
    # WiFi Port Record list
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
        # Find COM/Wi-Fi serial ports
        self.logger.info('Received port list request')

        # Return last results if we're currently downloading
        if self.loading:
            return self.ports

        self.logger.info("Generating ports list")

        # Get COM ports
        (success, out, err) = loader(self, ["-P"])
        if success:
            self.ports = out.splitlines()
            self.ports.sort(None, None, False)
        else:
            self.logger.debug('COM Port request returned %s', err)
 
        # Get Wi-Fi ports
        (success, out, err) = loader(self, ["-W"])
        if success:
            # Save Wi-Fi port records (in self.wports)
            updateWiFiPorts(self, out.splitlines())
            # Extract unique Wi-Fi module names (UID; from Wi-Fi records) and sort them
            wnames = [wifiports[wpUID] for wifiports in self.wports]
            wnames.sort(None, None, False)
        else:
            self.logger.debug('WiFi Port request returned %s', err)

        # Append Wi-Fi ports to COM ports list
        self.ports.extend(wnames)
        self.logger.debug('Found %s ports', len(self.ports))

        return self.ports


    def download(self, action, file_to_load, com_port):
        # Download application to Propeller
        # Set loading flag to prevent interruption
        self.loading = True

        try:
            # Patch - see if __init__ is back in full operation
            if not self.appdir or self.appdir == "" or self.appdir == "/":
                self.logger.info('ERROR: LOADER FOLDER NOT FOUND!')
                return False, ' ', ' '
#            Patch below removed temporarily during platform testing
#            # Patch until we figure out why the __init__ is not getting called
#            if not self.appdir or self.appdir == "" or self.appdir == "/":
#                # realpath expands to full path if __file__ or sys.argv[0] contains just a filename
#                self.appdir = os.path.dirname(os.path.realpath(__file__))
#                if self.appdir == "" or self.appdir == "/":
#                    # launch path is blank; try extracting from argv
#                    self.appdir = os.path.dirname(os.path.realpath(sys.argv[0]))

            # Set command download to RAM or EEPROM and to run afterward download
            command = []
            if self.loaderAction[action]["compile-options"] != "":
                # if RAM/EEPROM compile-option not empty, add it to the list
                command.extend([self.loaderAction[action]["compile-options"]])
            command.extend(["-r"])

            # Add requested port
            if com_port is not None:
                # Find port(s) named com_port
                if com_port in [wifiports[wpUID] for wifiports in self.wports]:
                    # Found Wi-Fi match
                    idx = [wifiports[wpUID] for wifiports in self.wports].index(com_port)
                    IPAddr = [wifiports[wpIP] for wifiports in self.wports][idx]
                    self.logger.debug('Requested port %s is at %s', com_port, IPAddr)
                    command.extend(["-i"])
                    command.extend([IPAddr.encode('ascii', 'ignore')])
                else:
                    # Not Wi-Fi match, should be COM port
                    self.logger.debug('Requested port is %s', com_port)
                    command.extend(["-p"])
                    command.extend([com_port.encode('ascii', 'ignore')])

            # Add target file
            command.extend([file_to_load.name.encode('ascii', 'ignore').replace('\\', '/')])

            # Download
            (success, out, err) = loader(self, command)

            # Return results
            return success, out or '', err or ''

        finally:
            # Done, clear loading flag to process other events
            self.loading = False


def loader(self, cmdOptions):
    # Launch Propeller Loader with cmdOptions and return True/False, output and error string
    # cmdOptions must be a list
    try:
        # Form complete command line as a list: [path+exe, option {,more_options...} {, filename}]
        cmdLine = [self.appdir + self.loaderExe[platform.system()]]
        cmdLine.extend(cmdOptions)

        self.logger.debug('Running loader command: %s', cmdLine)

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


def updateWiFiPorts(self, wstrings):
# Merge wstrings into WiFi Ports list
# Ensures unique entries (UIDs), updates existing entries, and removes ancient entries
# Records "age" with each update unless refreshed by a matching port; those older than MaxLife-1 are considered ancient
    for newPort in wstrings:
        # Search for MAC address in known ports
        if not getWiFiMAC(newPort) in [port[wpMAC] for port in self.wports]:
            # No MAC match, enter as unique port record
            enterUniqueWiFiPort(self, newPort)
        else:
            # Found MAC match, update record as necessary
            idx = [port[wpMAC] for port in self.wports].index(getWiFiMAC(newPort))
            if self.wports[idx][wpName] == getWiFiName(newPort):
                # Name hasn't changed; leave Name and UID, update IP and Life
                self.wports[idx][wpIP] = getWiFiIP(newPort)
                self.wports[idx][wpLife] = MaxLife
            else:
                # Name has changed; replace entire record with guaranteed-unique entry
                self.wports.pop(idx)
                enterUniqueWiFiPort(self, newPort)

    # Age records
    for port in self.wports:
        port[wpLife] = port[wpLife] - 1
    # Remove ancients
    while 0 in [port[wpLife] for port in self.wports]:
        self.wports.pop([port[wpLife] for port in self.wports].index(0))


def enterUniqueWiFiPort(self, newPort):
# Enter newPort as unique port record
# If name matches another, it will be made unique by appending one or more if its MAC digits
    # Start with UID = Name
    Name = getWiFiName(newPort)+'-'
    UID = Name[:-1]
    # Prep modifer (MAC address without colons)
    Modifier = getWiFiMAC(newPort).replace(":", "")

    # Check for unique name (UID)
    Size = 1
    while UID in [port[wpUID] for port in self.wports]:
        # Name is duplicate; modify for unique name
        UID = Name + Modifier[-Size:]
        Size += 1
        if Size == len(Modifier):
            # Ran out of digits? Repeat Modifier
            Name = UID
            Size = 0

    # UID is unique, create new entry (UID, Name, IP, MAC, MaxLife)
    self.wports.append([UID, getWiFiName(newPort), getWiFiIP(newPort), getWiFiMAC(newPort), MaxLife])




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
    return string[sPos:]
