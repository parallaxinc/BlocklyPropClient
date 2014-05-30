__author__ = 'Michel'

import platform
import os
import subprocess
from tempfile import NamedTemporaryFile


class SpinCompiler:

    def __init__(self, propeller_loader):
        self.propeller_loader = propeller_loader
        self.compiler_executables = {
            "Windows": "/propeller-tools/windows/openspin.exe",
            "Linux": "/propeller-tools/linux/openspin",
            "MacOS": "/propeller-tools/mac/openspin"
        }

        self.compile_actions = {
            "COMPILE": {"compile-options": ["-b"], "extension":".binary", "call-loader": False},
            "RAM": {"compile-options": ["-b"], "extension":".binary", "call-loader": True},
            "EEPROM": {"compile-options": ["-e"], "extension":".eeprom", "call-loader": True}
        }

        if not self.compiler_executables[platform.system()]:
            #showerror("Unsupported", platform.system() + " is currently unsupported")
            print("Unsupported", platform.system() + " is currently unsupported")
            exit(1)

        self.appdir = os.getcwd()

    def handle(self, action, code, com_port):
        result = {}

        compile_success, binary_file, compile_output, compile_err = self.compile(action, code)
        out = compile_output
        success = compile_success

        result["compile-success"] = compile_success

        if self.compile_actions[action]["call-loader"]:
            load_success, load_output, load_err = self.propeller_loader.load(action, binary_file, com_port)
            out += "\n" + load_output
            success = success and load_success
            result["load-success"] = load_success

        os.remove(binary_file.name)

        result["success"] = success
        result["message"] = out
        return result

    def compile(self, action, code):
        spin_file = NamedTemporaryFile(mode='w', suffix='.spin', delete=False)
        binary_file = NamedTemporaryFile(suffix=self.compile_actions[action]["extension"], delete=False)
        spin_file.write(code)
        spin_file.close()
        binary_file.close()

        executable = self.appdir + self.compiler_executables[platform.system()]
	print executable
        lib_directory = self.appdir + "/propeller-lib"

        executing_data = [executable, "-o", binary_file.name, "-L", lib_directory]
        executing_data.extend(self.compile_actions[action]["compile-options"])
        executing_data.append(spin_file.name)
        process = subprocess.Popen(executing_data, stdout=subprocess.PIPE)
        out, err = process.communicate()

        if process.returncode == 0:
            success = True
        else:
            success = False

        os.remove(spin_file.name)

        return (success, binary_file, out, err)
