__author__ = 'Michel'

import cherrypy
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool

# BlocklyProp imports
from SerialSocket import SerialSocket
from PropellerLoad import PropellerLoad
from SpinCompiler import SpinCompiler
from PropCCompiler import  PropCCompiler



PORT = 6009
VERSION = 0.1

class BlocklyServer(object):

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    @cherrypy.tools.allow(methods=['GET'])
    def index(self):
        cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
        serverinfo = {
            "server": "BlocklyPropHTTP",
            "version": VERSION
        }
        return serverinfo


    @cherrypy.expose(alias='ports.json')
    @cherrypy.tools.json_out()
    @cherrypy.tools.allow(methods=['GET'])
    def ports(self):
        cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
        return self.propellerLoad.get_ports()


    @cherrypy.expose(alias='compile.action')
    @cherrypy.tools.json_out()
    @cherrypy.tools.allow(methods=['POST'])
    def compile(self, action, language, code, comport=None):
        cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'

        result = self.compiler[language].handle(action, code, comport)

        return result

    @cherrypy.expose(alias='serial.connect')
    def serial_socket(self):
        cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
        handler = cherrypy.request.ws_handler

    propellerLoad = PropellerLoad()

    compiler = {
        "spin" : SpinCompiler(propellerLoad),
        "prop-c": PropCCompiler(propellerLoad)
    }

def main():
#    try:
        cherrypy.config.update({'server.socket_port': PORT})
        WebSocketPlugin(cherrypy.engine).subscribe()
        cherrypy.tools.websocket = WebSocketTool()

        cherrypy.quickstart(BlocklyServer(), '/', config={'/serial.connect': {
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

if __name__ == '__main__':
    main()
