__author__ = 'Michel'

import SocketServer
import platform
from tkMessageBox import showerror
import os

import BlocklyPropHTTPRequestHandler


PORT = 6009

handler = BlocklyPropHTTPRequestHandler.BlocklyPropHTTPRequestHandler
httpd = SocketServer.TCPServer(("", PORT), handler)

httpd.serve_forever()
