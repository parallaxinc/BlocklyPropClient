import multiprocessing
import webview
import logging

from cherrypy.process.servers import check_port

import guiserver


def start_ui(url):
    webview.create_window("BlocklyProp client", url, resizable=True)


if __name__ == '__main__':
    http_port = 41285
    http_host = '127.0.0.1'

    try_port = 0
    free_port_found = False
    while try_port < 10 and not free_port_found:
        try:
            check_port(http_host, http_port)
        except IOError:
            http_port += 1
            try_port += 1
        else:
            free_port_found = True

    if free_port_found:
        gui_server = guiserver.GuiServer()
        server = multiprocessing.Process(target=gui_server.start_server, args=(http_port,))
        server.daemon = True
        server.start()

        logging.warn('Starting ui')

        start_ui("http://localhost:{}/index.html".format(http_port))

        try:
            gui_server.stop_server()
            server.terminate()
        except:
            pass

        exit(0)
    else:
        logging.error('No port found')
        # TODO: show message to user
