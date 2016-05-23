from multiprocessing import Queue

from SocketIOClient import SocketIOClient


q = None


def callback(data):
    q.put(data)


class WebSocketConnection:

    def __init__(self, identifier):
        self.identifier = identifier

        self.socketIO = None

    def authenticate(self, login, password):
        self.socketIO = SocketIOClient('127.0.0.1', 8081)  # , LoggingNamespace)

        authentication_data = {
            'login': login,
            'password': password
        }

        global q
        q = Queue()
        self.socketIO.emit('authenticate', authentication_data, callback)
        response = q.get()
        if response['success']:
            return True
        return False


