from ws4py.websocket import WebSocket
from serial import Serial, SerialException
from time import sleep
import thread
import re
import logging

__author__ = 'Michel'

OPEN_CONNECTION_STRING = "+++ open port "

# Enable logging for functions outside of the class definition
module_logger = logging.getLogger('blockly')

class SerialSocket(WebSocket):
    def __init__(self, sock, protocols=None, extensions=None, environ=None, heartbeat_freq=None):
        self.logger = logging.getLogger('blockly.serial')
        self.logger.info('Creating serial logger.')

        super(SerialSocket, self).__init__(sock, protocols, extensions, environ, heartbeat_freq)
        self.serial = Serial()

    def received_message(self, message):
        module_logger.info('Message received')
        if message.data[0:len(OPEN_CONNECTION_STRING)] == OPEN_CONNECTION_STRING:
            connection_string = message.data[len(OPEN_CONNECTION_STRING):]

            port = connection_string
            baudrate = 115200

            connection_info = connection_string.split(' ')
            if len(connection_info) == 2:
                port = connection_info[0]
                baudrate = connection_info[1]

            self.serial.baudrate = baudrate
            self.serial.port = port

            try:
                self.logger.info("Opening serial port %s", port)
                self.serial.open()
            except SerialException as se:
                self.logger.error("Failed to connect to %s", port)
                self.logger.error("Serial exception message: %s", se.message)
                self.send("Failed to connect to: %s using baud rate %s\n\r(%s)\n\r" % (port, baudrate, se.message))
                return

            if self.serial.isOpen():
                self.logger.info("Serial port %2 is open.", port)
                self.send("Connection established with: %s using baud rate %s\n\r" % (port, baudrate))
                thread.start_new_thread(serial_poll, (self.serial, self))
            else:
                self.send("Failed to connect to: %s using baud rate %s\n\r" % (port, baudrate))
        else:
            if self.serial.isOpen():
                self.logger.info("Sending serial data")
                self.send(message.data)
                self.serial.write(message.data)

    def close(self, code=1000, reason=''):
        self.logger.info("Closing serial port")
        # close serial connection
        print 'closing'
        self.serial.close()
        super(SerialSocket, self).close(code, reason)


def serial_poll(serial, socket):
    module_logger.debug('Polling serial port.')
    try:
        while serial.isOpen():
            data = serial.read(serial.inWaiting())
            if len(data) > 0:
                # print 'Got:', data
                # data = re.sub("\r", "\n\r", data)
                socket.send(data)
            sleep(0.5)
          #  print 'not blocked'
    except SerialException as se:
        module_logger.error("Serial port exception while polling.")
        module_logger.error("Error message is: %s", se.message )
        print('connection closed')
