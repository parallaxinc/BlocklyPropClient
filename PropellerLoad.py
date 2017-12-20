import sys
import platform
import os
import subprocess
from serial.tools import list_ports
import logging

__author__ = 'Michel'

module_logger = logging.getLogger('blockly.loader')


# Elements of Port Records (portRec)
prUID  = 0
prName = 1
prIP   = 2
prMAC  = 3
prLife = 4

# Max lifetime+1 for wired (w) and wifi (wf) Port Records to remain without refresh
wMaxLife = 2
wfMaxLife = 4

# Wi-Fi Record Headers
wfNameHdr = "Name: '"
wfIPHdr   = "', IP: "
wfMACHdr  = ", MAC: "


class PropellerLoad:
    loading = False
    discovering = False
    # "Unique identifier" ports list
    ports = []
    # Port Record list- contains wired (UID) and wireless ports (UID, Name, IP, MAC)
    portRec = []
    # Lists for manipulation
    wnames = []
    wlnames = []


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

        self.loaderOption = {
            "CODE":         {"loader-options": "-c"},
            "VERBOSE":      {"loader-options": "-v"},
            "CODE_VERBOSE": {"loader-options": "-c -v"}
        }

        if not platform.system() in self.loaderExe:
            self.logger.error('The %s platform is not supported at this time.', platform.system())
            print(platform.system() + " is currently unsupported")
            exit(1)


    def get_ports(self):
        # Search for wired/wireless serial ports
        # Return previous results if we're currently downloading to a port or discovering ports
        if self.loading or self.discovering:
            return self.ports

        self.logger.info("Generating new ports list")
        # Set discovering flag to prevent interruption
        self.discovering = True

        try:
            # Find wired & wireless serial ports
            (success, out, err) = loader(self, ["-P", "-W"])
            # Process wired response
            if success:
                # Update port records (in self.portRec)
                updatePorts(self, out.splitlines())
                # Extract unique port names (UID; from port records) and sort them alphabetically
                wnames = [wiredport[prUID] for wiredport in self.portRec if wiredport[prName] == ""]
                wnames.sort(None, None, False)
                wlnames = [wirelessport[prUID] for wirelessport in self.portRec if wirelessport[prName] != ""]
                wlnames.sort(None, None, False)
                # Assign to return list (with wired group on top, wireless group below) in a single step
                # to avoid partial results being used by parallel calling process
                self.ports = wnames + wlnames
                self.logger.debug('Found %s ports', len(self.ports))
            else:
                # Error with external loader
                self.logger.error('Serial port request returned %s', err)
                self.ports = []
 
            return self.ports

        finally:
            # Done, clear discovering flag to process other events
            self.discovering = False


    def download(self, option, action, file_to_load, com_port):
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

            # Set command options to download to RAM or EEPROM and to run afterward download
            command = []

            if self.loaderOption[option]["loader-options"] != "":
                # if loader-option not empty, add it to the list
                command.extend([self.loaderOption[option]["loader-options"]])

            if self.loaderAction[action]["compile-options"] != "":
                # if RAM/EEPROM compile-option not empty, add it to the list
                command.extend([self.loaderAction[action]["compile-options"]])

            command.extend(["-r"])

            # Specify requested port
            if com_port is not None:
                # Determine port type and insert into command
                wlports = [wirelessport for wirelessport in self.portRec if wirelessport[prName] != ""]
                wlnames = [names[prUID] for names in wlports]
                if com_port in wlnames:
                    # Found wireless port match
                    IPAddr = [ips[prIP] for ips in wlports][wlnames.index(com_port)]
                    self.logger.debug('Requested port %s is at %s', com_port, IPAddr)
                    command.extend(["-i"])
                    command.extend([IPAddr.encode('ascii', 'ignore')])
                else:
                    # Not wireless port match, should be wired port
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


def updatePorts(self, strings):
# Merge strings into Port Record list
# Ensures unique entries (UIDs), updates existing entries, and removes ancient entries
# Records "age" with each update unless refreshed by a matching port; those older than xMaxLife-1 are considered ancient
    for newPort in strings:
        if not isWiFiStr(newPort):
            # Wired port- search for existing identifier
            if newPort in [port[prUID] for port in self.portRec]:
                # Found existing- just refresh life
                self.portRec[[port[prUID] for port in self.portRec].index(newPort)][prLife] = wMaxLife
            else:
                # No match- create new entry (UID, n/a, n/a, n/a, MaxLife)
                self.portRec.append([newPort, '', '', '', wMaxLife])
        else:
            # Wireless port- search for its MAC address within known ports
            if not getWiFiMAC(newPort) in [port[prMAC] for port in self.portRec]:
                # No MAC match- enter as unique port record
                enterUniqueWiFiPort(self, newPort)
            else:
                # Found MAC match- update record as necessary
                idx = [port[prMAC] for port in self.portRec].index(getWiFiMAC(newPort))
                if self.portRec[idx][prName] == getWiFiName(newPort):
                    # Name hasn't changed- leave Name and UID, update IP and Life
                    self.portRec[idx][prIP] = getWiFiIP(newPort)
                    self.portRec[idx][prLife] = wfMaxLife
                else:
                    # Name has changed- replace entire record with guaranteed-unique entry
                    self.portRec.pop(idx)
                    enterUniqueWiFiPort(self, newPort)


    # Age records
    for port in self.portRec:
        port[prLife] = port[prLife] - 1
    # Remove ancients
    while 0 in [port[prLife] for port in self.portRec]:
        self.portRec.pop([port[prLife] for port in self.portRec].index(0))


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
    while UID in [port[prUID] for port in self.portRec]:
        # Name is duplicate- modify for unique name
        UID = Name + Modifier[-Size:]
        Size += 1
        if Size == len(Modifier):
            # Ran out of digits? Repeat Modifier
            Name = UID
            Size = 1

    # UID is unique, create new entry (UID, Name, IP, MAC, MaxLife)
    self.portRec.append([UID, getWiFiName(newPort), getWiFiIP(newPort), getWiFiMAC(newPort), wfMaxLife])



def isWiFiStr(string):
# Return True if string is a Wi-Fi record string, False otherwise
    return (string.find(wfNameHdr) > -1) and (string.find(wfIPHdr) > -1) and (string.find(wfMACHdr) > -1)


def isWiFiName(string, wifiName):
# Return True if string contains Wi-Fi Module record named wifiName
    return getWiFiName(string) == wifiName


def getWiFiName(string):
# Return Wi-Fi Module Name from string, or None if not found
    return strBetween(string, wfNameHdr, wfIPHdr)


def getWiFiIP(string):
# Return Wi-Fi Module IP address from string, or None if not found
    return strBetween(string, wfIPHdr, wfMACHdr)


def getWiFiMAC(string):
# Return Wi-Fi Module MAC address from string, or None if not found
    return strAfter(string, wfMACHdr)


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
