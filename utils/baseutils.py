import os
import platform
import socket


def getpcname():
    n1 = platform.node()
    n2 = socket.gethostname()
    n3 = os.environ.get("COMPUTERNAME")
    if n1 == n2 == n3:
        return n1
    elif n1 == n2:
        return n1
    elif n1 == n3:
        return n1
    elif n2 == n3:
        return n2
    else:
        raise Exception("Computernames are not equal to each other")

if __name__ == "__main__":
    print(getpcname())
