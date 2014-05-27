__author__ = 'Michel'

import platform
import os

class SpinCompiler:

    def __init__(self):
        self.spinCompilerExecutables = {
            "Windows": "/propeller-tools/windows/openspin.exe"
        }

        if not self.spinCompilerExecutables[platform.system()]:
            #showerror("Unsupported", platform.system() + " is currently unsupported")
            print("Unsupported", platform.system() + " is currently unsupported")
            exit(1)

    def compile(self, action):
        print(action)

        return "compile result"