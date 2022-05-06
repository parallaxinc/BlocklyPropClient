import os
import sys
import logging
import functools

import cherrypy
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool

# BlocklyProp imports
from HandleWebSocket import HandleWebSocket
from PropellerLoad import PropellerLoad

__author__ = 'Michel'

PORT = 6009

# Enable logging for functions outside of the class definition
module_logger = logging.getLogger('blockly.server')


class BlocklyServer(object):

    def __init__(self, version, app_version, queue):
        self.logger = logging.getLogger('blockly.server')
        self.logger.info('Creating server logger.')

        self.version = version
        self.app_version = app_version
        self.queue = queue
        #self.ws_sessions = []

        # Find the path from which application was launched
        # realpath expands to full path if __file__ or sys.argv[0] contains just a filename
        self.appdir = os.path.dirname(os.path.realpath(__file__))
        if self.appdir == "" or self.appdir == "/":
            # launch path is blank; try extracting from argv
            self.appdir = os.path.dirname(os.path.realpath(sys.argv[0]))

        self.logger.debug("BlocklyServer.py: Application started from: %s", self.appdir)

        queue.put((10, 'INFO', 'Server started'))

    propellerLoad = PropellerLoad()

    @cherrypy.expose()
    def index(self):
        #cherrypy.request.remote.ip

        #self.queue.put((1, 'TRACE', 'Server poll received'))
        WebSocketHandler = cherrypy.request.ws_handler
        self.queue.put((1, 'TRACE', "BlocklyProp connection: " + str(WebSocketHandler.peer_address[1])))

        #print("BlocklyProp connection: " + str(WebSocketHandler.peer_address[1]))
        # Close all but the existing web socket from 127.0.0.1
        '''
        existing = False
        for ws_session in self.ws_sessions:
            #print("IP: %s    PORT: %s" % (ws_session.peer_address[0],ws_session.peer_address[1]))
            #self.queue.put((1, 'TRACE', "Existing: " + str(ws_session.peer_address[1])))
            if WebSocketHandler.peer_address[0] == ws_session.peer_address[0]:
                WebSocketHandler.close()
                existing = True
                self.queue.put((1, 'TRACE', 'Existing detected, closed: ' + str(WebSocketHandler.peer_address[1])))

        if not existing:
            self.ws_sessions.append(WebSocketHandler)
        '''
        pass


def main(port, version, app_version, queue):
    module_logger.info("Server starting")
    queue.put((10, 'INFO', 'Server starting'))

#    try:
    # Set cherrypy IP and port details
    cherrypy.config.update({'server.socket_port': port, 'server.socket_host': '0.0.0.0', 'server.thread_pool': 1})
    WebSocketPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()

    queue.put((10, 'INFO', 'Websocket configured'))

    cherrypy.quickstart(BlocklyServer(version, app_version, queue), '/', config={'/': {
        'tools.websocket.on': True,
        'tools.websocket.handler_cls': functools.partial(HandleWebSocket,
                                                         queue=queue,
                                                         ),
    }})


def stop(queue):
    cherrypy.engine.stop()
    queue.put((10, 'INFO', 'Server disconnected'))

if __name__ == '__main__':
    main(PORT, 0.01, None)
