import json
import logging

from ws4py.websocket import WebSocket


class StreamSocket(WebSocket):

    sockets = []

    @staticmethod
    def send_event(code):
        for socket in StreamSocket.sockets:
            try:
                socket.send({'code': code})
            except Exception as e:
                print(e.message)

    def __init__(self, sock, protocols=None, extensions=None, environ=None, heartbeat_freq=None):
        super(StreamSocket, self).__init__(sock, protocols, extensions, environ, heartbeat_freq)
        StreamSocket.sockets.append(self)

    def received_message(self, message):
        event = json.loads(message.data)
        handler = getattr(self, 'handler_' + event['code'], None)
        if handler is not None:
            handler(event)
        else:
            logging.warn("Missing handler: handler_%s", event['code'])

    def terminate(self):
        super(StreamSocket, self).terminate()
        StreamSocket.sockets.remove(self)

    def handler_connected(self, event):
        print('connected')
