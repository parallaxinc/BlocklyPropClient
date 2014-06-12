__author__ = 'Michel'

import platform
import os
import json
import subprocess
import re
from tempfile import NamedTemporaryFile


class PropCCompiler:

    def __init__(self, propellerLoader):
        self.propeller_loader = propellerLoader
        self.compiler_executables = {
            "Windows": "propeller-elf-gcc",
            "Linux": "propeller-elf-gcc",
            "MacOS": "propeller-elf-gcc"
        }

        self.compile_actions = {
            "COMPILE": {"compile-options": [], "extension":".elf", "call-loader": False},
            "RAM": {"compile-options": [], "extension":".elf", "call-loader": True},
            "EEPROM": {"compile-options": [], "extension":".elf", "call-loader": True}
        }

        if not self.compiler_executables[platform.system()]:
            #showerror("Unsupported", platform.system() + " is currently unsupported")
            print("Unsupported", platform.system() + " is currently unsupported")
            exit(1)

        self.appdir = os.getcwd()

    def handle(self, action, code, com_port):
        result = {}

        compile_success, binary_file, compile_output, compile_err = self.compile(action, code)
        print(compile_err)
        if compile_err is None:
            out = "Compile successful\n"
        else:
            out = compile_err
        success = compile_success

        result["compile-success"] = compile_success

        if self.compile_actions[action]["call-loader"]:
            load_success, load_output, load_err = self.propeller_loader.load(action, binary_file, com_port)
            out += "\n" + load_output
            success = success and load_success
            result["load-success"] = load_success

        try:
            os.remove(binary_file.name)
        except WindowsError:
            print("Binary does not exist")

        result["success"] = success
        result["message"] = out
        return result

    def compile(self, action, code):
        c_file = NamedTemporaryFile(mode='w', suffix='.c', delete=False)
        binary_file = NamedTemporaryFile(suffix=self.compile_actions[action]["extension"], delete=False)
        c_file.write(code)
        c_file.close()
        binary_file.close()

        includes = self.parse_includes(c_file) # parse includes
        descriptors = self.get_includes(includes) # get lib descriptors for includes
        executing_data = self.create_executing_data(c_file, binary_file, descriptors) # build execution command
        process = subprocess.Popen(executing_data, stdout=subprocess.PIPE) # call compile
        out, err = process.communicate()

        if process.returncode == 0:
            success = True
        else:
            success = False

        os.remove(c_file.name)

        return (success, binary_file, out, err)

    def get_includes(self, includes):
        global lib_descriptor
        descriptors = []
        for include in includes:
            for descriptor in lib_descriptor:
                if include in descriptor['include']:
                    descriptors.append(descriptor)
        return descriptors

    def parse_includes(self, c_file):
        includes = set()

        f = open(c_file.name)
        for line in f:
            if '#include' in line:
                match = re.match(r'^#include "(\w+).h"', line)
                if match:
                    includes.add(match.group(1))

        return includes

    def create_executing_data(self, c_file, binary_file, descriptors):
        executable = self.compiler_executables[platform.system()]
        lib_directory = self.appdir + "/propeller-c-lib/"

        executing_data = [executable]
        for descriptor in descriptors:
            executing_data.append("-I")
            executing_data.append(lib_directory + descriptor["libdir"])
            executing_data.append("-L")
            executing_data.append(lib_directory + descriptor["memorymodel"]["cmm"])
        executing_data.append("-Os")
        executing_data.append("-mcmm")
        executing_data.append("-m32bit-doubles")
        executing_data.append("-std=c99")
        executing_data.append("-o")
        executing_data.append(binary_file.name)
        executing_data.append(c_file.name)
        executing_data.append("-lm")
        for descriptor in descriptors:
            executing_data.append("-l" + descriptor["name"])

        return executing_data


lib_descriptor = json.load(open(os.getcwd() + "/propeller-c-lib/lib-descriptor.json"))