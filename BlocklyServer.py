import base64
import os
import sys
import tempfile
import logging

import cherrypy
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool

# BlocklyProp imports
from SerialSocket import SerialSocket
from PropellerLoad import PropellerLoad

__author__ = 'Michel'

PORT = 6009

# Enable logging for functions outside of the class definition
module_logger = logging.getLogger('blockly.server')


class BlocklyServer(object):

    def __init__(self, version, queue):
        self.logger = logging.getLogger('blockly.server')
        self.logger.info('Creating server logger.')

        self.version = version
        self.queue = queue
	# self.appdir = os.path.dirname(sys.argv[0])
	self.appdir = os.path.dirname(os.path.realpath(__file__))
        self.logger.debug("Application started from: %s", self.appdir)

        queue.put((10, 'INFO', 'Server started'))

    propellerLoad = PropellerLoad()

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
        self.logger.debug('Server poll received')
        return serverinfo


    @cherrypy.expose(alias='ports.json')
    @cherrypy.tools.json_out()
    @cherrypy.tools.allow(methods=['GET'])
    def ports(self):
        cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
        self.queue.put((3, 'DEBUG', 'Port list retrieved'))
        self.logger.debug('Port list retreived')

        ports = self.propellerLoad.get_ports()
        if len(ports) > 0:
            filtered_ports = []
            for port in ports:
                self.logger.debug('Port %s discovered.', port)
                if ' bt ' not in port.lower() and 'bluetooth' not in port.lower():
                    filtered_ports.append(port)
                    self.logger.debug("Port %2 appended to list.", port)
            return filtered_ports
        else:
            # No useable ports detected. Need to determine how the browser
            # handles an empty list of available ports.
            self.logger.debug("No ports detected. Replying with /dev/null")
            return '/dev/null'


    @cherrypy.expose(alias='load.action')
    @cherrypy.tools.json_out()
    @cherrypy.tools.allow(methods=['POST'])
    def load(self, action, binary, extension, comport=None):
        if action is None:
            self.logger.error('Load action is undefined.')
            return {
                'message': 'Load action is undefined',
                'success': False
            }

        cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'

        self.logger.debug('Writing program payload to temp file.')

        binary_file = tempfile.NamedTemporaryFile(suffix=extension, delete=False)
        binary_file.write(base64.b64decode(binary))
        binary_file.close()

        self.logger.debug('%s saved.', binary_file.name)

        self.logger.debug('Loading program to device.')

        (success, out, err) = self.propellerLoad.load(action, binary_file, comport)
        self.queue.put((10, 'INFO', 'Application loaded (%s)' % action))

        self.logger.info('Application load complete.')

        os.remove(binary_file.name)

        result = {
            'message': out + err,
            'success': success
        }
        return result

    @cherrypy.expose(alias='serial.connect')
    def serial_socket(self):
        cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
        self.queue.put((10, 'INFO', 'Serial socket set up'))
        handler = cherrypy.request.ws_handler


def main(port, version, queue):
    module_logger.info("Server starting")
    queue.put((10, 'INFO', 'Server starting'))

#    try:
    # Set cherrypy IP and port details
    cherrypy.config.update({'server.socket_port': port, 'server.socket_host': '0.0.0.0'})
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
