from socketIO_client import SocketIO, LoggingNamespace, BaseNamespace

from SocketIOClient import SocketIOClient


class ClientNamespace(LoggingNamespace):

    def on_aaa_response(self, *args):
        print('on_aaa_response', args)

    def on_test2_response(self, message):
        print('test2_response', message)


def on_test_response(message):
    print('test_response', message)

def on_serial_connect_response(message):
    print('test_response', message)

socketIO = SocketIOClient('127.0.0.1', 8081)  # , LoggingNamespace)
socketIO.on('test', on_test_response)
socketIO.on('serial connect', on_serial_connect_response, '/client')
#socketIO.emit('test2', {})

client_namespace = socketIO.define(ClientNamespace, '/client')
client_namespace.emit('serial connect', {'test': 'hello'})
#socketIO.emit('serial connect', {'test': 'hello'}, path='/client')

# client_namespace = socketIO.define(ClientNamespace, '/client')

socketIO.wait(seconds=1)

socketIO.disconnect()
