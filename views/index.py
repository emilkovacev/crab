from crablib.fileIO import read_file
from crablib.http.response import InvalidRequest
from crablib.http.response import http_200
from crablib.http.types import Request
from crablib.http.websocket_response import text_response, binary_response, pong



def home(socket, request: Request):
    if request.request_type == 'GET':
        response = http_200('text/html', read_file(f'html/handshake.html'), 'utf-8')
        return socket.sendall(response)
    else:
        raise InvalidRequest


def websocket(socket, request: Request):
    if request.request_type == 'GET':
        with socket.ws_conn(request) as conn:
            while True:
                frame = conn.request_frame()
                if frame.opcode == 0x8: return
                elif frame.opcode == 0x9: conn.send_frame(pong())
                else: conn.send_frame(frame)
    else:
        raise InvalidRequest
