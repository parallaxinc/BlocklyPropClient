__author__ = 'Michel'

"""Simple HTTP Server.

This module builds on BaseHTTPServer by implementing the standard GET
and HEAD requests in a fairly straightforward manner.

"""


__version__ = "0.1"

__all__ = ["BlocklyPropHTTPRequestHandler"]

import os
import posixpath
import BaseHTTPServer
import urllib
import cgi
import shutil
import json
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
from cgi import parse_header, parse_multipart
from urlparse import parse_qs

from PropellerLoad import PropellerLoad
from SpinCompiler import SpinCompiler
from PropCCompiler import  PropCCompiler


class BlocklyPropHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    """Simple HTTP request handler with GET and HEAD commands.

    The GET and HEAD requests are identical except that the HEAD
    request omits the actual contents of the file.

    """

    server_version = "BlocklyPropHTTP/" + __version__

    def do_GET(self):
        """Serve a GET request."""
        path = self.path
        print("GET:", path)
        f = StringIO()
        if path == "/ports.json":
            global propellerLoad
            ports = propellerLoad.get_ports()
            f.write(ports)
        elif path == "/serverinfo.json":
            serverinfo = {
                "server":"BlocklyPropHTTP",
                "version":__version__
            }
            f.write(json.dumps(serverinfo))

        length = f.tell()
        f.seek(0)

        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-type", "text/json")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        if f:
            self.copyfile(f, self.wfile)
            f.close()

    def do_POST(self):
        """Serve a POST request."""
        postvars = self.parse_POST()
        action = postvars.get("action")[0]
        language = postvars.get("language")[0]
        code = postvars.get("code")[0]
        com_port = postvars.get("com-port")
        if com_port is not None:
            com_port = com_port[0]

        global compiler
        result = compiler[language].handle(action, code, com_port)

        f = StringIO()
        f.write(json.dumps(result))
        length = f.tell()
        f.seek(0)

        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-type", "text/json")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        if f:
            self.copyfile(f, self.wfile)
            f.close()


    def copyfile(self, source, outputfile):
        """Copy all data between two file objects.

        The SOURCE argument is a file object open for reading
        (or anything with a read() method) and the DESTINATION
        argument is a file object open for writing (or
        anything with a write() method).

        The only reason for overriding this would be to change
        the block size or perhaps to replace newlines by CRLF
        -- note however that this the default server uses this
        to copy binary data as well.

        """
        shutil.copyfileobj(source, outputfile)

    def parse_POST(self):
        ctype, pdict = parse_header(self.headers['content-type'])
        if ctype == 'multipart/form-data':
            postvars = parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            postvars = parse_qs(
                    self.rfile.read(length),
                    keep_blank_values=1)
        else:
            postvars = {}
        return postvars


propellerLoad = PropellerLoad()


compiler = {
    "spin" : SpinCompiler(propellerLoad),
    "prop-c": PropCCompiler(propellerLoad)
}