import base64
import os
import tempfile

import cherrypy
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool

# BlocklyProp imports
from SerialSocket import SerialSocket
from PropellerLoad import PropellerLoad

__author__ = 'Michel'

PORT = 6009


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
        return self.propellerLoad.get_ports()


    @cherrypy.expose(alias='load.action')
    @cherrypy.tools.json_out()
    @cherrypy.tools.allow(methods=['POST'])
    def load(self, action, binary, extension, comport=None):
        cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'

        binary_file = tempfile.NamedTemporaryFile(suffix=extension, delete=False)
        binary_file.write(base64.b64decode(binary))
        binary_file.close()

        (success, out, err) = self.propellerLoad.load(action, binary_file, comport)
        self.queue.put((10, 'INFO', 'Application loaded (%s)' % action))

        os.remove(binary_file.name)

        result = {
            'message': out + err
        }
        return result

    @cherrypy.expose(alias='serial.connect')
    def serial_socket(self):
        cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
        self.queue.put((10, 'INFO', 'Serial socket set up'))
        handler = cherrypy.request.ws_handler

    propellerLoad = PropellerLoad()


def main(port, version, queue):
    queue.put((10, 'INFO', 'Server starting'))
    # sys.stdout = open('stdfile.txt', 'w')
    # sys.stderr = open('errfile.txt', 'w')
#    try:
    cherrypy.config.update({'server.socket_port': port})
    WebSocketPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()

    queue.put((10, 'INFO', 'Websocket configured'))

    cherrypy.quickstart(BlocklyServer(version, queue), '/', config={'/serial.connect': {
        'tools.websocket.on': True,
        'tools.websocket.handler_cls': SerialSocket
    }})


def stop(queue):
    cherrypy.engine.stop()
    queue.put((10, 'INFO', 'Server disconnected'))

if __name__ == '__main__':
    main(PORT, 0.01, None)
