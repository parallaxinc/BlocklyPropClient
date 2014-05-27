__author__ = 'Michel'

from os.path import *
from Tkinter import *
import ttk
from ttk import *
from tkFileDialog import askopenfilename
from tkMessageBox import showerror
import subprocess
import platform
import os

from server import BlocklyPropServer



class BlocklyPropClientGui(Frame):
    def __init__(self):
        self.propellerLoadExecutables = {
            "Windows" : "/propeller-tools/windows/propeller-load.exe"
        }

        if not self.propellerLoadExecutables[platform.system()]:
            showerror("Unsupported", platform.system() + " is currently unsupported")
            exit(1)

        self.appdir = os.getcwd()
        initial_dir = expanduser("~")
        os.chdir(initial_dir)
        Frame.__init__(self)
        self.master.title("BlocklyProp client")
        self.master.minsize(200, 300)
        self.master.maxsize(200, 300)
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.grid(sticky=W+E+N+S)

        self.notebook = ttk.Notebook(self)
        formLoad = ttk.Frame(self.notebook)
        formServer = ttk.Frame(self.notebook)
        formProxy = ttk.Frame(self.notebook)
        self.notebook.grid(columnspan=2, sticky=(N, S, E, W))

        self.notebook.add(formLoad, text='Load')
        self.notebook.add(formServer, text='Server')
        self.notebook.add(formProxy, text='Proxy')

        formLoad.rowconfigure(2, weight=1)
        formLoad.columnconfigure(1, weight=1)

        self.server = BlocklyPropServer()

        self.master.protocol("WM_DELETE_WINDOW", self.close)

   #     self.button = Button(self, text="Browse", command=self.load_file, width=10)
   #     self.button.grid(row=1, column=0, sticky=W)

    def close(self):
        self.server.stop()
        exit(1)

    def load_file(self):
        # initialdir=initial_dir,
        self.filename = askopenfilename(filetypes=[("Propeller files", "*.binary;*.eeprom")], title="Select a compiled Propeller file")
        if self.filename:
            try:
                if not self.filename:
                    print("No file selected")
                else:
                    os.chdir( os.path.dirname(os.path.realpath(self.filename)))
                    if self.filename.endswith(".eeprom"):
                        process = subprocess.Popen([self.appdir + self.propellerLoadExecutables[platform.system()], "-r", "-e", self.filename], stdout=subprocess.PIPE)
                    else:
                        process = subprocess.Popen([self.appdir + self.propellerLoadExecutables[platform.system()], "-r", self.filename], stdout=subprocess.PIPE)
                    out, err = process.communicate()
                    print out

            except:                     # <- naked except is a bad idea
                showerror("Open Source File", "Failed to read file\n'%s'" % self.filename)
            return

if __name__ == "__main__":
    BlocklyPropClientGui().mainloop()