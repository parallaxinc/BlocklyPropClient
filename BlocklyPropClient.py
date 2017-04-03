"""
    BlocklyProp Client

    0.5.3  February 22, 2017
    - Correct error in path to propeller-load executable.
    - Detect condition where serial port has disappeared
    - Correct error where browser request for specific port
      speed was disregarded.

"""
import Tkinter as tk
import ttk as ttk
import tkMessageBox
import tkFileDialog
import ScrolledText
import multiprocessing
from datetime import datetime
import threading
import webbrowser
import os
import ip
import sys
import logging
import BlocklyServer
import BlocklyLogger
import BlocklyHardware


__author__ = 'Michel & Vale'

PORT = 6009

# -----------------------------------------------------------------------
# NOTE:
#
# Please verify that the version number in the local about.txt and the
# ./package/win-resources/blocklypropclient-installer.iss matches this.
# -----------------------------------------------------------------------
VERSION = "0.6.2"


# Enable logging for functions outside of the class definition
module_logger = None


class BlocklyPropClient(tk.Tk):
    def __init__(self, *args, **kwargs):
        global module_logger

        # Enable application logging
        BlocklyLogger.init()
        self.logger = logging.getLogger('blockly.main')
        module_logger = logging.getLogger('blockly')

        self.logger.info('Creating logger.')

        BlocklyHardware.init()

        # Init Tk
        tk.Tk.__init__(self, *args, **kwargs)

        # initialize values
        self.version = 0.0
        self.app_version = "0.0"
        self.connected = False

        # Find the path from which application was launched
        # realpath expands to full path if __file__ or sys.argv[0] contains just a filename
	self.appdir = os.path.dirname(os.path.realpath(__file__))
        if self.appdir == "" or self.appdir == "/":
	    # launch path is blank; try extracting from argv
            self.appdir = os.path.dirname(os.path.realpath(sys.argv[0]))

	self.logger.info('Logging is enabled')
	self.logger.info('BlocklyPropClient.py: Application launched from %s', self.appdir)

        # initialize config variables
        self.ip_address = tk.StringVar()
        self.port = tk.StringVar()
        self.trace_log = tk.IntVar()
        self.logfile = tk.StringVar()

        # Default trace to enabled or logging level 1, not sure which it is
        self.trace_log.set(1)

        self.title("BlocklyProp")

        # Set icon for Windows platform
        self.logger.info('Operating system is %s', os.name)
        if "nt" == os.name:
            self.wm_iconbitmap(bitmap='blocklyprop.ico')

        # Init the system
        self.initialize()
        self.initialize_menu()

    # Set the application version and app_version values
    def set_version(self, version):
        # The application version number was converted to a traditional 'major'.'minor'.'patch_level'
        # format. There is code in the BlocklyProp Javascript that expects the version number as a
        # float. We handle that issue here.
        ver_elements = VERSION.split('.')
        if len(ver_elements) >= 2:
            n_version = float(ver_elements[0] + '.' + ver_elements[1])
        else:
            n_version = 0.4

        self.version = n_version
        self.app_version = version

    def initialize(self):
        self.logger.info('Initializing the UI')

        # Display the client screen
        self.grid()

        # IP address label
        self.lbl_ip_address = ttk.Label(self, anchor=tk.E, text='IP Address :')
        self.lbl_ip_address.grid(column=0, row=0, sticky='nesw')

        # TCP port number label
        self.lbl_port = ttk.Label(self, anchor=tk.E, text='Port :')
        self.lbl_port.grid(column=0, row=1, sticky='nesw')

        # Log file label
        self.lbl_logfile = ttk.Label(self, anchor=tk.E, text='Log File :')
        self.lbl_logfile.grid(column=0, row=2, sticky='nesw')

        # Open browser button
        self.btn_open_browser = ttk.Button(self, text='Open Browser', command=self.handle_browser)
        self.btn_open_browser.grid(column=0, row=3, sticky='nesw', padx=3, pady=3)

        # Trace label
        self.lbl_log = ttk.Label(self, anchor=tk.W, text='Trace :')
        self.lbl_log.grid(column=0, row=4, sticky='nesw', padx=3, pady=3)

        # Trace log display window
        self.ent_log = ScrolledText.ScrolledText(self, state='disabled')
        self.ent_log.grid(column=0, row=5, columnspan=2, sticky='nesw', padx=3, pady=3)


        # IP address text box
        self.ent_ip_address = ttk.Entry(self, state='readonly', textvariable=self.ip_address)
        self.ent_ip_address.grid(column=1, row=0, sticky='nesw', padx=3, pady=3)

        # TCP port text box
        self.ent_port = ttk.Entry(self, textvariable=self.port)
        self.ent_port.grid(column=1, row=1, sticky='nesw', padx=3, pady=3)

        # Log file text box
        self.ent_logfile = ttk.Entry(self, textvariable=self.logfile)
        self.ent_logfile.grid(column=1, row=2, sticky='nesw', padx=3, pady=3)


        # Connect to device button
        self.btn_connect = ttk.Button(self, text='Connect', command=self.handle_connect)
        self.btn_connect.grid(column=1, row=3, sticky='nesw', padx=3, pady=3)

        #self.lbl_current_code = ttk.Label( self, anchor=tk.E, text='Code most recently compiled :' )
        #self.lbl_current_code.grid(column=0, row=5, sticky='nesw', padx=3, pady=3)

        #self.current_code = ScrolledText.ScrolledText( self, state='disabled')
        #self.current_code.grid(column=0, row=6, columnspan=2, sticky='nesw', padx=3, pady=3)

        self.check_log_trace = tk.Checkbutton(self, anchor=tk.E, text='Trace logging', variable=self.trace_log, offvalue=1, onvalue=0)
        self.check_log_trace.grid(column=1, row=4, sticky='nesw', padx=3, pady=3)


        #s = ttk.Style()
        #s.configure('Right.TCheckbutton', anchor='e')
        #self.check_log_trace = ttk.Checkbutton(self, style='Right.TCheckbutton', text='Trace logging', variable=self.trace_log)
        #self.btn_log_checkbox = ttk.Button(self, text='Low level logging: Currently False', command=self.handle_lowlevel_logging)
        #self.btn_log_checkbox.grid(column=1, row=3, sticky='nesw', padx=3, pady=3)

        self.grid_columnconfigure(0, minsize=100)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(4, weight=1)
        self.resizable(True, True)
        self.minsize(250, 200)

        self.protocol("WM_DELETE_WINDOW", self.handle_close)

        self.ip_address.set(ip.get_lan_ip())
        self.logger.info('Client IP is: %s', self.ip_address.get())

        self.port.set(PORT)
        self.logger.info('Port number is: %s', self.port.get())

        if BlocklyLogger.path is None:
            self.logfile.set(' ')
            self.logger.info('Disk logging is disabled.')
        else:
            self.logfile.set(BlocklyLogger.path)
            self.logger.info('Disk log file location is: %s', BlocklyLogger.path)

        self.server_process = None

        self.q = multiprocessing.Queue()

        monitor = threading.Thread(target=self.text_catcher)
        monitor.daemon = True
        monitor.start()

    def initialize_menu( self ):
        self.logger.info('Initializing the UI menu')

        menubar = tk.Menu(self)
        about_menu = tk.Menu( menubar, tearoff=0 )
        about_menu.add_command( label="BlocklyPropClient Source Code", command=self.handle_client_code_browser )
        about_menu.add_command( label="BlocklyProp Source Code", command=self.handle_code_browser )
        about_menu.add_separator()
        about_menu.add_command( label="About", command=self.about_info )
        menubar.add_cascade( label="About", menu=about_menu)
        self.config( menu=menubar )

    def handle_connect(self):
        self.logger.info('Connect state is: %s', self.connected)

        if self.connected:
            self.logger.debug('Terminating server process')
            BlocklyServer.stop(self.q)
            self.server_process.terminate()
            self.connected = False

            # Set the connect/disconnect button text to the alternate state
            self.btn_connect['text'] = "Connect"
        else:
            # read entered values and start server
            self.server_process = multiprocessing.Process(
                target=BlocklyServer.main,
                args=(int(self.port.get()), self.version, self.q))

            self.server_process.start()

            self.connected = True
            self.btn_connect['text'] = "Disconnect"

    def handle_save_as( self ):
        file = tkFileDialog.asksaveasfile( mode='w' )
        code = open( "c_code_file", 'r' ).read()

        file.write( code )
        file.close()

        tkMessageBox.showinfo("Info", "The most recently compiled code has been saved to a file successfully" )

    def handle_browser(self):
        webbrowser.open_new('http://blockly.parallax.com')

    def handle_code_browser(self):
        webbrowser.open_new('http://github.com/parallaxinc/BlocklyProp')

    def handle_client_code_browser(self):
        webbrowser.open_new('http://github.com/parallaxinc/BlocklyPropClient')

    # Open the application About dialog box
    def about_info(self):
        try:
            with open(self.appdir + '/about.txt', 'r') as about_file:
                tkMessageBox.showinfo("About BlocklyProp", about_file.read())
        except OSError:
            tkMessageBox.showinfo("About BlocklyProp", "About file is missing")

    # Open the application Quit dialog box and process user selection
    def handle_close(self):
        self.logger.info('Opening Quit dialog')

        if tkMessageBox.askokcancel("Quit?", "Are you sure you want to quit?"):
            # stop server if running
            if self.connected:
                self.logger.info('Terminating server process')
                self.server_process.terminate()

            self.quit()
        else:
            self.logger.debug('Cancelling application quit request')

    def text_catcher(self):
        try:
            while 1:
                (level, level_name, message) = self.q.get()
                min_level = self.trace_log.get() * 5

                if level > min_level:
                    self.ent_log['state'] = 'normal'
                    self.ent_log.insert(tk.END, datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' ' + level_name + ': ' + message + '\n')
                    self.ent_log.yview_pickplace("end")
                    self.ent_log['state'] = 'disabled'
        except EOFError:
            # print('EOF Error')
            self.logger.error('Unexpected end of file encountered')


if __name__ == '__main__':
    multiprocessing.freeze_support()

    bp_client = BlocklyPropClient()
    bp_client.set_version(VERSION)
    bp_client.mainloop()
