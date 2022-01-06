import re
import socketserver
import webbrowser
import argparse
from functools import partialmethod
from typing import Callable, Any, Optional
from socketserver import BaseRequestHandler

from crablib.http.errors import HttpError
from crablib.http.types import Request, Response, Frame
from crablib.http.websocket import Connection
from crablib.http.parse import parse_request
from crablib.http.response import http_404, handshake_response
from crabserver.path import Path
from urls import urls


class CrabServer(socketserver.BaseRequestHandler):

    clients = []

    def handle(self):
        raw: bytes = self.request.recv(2048)
        if len(raw) == 0: return
        request: Request = parse_request(raw)
        self.match(request)


    def match(self, request):
        item: Path
        for item in urls:
            match = re.match(item.regex, request.path)
            if match:
                try:
                    item.view(self, request)
                    return
                except HttpError as e:
                    self.http_error(e)
        self.http_error(HttpError(404))

    def handshake(self, request):
        self.clients.append(self)
        key = request.headers['Sec-WebSocket-Key']
        response = handshake_response(key)
        for socket in self.clients:
            try:
                socket.sendall(response)
            except OSError:
                pass

    def ws_conn(self, request):
        print(request.headers)
        key = request.headers['Sec-WebSocket-Key']
        response = handshake_response(key)
        return Connection(self, request, response)

    def http_error(self, e: Optional[HttpError]):
        if e:
            response = http_404('plain/text', f'http error: {e.status_code}'.encode())
            self.sendall(response)

    def sendall(self, content: Response) -> None:
        try:
            self.request.sendall(content.write_raw())
        except OSError:
            pass

    def sendframe(self, frame: Frame) -> None:
        try:
            self.request.sendall(frame.write_raw())
        except OSError:
            pass


def startserver(server, HOST, PORT):
    crabserver: Callable[[Any], BaseRequestHandler] = server
    partialmethod(crabserver, server.http_error)
    socketserver.ThreadingTCPServer.allow_reuse_address = True

    with socketserver.ThreadingTCPServer((HOST, int(PORT)), crabserver) as server:
        webbrowser.open(f'http://{HOST}:{PORT}')
        try:
            print(f'starting server for {HOST} at {PORT}')
            server.serve_forever()

        except KeyboardInterrupt:
            print('shutting down...')
            server.shutdown()
            server.server_close()


if __name__ == '__main__':
    HOST, PORT = '0.0.0.0', 8000
    parser = argparse.ArgumentParser()
    parser.add_argument("--bind", type=str, help="bind host and port")
    args = parser.parse_args()

    if args.bind:
        HOST, PORT = args.bind.split(':')

    def error(e: Exception) -> bytes:
        return b'Error 404!'

    startserver(HOST, PORT, error)
