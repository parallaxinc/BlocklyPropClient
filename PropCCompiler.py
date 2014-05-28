__author__ = 'Michel'

import platform
import os

class PropCCompiler:

    def __init__(self, propellerLoader):
        self.propellerLoader = propellerLoader
        self.cCompilerExecutables = {
            "Windows": "propeller-elf-gcc",
            "Linux": "propeller-elf-gcc",
            "MacOS": "propeller-elf-gcc"
        }

        if not self.cCompilerExecutables[platform.system()]:
            #showerror("Unsupported", platform.system() + " is currently unsupported")
            print("Unsupported", platform.system() + " is currently unsupported")
            exit(1)

        self.appdir = os.getcwd()

    def handle(self, action, code):
        print(action)

        return "compile result"