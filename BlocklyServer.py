__author__ = 'Michel'

import cherrypy
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool

# BlocklyProp imports
from SerialSocket import SerialSocket
from PropellerLoad import PropellerLoad
from SpinCompiler import SpinCompiler
from PropCCompiler import PropCCompiler

import sys, os


PORT = 6009
VERSION = 0.2


class BlocklyServer(object):

    def __init__(self, version, queue):
        self.version = version
        self.queue = queue
        queue.put((10, 'INFO', 'Server started'))

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    @cherrypy.tools.allow(methods=['GET'])
    def index(self):
        cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
        serverinfo = {
            "server": "BlocklyPropHTTP",
            "version": self.version
        }
        self.queue.put((1, 'TRACE', 'Server poll received'))
        return serverinfo


    @cherrypy.expose(alias='ports.json')
    @cherrypy.tools.json_out()
    @cherrypy.tools.allow(methods=['GET'])
    def ports(self):
        cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
        self.queue.put((3, 'DEBUG', 'Port list retrieved'))
        
        ports = self.propellerLoad.get_ports()
        filtered_ports = []
        for port in ports:
            if ' bt ' not in port.lower() and 'bluetooth' not in port.lower():
                filtered_ports.append(port)
        return filtered_ports



    @cherrypy.expose(alias='compile.action')
    @cherrypy.tools.json_out()
    @cherrypy.tools.allow(methods=['POST'])
    def compile(self, action, language, code, comport=None):
        cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
        
        file = open( "c_code_file", 'w' )
        file.write( code )
        file.close()
        
        result = self.compiler[language].handle(action, code, comport)
        self.queue.put((10, 'INFO', 'Application compiled'+ ' (' + action + ' : ' + language + ')'))
        return result

    @cherrypy.expose(alias='serial.connect')
    def serial_socket(self):
        cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
        self.queue.put((10, 'INFO', 'Serial socket set up'))
        handler = cherrypy.request.ws_handler

    propellerLoad = PropellerLoad()

    compiler = {
        "spin": SpinCompiler(propellerLoad),
        "prop-c": PropCCompiler(propellerLoad)
    }


def main(port, version, queue):
    # sys.stdout = open('stdfile.txt', 'w')
    # sys.stderr = open('errfile.txt', 'w')
#    try:
    cherrypy.config.update({'server.socket_port': port, 'log.access_file': 'access.txt'})
    WebSocketPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()

    cherrypy.quickstart(BlocklyServer(version, queue), '/', config={'/serial.connect': {
        'tools.websocket.on': True,
        'tools.websocket.handler_cls': SerialSocket
    }})

#        handler = BlocklyPropHTTPRequestHandler
#        httpd = SocketServer.TCPServer(("", PORT), handler)
#        print('started httpserver...')
#        httpd.serve_forever()
#    except KeyboardInterrupt:
#        print('^C received, shutting down server')

#        httpd.socket.close()


def stop(queue):
    cherrypy.engine.stop()
    queue.put((10, 'INFO', 'Server disconnected'))

if __name__ == '__main__':
    main(PORT, VERSION, None)
