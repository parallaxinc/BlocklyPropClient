import sys

__author__ = 'Michel'

import platform
import os
import subprocess
from serial.tools import list_ports


class PropellerLoad:

    loading = False
    ports = []

    def __init__(self):
        self.propeller_load_executables = {
            "Windows": "/propeller-tools/windows/propeller-load.exe",
            "Linux": "/propeller-tools/linux/propeller-load",
            "MacOS": "/propeller-tools/mac/propeller-load",
            "Darwin": "/propeller-tools/mac/propeller-load"
        }

        self.load_actions = {
            "RAM": {"compile-options": []},
            "EEPROM": {"compile-options": ["-e"]}
        }

        if not platform.system() in self.propeller_load_executables:
            #showerror("Unsupported", platform.system() + " is currently unsupported")
            print("Unsupported", platform.system() + " is currently unsupported")
            exit(1)

        self.appdir = os.getcwd()
        self.appdir = os.path.dirname(sys.argv[0])

    def get_ports(self):
        if self.loading:
            return self.ports

        if platform.system() == "Windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            process = subprocess.Popen([self.appdir + self.propeller_load_executables[platform.system()], "-P"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
            out, err = process.communicate()

            self.ports = out.splitlines()
            return self.ports
        else:
            ports = [port for (port, driver, usb) in list_ports.comports()]
            #self.appdir +
            #process = subprocess.Popen([self.appdir + self.propeller_load_executables[platform.system()], "-P"], stdout=subprocess.PIPE)

            #out, err = process.communicate()
#        return json.dumps(out.splitlines())
            #ports = []
            #for port in out.splitlines():
            #    ports.append(port[port.index('/'):])

            self.ports = ports
            return ports

    def load(self, action, file_to_load, com_port):
        self.loading = True
        executable = self.appdir + self.propeller_load_executables[platform.system()]

        executing_data = [executable, "-r"]
        executing_data.extend(self.load_actions[action]["compile-options"])
        if com_port is not None:
            executing_data.append("-p")
            executing_data.append(com_port.encode('ascii', 'ignore'))
        executing_data.append(file_to_load.name.encode('ascii', 'ignore').replace('\\', '/'))

        print(executing_data)

        if platform.system() == "Windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            process = subprocess.Popen(executing_data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
        else:
            process = subprocess.Popen(executing_data, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        out, err = process.communicate()

        if process.returncode == 0:
            success = True
        else:
            success = False

        self.loading = False
        return (success, out or '', err or '')


def resource_path(relative):
    return os.path.join(
        os.environ.get(
            "_MEIPASS2",
            os.path.abspath(".")
        ),
        relative
    )
