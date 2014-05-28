__author__ = 'Michel'

import SocketServer

from BlocklyPropHTTPRequestHandler import BlocklyPropHTTPRequestHandler

PORT = 6009


def main():
    try:
        handler = BlocklyPropHTTPRequestHandler
        httpd = SocketServer.TCPServer(("", PORT), handler)
        print('started httpserver...')
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('^C received, shutting down server')
        httpd.socket.close()

if __name__ == '__main__':
    main()
