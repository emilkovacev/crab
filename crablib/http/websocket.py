import base64
import hashlib

from crablib.http.parse import parse_frame
from crablib.http.types import Request, Response, Frame
from crablib.http.websocket_response import end_connection


def generate_key(key: str) -> str:
    GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
    hashed_key: bytes = hashlib.sha1(key.encode() + GUID.encode()).digest()
    encoded_key = base64.b64encode(hashed_key)
    return encoded_key.decode()


class Connection:
    def __init__(self, server, request: Request, response: Response):
        self.server = server
        self.request = request
        self.response = response

    def __enter__(self):
        self.server.clients.append(self.server)
        for socket in self.server.clients:
            try:
                socket.sendall(self.response)
            except OSError:
                pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        for socket in self.server.clients:
            frame = end_connection()
            socket.sendframe(frame)

    def request_frame(self):
        return parse_frame(self.server.request.recv(1024))

    def send_frame(self, frame: Frame):
        self.server.sendframe(frame)
