__author__ = 'Michel & Vale'

import pygtk
pygtk.require('2.0')
import gtk

import ScrolledText
import multiprocessing
from datetime import datetime
import threading
import os
import ip
import BlocklyServer

PORT = 6009
VERSION = 0.2


class BlocklyPropClient():

    def delete_event(self, widget, event, data=None):
        # If you return FALSE in the "delete_event" signal handler,
        # GTK will emit the "destroy" signal. Returning TRUE means
        # you don't want the window to be destroyed.
        # This is useful for popping up 'are you sure you want to quit?'
        # type dialogs.
        print "delete event occurred"

        message = gtk.MessageDialog(parent=self.window, flags=gtk.DIALOG_MODAL, type=gtk.MESSAGE_QUESTION, buttons=gtk.BUTTONS_OK_CANCEL)
        message.set_markup("Are you sure you want to quit?")
        message.set_title("Quit?")
        response = message.run()
        message.destroy()
        if response == gtk.RESPONSE_OK:
            # stop server if running
            if self.connected:
               # BlocklyServer.stop()
                self.server_process.terminate()

            return True

        # Change FALSE to TRUE and the main window will not be destroyed
        # with a "delete_event".
        return False

    # Another callback
    def destroy(self, widget, data=None):
        gtk.main_quit()

    def __init__(self, *args, **kwargs):

        # initialize values
        self.version = 0.0
        self.connected = False

        # initialize config variables
        self.ip_address = ''
        self.port = ''
        self.trace_log = 1

       # self.trace_log.set(1)

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

        # When the window is given the "delete_event" signal (this is given
        # by the window manager, usually by the "close" option, or on the
        # titlebar), we ask it to call the delete_event () function
        # as defined above. The data passed to the callback
        # function is NULL and is ignored in the callback function.
        self.window.connect("delete_event", self.delete_event)

        # Here we connect the "destroy" event to a signal handler.
        # This event occurs when we call gtk_widget_destroy() on the window,
        # or if we return FALSE in the "delete_event" callback.
        self.window.connect("destroy", self.destroy)

        # Sets the border width of the window.
        self.window.set_border_width(10)

        self.window.title("BlocklyProp")

        # Set icon
        if "nt" == os.name:
      #      self.wm_iconbitmap(bitmap='blocklyprop.ico')
            pass
        else:
            #self.wm_iconbitmap(bitmap = "@myicon.xbm")
            pass

        self.initialize()
        self.initialize_menu()

        self.window.show()

    def main(self):
        gtk.main()

    def set_version(self, version):
        self.version = version

    def initialize(self):
        self.table = gtk.Table(rows=4, columns=2, homogeneous=False)

        self.lbl_ip_address = gtk.Label('IP Address :')
        self.table.attach(self.lbl_ip_address, 0, 0, 0, 0)
       # self.lbl_ip_address.grid(column=0, row=0, sticky='nesw')

        self.ent_ip_address = gtk.Entry()
        self.ent_ip_address.set_editable(False)
        self.table.attach(self.ent_ip_address, 1, 0, 1, 0)
       # self.ent_ip_address.grid(column=1, row=0, sticky='nesw', padx=3, pady=3)

        self.lbl_port = gtk.Label(text='Port :')
        self.table.attach(self.lbl_port, 0, 1, 0, 1)
       # self.lbl_port.grid(column=0, row=1, sticky='nesw')

        self.ent_port = gtk.Entry()
        self.table.attach(self.ent_port, 1, 1, 1, 1)
       # self.ent_port.grid(column=1, row=1, sticky='nesw', padx=3, pady=3)

        self.btn_connect = gtk.Button('Connect')
        self.btn_connect.connect('clicked', self.handle_connect)
        self.table.attach(self.btn_connect, 1, 2, 0, 1)
      #  self.btn_connect.grid(column=1, row=2, sticky='nesw', padx=3, pady=3)

        self.lbl_log = gtk.Label('Log :')
        self.table.attach(self.lbl_log, 0, 3, 0, 3)
      #  self.lbl_log.grid(column=0, row=3, sticky='nesw', padx=3, pady=3)

       # self.ent_log = ScrolledText.ScrolledText(self, state='disabled')
       # self.ent_log.grid(column=0, row=4, columnspan=2, sticky='nesw', padx=3, pady=3)

        #s = ttk.Style()
        #s.configure('Right.TCheckbutton', anchor='e')
        #self.check_log_trace = ttk.Checkbutton(self, style='Right.TCheckbutton', text='Trace logging', variable=self.trace_log)
        self.check_log_trace = gtk.CheckButton('Trace logging')
        self.table.attach(self.check_log_trace, 1, 3, 1, 3)
       # self.check_log_trace.grid(column=1, row=3, sticky='nesw', padx=3, pady=3)
        
        #self.btn_log_checkbox = ttk.Button(self, text='Low level logging: Currently False', command=self.handle_lowlevel_logging)
        #self.btn_log_checkbox.grid(column=1, row=3, sticky='nesw', padx=3, pady=3)

      #  self.grid_columnconfigure(0, minsize=100)
      #  self.grid_columnconfigure(0, weight=1)
      #  self.grid_columnconfigure(1, weight=2)
      #  self.grid_rowconfigure(4, weight=1)
      #  self.resizable(True, True)
      #  self.minsize(250, 200)

      #  self.protocol("WM_DELETE_WINDOW", self.handle_close)

        self.ip_address = ip.get_lan_ip()
        self.port = PORT

        self.ent_ip_address.set_text(self.ip_address)
        self.ent_port.set_text(self.port)

        self.q = multiprocessing.Queue()
 #       self.stdoutToQueue = StdoutToQueue(self.q)

        monitor = threading.Thread(target=self.text_catcher)
        monitor.daemon = True
        monitor.start()

        self.window.add(self.table)

    def initialize_menu(self):
        pass
      #  menubar = tk.Menu(self)

      #  menubar.add_command(label="Quit", command=self.handle_close)

      #  options_menu = tk.Menu(menubar, tearoff=0)
      #  options_menu.add_command(label="Library location")
      #  menubar.add_cascade(label="Options", menu=options_menu)

      #  help_menu = tk.Menu(menubar, tearoff=0)
      #  help_menu.add_command(label="Help")
      #  help_menu.add_command(label="About")
      #  menubar.add_cascade(label="Help", menu=help_menu)

      #  self.config(menu=menubar)

    def handle_connect(self):
        if self.connected:
            BlocklyServer.stop(self.q)
            self.server_process.terminate()
            self.connected = False
            self.btn_connect.set_label("Connect")
        else:
            # read entered values and start server
            self.server_process = multiprocessing.Process(target=BlocklyServer.main, args=(int(self.port.get()), self.version, self.q)) #, kwargs={'out':self.stdoutToQueue})
           # self.server_process = threading.Thread(target=BlocklyServer.main, args=(int(self.port.get()), self.version)) #, kwargs={'out':self.stdoutToQueue})
            self.server_process.start()

            self.connected = True
            self.btn_connect.set_label("Disconnect")

    def handle_close(self):
        pass
   #     if tkMessageBox.askokcancel("Quit?", "Are you sure you want to quit?"):
            # stop server if running
   #         if self.connected:
               # BlocklyServer.stop()
   #             self.server_process.terminate()
   #         self.quit()

    def text_catcher(self):
        while 1:
            (level, level_name, message) = self.q.get()
            min_level = self.trace_log.get() * 5
            if level > min_level:
                pass
   #             self.ent_log['state'] = 'normal'
   #             self.ent_log.insert(tk.END, datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' ' + level_name + ': ' + message + '\n')
   #             self.ent_log.yview_pickplace("end")
   #             self.ent_log['state'] = 'disabled'


if __name__ == '__main__':
    multiprocessing.freeze_support()

    bp_client = BlocklyPropClient()
    bp_client.set_version(VERSION)
    bp_client.main()