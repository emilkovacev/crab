from crablib.http.parse import Response
from crablib.http.response import http_404
from crablib.server import startserver, CrabServer


class Server(CrabServer):
    def http_error(self, e) -> Response:
        return http_404('text/plain', 'new http error!'.encode())


startserver(Server, '0.0.0.0', 8000)
