__author__ = 'Michel'

from ws4py.websocket import WebSocket
from serial import Serial, SerialException
from time import sleep
import thread
import re


OPEN_CONNECTION_STRING = "+++ open port "


class SerialSocket(WebSocket):
    def __init__(self, sock, protocols=None, extensions=None, environ=None, heartbeat_freq=None):
        super(SerialSocket, self).__init__(sock, protocols, extensions, environ, heartbeat_freq)
        self.serial = Serial()

    def received_message(self, message):
        if message.data[0:len(OPEN_CONNECTION_STRING)] == OPEN_CONNECTION_STRING:
            port = message.data[len(OPEN_CONNECTION_STRING):]
            self.serial.port = port
            self.serial.baudrate = 115200
            try:
                self.serial.open()
            except SerialException as se:
                self.send("Failed to connect to: " + port + "\n\r(" + se.message + ")\n\r")
                return

            if self.serial.isOpen():
                self.send("Connection established with: " + port + "\n\r")
                thread.start_new_thread(serial_poll, (self.serial, self))
            else:
                self.send("Failed to connect to: " + port + "\n\r")
        else:
            if self.serial.isOpen():
                self.send(message.data)
                self.serial.write(message.data)

    def close(self, code=1000, reason=''):
        # close serial connection
        print 'closing'
        self.serial.close()
        super(SerialSocket, self).close(code, reason)


def serial_poll(serial, socket):
    try:
        while serial.isOpen():
            data = serial.read(serial.inWaiting())
            if len(data) > 0:
                # print 'Got:', data
                # data = re.sub("\r", "\n\r", data)
                socket.send(data)
            sleep(0.5)
          #  print 'not blocked'
    except SerialException:
        print('connection closed')
