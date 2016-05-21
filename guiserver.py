import os
import sys

import cherrypy
import logging

from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool

from utils.userpreferences import  UserPreferences
import weblogger


class GuiWebApplication:

    def __init__(self, client):
        self.client = client
        self.user_preferences = UserPreferences()

    @cherrypy.expose(alias='login.do')
    @cherrypy.tools.json_out()
    @cherrypy.tools.allow(methods=['POST'])
    def login(self, login, password, identifier):
        self.client.logged_in = True
        return {
            'login': login,
            'password': password,
            'identifier': identifier
        }

    @cherrypy.expose(alias='test')
    @cherrypy.tools.allow(methods=['GET'])
    def index(self):
        return "Hello"

    @cherrypy.expose(alias='ports.json')
    @cherrypy.tools.json_out()
    @cherrypy.tools.allow(methods=['GET'])
    def ports(self):
        return []

    @cherrypy.expose(alias='logging.stream')
    def logging(self):
        handler = cherrypy.request.ws_handler


class GuiServer:

    http_port = 8080

    def __init__(self):
        self.logged_in = False

    def start_server(self, http_port):
        self.http_port = http_port

        web_logger = weblogger.WebLogger()
        logging.getLogger('').addHandler(web_logger)

        app_dir = os.path.dirname(sys.argv[0])

        cherrypy.config.update({'server.socket_port': self.http_port})
        WebSocketPlugin(cherrypy.engine).subscribe()
        cherrypy.tools.websocket = WebSocketTool()

        cherrypy.quickstart(GuiWebApplication(self), '/', config={
            '/': {
                'tools.staticdir.root': app_dir
            },
            '/index.html': {
                'tools.staticfile.on': True,
                'tools.staticfile.filename': os.path.join(app_dir, 'static/index.html')
            },
            '/static': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': os.path.join(app_dir, 'static/')
            },
            '/libs': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': os.path.join(app_dir, 'bower_components/')
            },
            '/logging.stream': {
                'tools.websocket.on': True,
                'tools.websocket.handler_cls': weblogger.WebLoggerSocket
            }
        })

    @staticmethod
    def stop_server():
        cherrypy.engine.stop()


if __name__ == "__main__":
    gui_server = GuiServer()
    gui_server.start_server(8080)
