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
    ports = []

    def __init__(self):
        self.logger = logging.getLogger('blockly.loader')
        self.logger.info('Creating loader logger.')

        # Find the path from which application was launched
        # realpath expands to full path if __file__ or sys.argv[0] contains just a filename
	self.appdir = os.path.dirname(os.path.realpath(__file__))
        if self.appdir == "" or self.appdir == "/":
	    # launch path is blank; try extracting from argv
            self.appdir = os.path.dirname(os.path.realpath(sys.argv[0]))
        self.logger.debug("PropellerLoad.py: Application running from: %s", self.appdir)

        self.propeller_load_executables = {
            "Windows":  "/propeller-tools/windows/proploader.exe",
            "Linux":    "/propeller-tools/linux/proploader",
            "MacOS":    "/propeller-tools/mac/proploader",
            "Darwin":   "/propeller-tools/mac/proploader"
        }

        self.load_actions = {
            "RAM": {"compile-options": []},
            "EEPROM": {"compile-options": ["-e"]}
        }

        if not platform.system() in self.propeller_load_executables:
            self.logger.error('The %s platform is not supported at this time.', platform.system())
            print(platform.system() + " is currently unsupported")
            exit(1)

    def get_ports(self):
        self.logger.info('Getting ports')

        if self.loading:
            return self.ports

        self.logger.info("Enumerating host ports")

        if platform.system() == "Windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            process = subprocess.Popen([self.appdir + self.propeller_load_executables[platform.system()], "-P"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
            out, err = process.communicate()
            self.logger.debug('Loader complete: Error code %s returned.', err)
            self.ports = out.splitlines()
            return self.ports
        else:
            # Get COM ports
            process = subprocess.Popen([self.appdir + self.propeller_load_executables[platform.system()], "-P"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = process.communicate()
            if err is '':
                # Success
                self.ports = out.splitlines()
            else:
                # Failure
                self.logger.debug('COM Port request returned %s', err)
 
            # Get WiFi ports
            process = subprocess.Popen([self.appdir + self.propeller_load_executables[platform.system()], "-W"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = process.communicate()
            if err is '':
                # Success 
                wport = strBetween(out, "Name: '", "', IP:")
            else:
                # Failure
                self.logger.debug('WiFi Port request returned %s', err)

            self.ports.extend(wport)

#            ports = [port for (port, driver, usb) in list_ports.comports()]

            self.logger.debug('Port count: %s', len(self.ports))

            return self.ports

    def load(self, action, file_to_load, com_port):
        self.loading = True

        # Patch until we figure out why the __init__ is not getting called
	if not self.appdir or self.appdir == "" or self.appdir == "/":
            # realpath expands to full path if __file__ or sys.argv[0] contains just a filename
	    self.appdir = os.path.dirname(os.path.realpath(__file__))
            if self.appdir == "" or self.appdir == "/":
	        # launch path is blank; try extracting from argv
                self.appdir = os.path.dirname(os.path.realpath(sys.argv[0]))

        executable = self.appdir + self.propeller_load_executables[platform.system()]
        self.logger.debug('Loader executable path is: %s)', executable)

        executing_data = [executable, "-r"]
        executing_data.extend(self.load_actions[action]["compile-options"])
        self.logger.debug('Loader commandline is: %s', executing_data)

        if com_port is not None:
            self.logger.info("Talking to com port.")
            executing_data.append("-p")
            executing_data.append(com_port.encode('ascii', 'ignore'))

        executing_data.append(file_to_load.name.encode('ascii', 'ignore').replace('\\', '/'))

        print(executing_data)
        self.logger.info("Executing process %s", executing_data)

        try:
            if platform.system() == "Windows":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

                process = subprocess.Popen(executing_data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
            else:
                process = subprocess.Popen(executing_data, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            out, err = process.communicate()
            self.logger.info("Load result is: %s", process.returncode)
            self.logger.debug("Load error string: %s", err)
            self.logger.debug("Load output string: %s", out)

            if process.returncode == 0:
                success = True
            else:
                success = False

            self.loading = False
            return success, out or '', err or ''

        except OSError as ex:
            self.logger.error("%s", ex.message)


def resource_path(relative):
    return os.path.join(
        os.environ.get(
            "_MEIPASS2",
            os.path.abspath(".")
        ),
        relative
    )


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
    return [string[sPos:ePos]]


def strAfter(string, startStr):
# Return substring from string after startStr, or None if no match
    # Find startStr
    sPos = string.find(startStr)
    if sPos == -1: return None
    sPos += len(startStr)
    # Return string after
    return [string[sPos:-1]]
