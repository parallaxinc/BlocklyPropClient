__author__ = 'Michel'

import platform
import os
import subprocess
import json


class PropellerLoad:

    def __init__(self):
        self.propellerLoadExecutables = {
            "Windows": "/propeller-tools/windows/propeller-load.exe"
        }

        if not self.propellerLoadExecutables[platform.system()]:
            #showerror("Unsupported", platform.system() + " is currently unsupported")
            print("Unsupported", platform.system() + " is currently unsupported")
            exit(1)

        self.appdir = os.getcwd()

    def get_ports(self):
        process = subprocess.Popen([self.appdir + self.propellerLoadExecutables[platform.system()], "-P"], stdout=subprocess.PIPE)
        out, err = process.communicate()
        return json.dumps(out.splitlines())