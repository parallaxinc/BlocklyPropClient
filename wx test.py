__author__ = 'Michel'

import wx
import multiprocessing
from datetime import datetime
import threading
import os
import ip
import BlocklyServer

PORT = 6009
VERSION = 0.2


class BlocklyPropClient(wx.Frame):

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(400, 300))
        self.SetMinSize((250, 230))

        # initialize values
        self.version = 0.0
        self.connected = False

        # initialize config variables
        self.ip_address = ''
        self.port = ''
        self.trace_log = 1

        # Set icon
        if "nt" == os.name:
            favicon = wx.Icon('blocklyprop.ico', wx.BITMAP_TYPE_ICO)
            self.SetIcon(favicon)
        else:
            #self.wm_iconbitmap(bitmap = "@myicon.xbm")
            pass

        self.initialize()
       # self.initialize_menu()

        self.Bind(wx.EVT_CLOSE, self.do_exit)
        self.Show(True)

        self.btn_connect.SetFocus()

    def set_version(self, version):
        self.version = version

    def initialize(self):
        panel = wx.Panel(self)
        grid = wx.GridBagSizer(9, 25)

        self.ip_address = ip.get_lan_ip()
        self.port = PORT

        self.q = multiprocessing.Queue()
 #       self.stdoutToQueue = StdoutToQueue(self.q)

        self.lbl_ip_address = wx.StaticText(panel, label='IP Address :')
        grid.Add(self.lbl_ip_address, (0, 0))

        self.ent_ip_address = wx.TextCtrl(panel, style=wx.TE_READONLY)
        grid.Add(self.ent_ip_address, (0, 1), flag=wx.EXPAND)

        self.lbl_port = wx.StaticText(panel, label='Port :')
        grid.Add(self.lbl_port, (1, 0))

        self.ent_port = wx.TextCtrl(panel)
        grid.Add(self.ent_port, (1, 1), flag=wx.EXPAND)

        self.btn_connect = wx.Button(panel, label='Connect')
        self.Bind(wx.EVT_BUTTON, self.handle_connect, self.btn_connect)
        grid.Add(self.btn_connect, (2, 1), flag=wx.EXPAND)

        self.lbl_log = wx.StaticText(panel, label='Log :')
        grid.Add(self.lbl_log, (3, 0))

        self.check_log_trace = wx.CheckBox(panel, label='Trace logging')
        grid.Add(self.check_log_trace, (3, 1), flag=wx.ALIGN_RIGHT)

        self.ent_log = wx.TextCtrl(panel, style=wx.TE_READONLY|wx.TE_MULTILINE)
        grid.Add(self.ent_log, (4, 0), (1, 2), flag=wx.EXPAND)

        grid.AddGrowableRow(4, 1)
        grid.AddGrowableCol(0, 1)
        grid.AddGrowableCol(1, 2)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(grid, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)
        panel.SetSizer(hbox)

        self.ent_ip_address.SetValue(self.ip_address)
        self.ent_port.SetValue(str(self.port))

        monitor = threading.Thread(target=self.text_catcher)
        monitor.daemon = True
        monitor.start()

    def handle_connect(self, e):
        if self.connected:
            BlocklyServer.stop(self.q)
            self.server_process.terminate()
            self.connected = False
            self.btn_connect.SetLabel("Connect")
        else:
            # read entered values and start server
            self.server_process = multiprocessing.Process(target=BlocklyServer.main, args=(self.port, self.version, self.q)) #, kwargs={'out':self.stdoutToQueue})
           # self.server_process = threading.Thread(target=BlocklyServer.main, args=(int(self.port.get()), self.version)) #, kwargs={'out':self.stdoutToQueue})
            self.server_process.start()

            self.connected = True
            self.btn_connect.SetLabel("Disconnect")

    def do_exit(self, e):

        message = wx.MessageDialog(self, "Are you sure you want to quit?", "Quit?", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        if message.ShowModal() == wx.ID_OK:
            # stop server if running
            if self.connected:
          #      BlocklyServer.stop(self.q)
                self.server_process.terminate()
          #      self.connected = False

            message.Destroy()
            self.on_exit_app(e)

        message.Destroy()

    def text_catcher(self):
        while 1:
            (level, level_name, message) = self.q.get()
            min_level = self.trace_log * 5
            if level > min_level:
                self.ent_log.AppendText(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' ' + level_name + ': ' + message + '\n')
                self.ent_log.PageDown()
             #   self.ent_log.yview_pickplace("end")

    def on_exit_app(self, event):
        self.Destroy()


if __name__ == '__main__':
    multiprocessing.freeze_support()

    app = wx.App(False)
    client = BlocklyPropClient(None, 'BlocklyProp')
    client.set_version(VERSION)
    app.MainLoop()