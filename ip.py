import os
import socket

__author__ = 'Michel'

if os.name != "nt":
    import fcntl
    import struct

    def get_interface_ip(if_name):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s',
                                if_name[:15]))[20:24])


def get_lan_ip():
    # Find the client's IP address
    try:
        ip = socket.gethostbyname(socket.gethostname())
    except socket.error as msg:
        print msg.message
        ip = "0.0.0.0"

    if ip.startswith("127.") and os.name != "nt":
        interfaces = [
            "eth0",
            "eth1",
            "eth2",
            "wlan0",
            "wlan1",
            "wifi0",
            "ath0",
            "ath1",
            "ppp0",
            ]

        for if_name in interfaces:
            try:
                ip = get_interface_ip(if_name)
                break
            except IOError:
                pass
    return ip
