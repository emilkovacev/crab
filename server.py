from crablib.http.types import Response
from crablib.http.response import http_404
from crabserver.server import startserver, CrabServer


class Server(CrabServer):
    def http_error(self, e):
        response = http_404('text/plain', f'super duper error {e.status_code}'.encode())
        self.sendall(response)


startserver(Server, '0.0.0.0', 8000)
