__author__ = 'Michel'

import platform
import os
import subprocess


class PropellerLoad:

    def __init__(self):
        self.propeller_load_executables = {
            "Windows": "/propeller-tools/windows/propeller-load.exe",
            "Linux": "/propeller-tools/linux/propeller-load",
            "MacOS": "/propeller-tools/mac/propeller-load"
        }

        self.load_actions = {
            "RAM": {"compile-options": []},
            "EEPROM": {"compile-options": ["-e"]}
        }

        if not self.propeller_load_executables[platform.system()]:
            #showerror("Unsupported", platform.system() + " is currently unsupported")
            print("Unsupported", platform.system() + " is currently unsupported")
            exit(1)

        self.appdir = os.getcwd()

    def get_ports(self):
        process = subprocess.Popen([self.appdir + self.propeller_load_executables[platform.system()], "-P"], stdout=subprocess.PIPE)
        out, err = process.communicate()
#        return json.dumps(out.splitlines())
        return out.splitlines()

    def load(self, action, file_to_load, com_port):
        executable = self.appdir + self.propeller_load_executables[platform.system()]

        executing_data = [executable, "-r"]
        executing_data.extend(self.load_actions[action]["compile-options"])
        if com_port is not None:
            executing_data.append("-p")
            executing_data.append(com_port)
        executing_data.append(file_to_load.name)
        process = subprocess.Popen(executing_data, stdout=subprocess.PIPE)
        out, err = process.communicate()

        if process.returncode == 0:
            success = True
        else:
            success = False

        return (success, out, err)
