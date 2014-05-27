__author__ = 'Michel'

#import SimpleHTTPServer
import SocketServer
import threading
import atexit
from BlocklyPropHTTPRequestHandler import BlocklyPropHTTPRequestHandler

PORT = 6009


class BlocklyPropServer:
    def __init__(self):
        handler = BlocklyPropHTTPRequestHandler
        self.httpd = SocketServer.TCPServer(("", PORT), handler)

        self.server_thread = threading.Thread(target=start_server, args=("Server-Thread", self.httpd))
        self.server_thread.start()

        #atexit.register(self.stop)

    def stop(self):
        self.httpd.shutdown()



def start_server(thread_name, server):
    server.serve_forever()
