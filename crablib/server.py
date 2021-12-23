import re
import socketserver
import webbrowser
import argparse
from functools import partialmethod
from typing import Callable, Any, Optional
from socketserver import BaseRequestHandler

from crablib.http.errors import HttpError
from crablib.http.parse import Request, parse_request, Response
from crablib.http.path import Path
from crablib.http.response import http_404
from urls import urls


class CrabServer(socketserver.BaseRequestHandler):

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
                    self.request.sendall(self.http_error(e).write_raw())
        self.request.sendall(self.http_error(HttpError(404)).write_raw())

    @classmethod
    def http_error(cls, e: Optional[HttpError]) -> Response:
        return http_404('plain/text', 'error 404'.encode())


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
