from SocketIOClient import SocketIOClient


def authenticate_callback():
    print('authenticationresult')


class WebSocketConnection:

    def __init__(self, identifier):
        self.identifier = identifier

        self.socketIO = None

    def authenticate(self, login, password):
        print("Connect")
        self.socketIO = SocketIOClient('127.0.0.1', 8081, wait_for_connection=False)  # , LoggingNamespace)


        authentication_data = {
            'login': login,
            'password': password
        }

        # self.socketIO.emit('authenticate', authentication_data, authenticate_callback)

    def disconnect(self):
        print("Disconnect")
        self.socketIO.disconnect()
        self.socketIO = None






