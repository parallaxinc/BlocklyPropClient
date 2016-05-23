from SocketIOClient import SocketIOClient


def authenticate_callback():
    print('authenticationresult')

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

        self.socketIO.emit('authenticate', authentication_data, authenticate_callback)




