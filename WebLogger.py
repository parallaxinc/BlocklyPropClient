import logging

from ws4py.websocket import WebSocket


class WebLogger(logging.Handler):

    def emit(self, record):
        # print('Log line: ' + self.format(record))
        log_line = self.format(record)
        WebLoggerSocket.send_log_line(log_line)


class WebLoggerSocket(WebSocket):

    sockets = []

    @staticmethod
    def send_log_line(log_line):
        for socket in WebLoggerSocket.sockets:
            try:
                socket.send({'log-line': log_line})
            except Exception as e:
                print(e.message)

    def __init__(self, sock, protocols=None, extensions=None, environ=None, heartbeat_freq=None):
        super(WebLoggerSocket, self).__init__(sock, protocols, extensions, environ, heartbeat_freq)
        WebLoggerSocket.sockets.append(self)

    def received_message(self, message):
        pass

    def terminate(self):
        super(WebLoggerSocket, self).terminate()
        WebLoggerSocket.sockets.remove(self)
