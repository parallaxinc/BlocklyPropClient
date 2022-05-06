__author__ = 'Paul Beyleveld'
'''
Based on code from Michel, completely re-written to implement websocket 
compatible with BlocklyProp Solo v1.6.3

This allows programming older hardware like scribbler S2 from Blocklyprop Solo.
'''

from ws4py.websocket import WebSocket
from tempfile import NamedTemporaryFile
from serial import Serial, SerialException
from datetime import datetime, timedelta
from time import sleep
import thread, json, os
import base64

from PropellerLoad import PropellerLoad

# version 1.0.4 matches BlocklyProp Launcher version which BlocklyProp Solo expects when connecting.
VERSION = "1.0.4"

class HandleWebSocket(WebSocket):

    '''
    Overload the wy4py Websocket handler for increased functionality, extend with queue to allow GUI feedback
    '''
    def __init__(self, sock, protocols=None, extensions=None, environ=None, heartbeat_freq=None, queue=None):
        super(HandleWebSocket, self).__init__(sock, protocols, extensions, environ, heartbeat_freq)

        self.queue = queue
        self.handshake_completed = False
        self.com_port = ''
        self.threadrunning = False
        self.monitoring = False
        self.serial = Serial()
        self.serial.dtr = False
        self.serial.rts = False
        self.serial.timeout = 1
        self.term_message = ''
        self.lastaction = ''
        #self.peer_address = WebSocket.peer_address

    '''
    This function is called when the websocket recieves a new message, here we parse the messages and implement the instructions
    '''
    def received_message(self, message):
        response = ''
        self.lastaction = ''
        data = json.loads(message.data)

        #print(message.data)
        #self.queue.put((10, 'INFO', 'recv<' + message.data))

        if data['type'] == 'hello-browser':
            self.queue.put((10, 'INFO', '+ Site connected'))
            response = {
                "type": "hello-client",
                "version": str(VERSION)
            }

        elif data['type'] == 'port-list-request':
            self.queue.put((10, 'INFO', '-> Site requested port list'))
            response = self.get_portlist()
            self.handshake_completed = True

        elif data['type'] == 'pref-port':
            if data['portPath'] is not None:
                self.com_port = data['portPath'].encode('ascii')
                self.queue.put((10, 'INFO', '-> User selected preferred port: ' + str(self.com_port)))
                #print self.com_port
            response = self.get_portlist()
            self.monitoring = False

        elif data['type'] == 'load-prop':
            self.monitoring = False
            if self.serial.isOpen():
                self.serial.close()

            response = {
                "type": "ui-command",
                "action": "message-compile",
                "msg": "\r000-Scanning port COM3"
            }

            self.queue.put((10, 'INFO', "-> Programming on port " + str(data['portPath'])))
            self.send(json.dumps(response))

            try:
                # write the binary payload to temp file
                binary_file = NamedTemporaryFile(mode='w+b', suffix='.elf', delete=False)
                fstr = base64.b64decode(data['payload'])
                binary_file.write(fstr)
                binary_file.close()

                options = "CODE"
                #options = "VERBOSE"
                #options = "CODE_VERBOSE"
                (load_success, load_output, load_err) = self.propellerLoad.download(options, data['action'], binary_file, str(data['portPath']))
            except Exception as e:
                print(e)

            if not load_success:
                response = {
                    "type": "ui-command",
                    "action": "message-compile",
                    "msg": "\r104-" + load_output.rstrip()
                }
                self.queue.put((10, 'INFO', "<- " + str(load_output.rstrip())))
                self.send(json.dumps(response))
                response = {
                    "type": "ui-command",
                    "action": "message-compile",
                    "msg": "\r102-Error: Download Failed!"
                }
                self.queue.put((10, 'INFO', "<- Error: Download Failed!"))
            else:
                response = {
                    "type": "ui-command",
                    "action": "message-compile",
                    "msg": "\r014-Success: " + load_output.rstrip()
                }
                self.queue.put((1, 'TRACE', "<- " + str(load_output.rstrip())))
                self.send(json.dumps(response))
                response = {
                    "type": "ui-command",
                    "action": "message-compile",
                    "msg": "\r005-Success: Download Completed"
                }
                self.queue.put((10, 'INFO', "<- Success: Download Completed"))


            try:
                os.remove(binary_file.name)
            except WindowsError:
                #print("Binary file does not exist")
                self.queue.put((10, 'WARNING', '+ Failed to delete temp file, file not found'))

        elif data['type'] == 'serial-terminal':

            if data['action'] == 'open':
                self.serial.baudrate = data['baudrate']
                self.serial.port = data['portPath']
                self.monitoring = True
                self.lastaction = 'openser'

            elif data['action'] == 'close':
                self.monitoring = False

            elif data['action'] == 'msg':
                self.term_message = data['msg']


        if response != '':
            #print(response)
            self.send(json.dumps(response))

        if self.handshake_completed and not self.threadrunning:
            #print "INFO: Starting poll thread"
            self.queue.put((1, 'TRACE', '+ Starting port polling thread: ' + str(self.peer_address[1])))
        #self.session_open = True
            thread.start_new_thread(comport_poll, (self.serial, self.queue, self, self.peer_address[1]))
            self.threadrunning = True

    def opened(self):
        self.queue.put((1, 'TRACE', '+ websocket opened: ' + str(self.peer_address[1])))
        #print "opened"

    '''
    Close any threads associated to the websocket that is terminated
    '''
    def close(self, code=1000, reason=''):
        self.threadrunning = False

        if not self.server_terminated:
            self.server_terminated = True
            try:
                self._write(self.stream.close(code=code, reason=reason).single(mask=self.stream.always_mask))
            except Exception as ex:
                self.queue.put((1, 'ERROR', '+ Error when terminating the websocket: ' + str(ex)))
        # close websocket connection
        #self.handshake_completed = False

        #print str(self.peer_address[1]) + "> " + 'closing'
        self.queue.put((10, 'INFO', '+ closing websocket: ' + str(self.peer_address[1])))

    '''
    User the propeller loader to detect ports and build available serial port list
    '''
    def get_portlist(self):
        ports = self.propellerLoad.get_ports()
        filtered_ports = []

        if self.com_port != '' and self.com_port not in ports:
            #self.com_port = ''
            #filtered_ports.append('')
            #print 'WARNING: Port no longer detected'
            self.queue.put((10, 'WARNING', '+ Previously selected port no longer detected, cable unplugged?'))

        filtered_ports.append(self.com_port.encode('ascii'))

        for port in ports:
            if ' bt ' not in port.lower() and 'bluetooth' not in port.lower() and self.com_port.lower() != port.lower():
                filtered_ports.append(port)
        self.queue.put((10, 'INFO', '<- [%s] Sending port list %s' % (str(self.peer_address[1]), str(filtered_ports))))

        return {
            "type": "port-list",
            "ports": filtered_ports
        }


    propellerLoad = PropellerLoad()

