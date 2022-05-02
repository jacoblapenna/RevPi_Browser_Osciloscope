import socket

class Server:

    def __init__(self):
        self.ip = "127.0.0.1"
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self._socket.connect(("1.1.1.1", 1))
            self.ip = self._socket.getsockname()[0]
        finally:
            self._socket.close()