'''
Thread that will asynchronously poll available serial ports on a 5 second interval and update via open websocket
'''
def comport_poll(serial, queue, socket, poll_id):

    last_time = datetime.now()

    while (not socket.client_terminated or not socket.server_terminated) and socket.threadrunning:
        curr_time = datetime.now()
        #print socket.lastaction

        #check weather monitoring is requested
        if socket.monitoring:

            #open the serial port
            if not serial.isOpen() or socket.lastaction == 'openser':
                #queue.put((1, 'TRACE', '+ Polling serial port.'))
                packetID = 1
                socket.lastaction = ''

                try:
                    #sleep(0.5)

                    queue.put((10, 'INFO', '+ [%s] Opening serial port: %s' % (str(poll_id), str(serial.port))))
                    if not serial.isOpen():
                        serial.open()
                    serial.flushInput()
                    serial.flushOutput()

                    serial.setDTR(True)
                    #sleep(0.025)
                    serial.setDTR(False)

                    sleep(0.2)

                    serial.flushInput()
                    serial.flushOutput()

                except SerialException as se:
                    queue.put((10, 'ERROR', '+ Failed to connect to: ' + str(serial.port)))
                    queue.put((1, 'TRACE', '+ Serial exception message: ' + str(se.message)))
                    # self.send(base64.b64encode("Failed to connect to: %s using baud rate %s\n\r(%s)\n\r" % (port, baudrate, se.message)))
                    #print "Failed to connect to serial port: " + str(se.message)
                    response = {
                        "type": "serial-terminal",
                        "packetID": "1",
                        #"msg": base64.b64encode("Failed to connect.\rPlease close this terminal and select a connected port.")
                        "msg": base64.b64encode("\rError: Failed to connect to: %s using baud rate %s\n\rPlease close this terminal and select a connected port.\n\r" % (serial.port, serial.baudrate))
                    }
                    socket.monitoring = False
                    socket.send(json.dumps(response))
            else:
                data = serial.read(serial.inWaiting())
                if data:
                    queue.put((1, 'TRACE', '+ Data received from device: ' + data))

                    response = {
                        "type": "serial-terminal",
                        "packetID": str(packetID),
                        "msg": base64.b64encode(data)
                    }

                    socket.send(json.dumps(response))
                    # socket.send(base64.b64encode(message))
                    packetID = packetID + 1
        else:
            if serial.isOpen():
                queue.put((10, 'INFO', '+ [%s] Closing serial port: %s' % (str(poll_id), str(serial.port))))
                serial.close()

        try:
            # send updated port list every 5 seconds
            if (curr_time - last_time >= timedelta(seconds=5)):
                last_time = curr_time
                response = socket.get_portlist()
                # print str(socket.peer_address[1]) + "> " + str(response)
                socket.send(json.dumps(response))
        except Exception as e:
            # print(e)
            queue.put((1, 'TRACE', '+ port list exception: ' + str(e)))

        sleep(0.5)


    if serial.isOpen():
        queue.put((10, 'INFO', '+ Closing serial port: ' + str(serial.port)))
        serial.close()
        socket.monitoring = False

    queue.put((1, 'TRACE', '+ port list polling closed: ' + str(socket.peer_address[1])))

