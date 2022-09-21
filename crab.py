import socketserver
from parse_http import parse_http_request
from builtin import plain_response, html_response
import re


def path(regex_path: str, func):
    return regex_path, func

class Crab:
    def __init__(self, views=[], host="0.0.0.0", port=5000):
        self.host = host
        self.port = port
        self.views = views

        class TCPHandler(socketserver.BaseRequestHandler):
            def handle(self):
                self.data = self.request.recv(1024)
                self.http_request = parse_http_request(self.data)

                # find matching view
                for regex_path, func in views:
                    paths_match = re.match(regex_path, self.http_request.path)
                    if paths_match:
                        groups = paths_match.groups()
                        result = func(self, *groups)
                        if result:
                            self.request.sendall(result)
                        return

            def request_bytes(self):
                self.request.recv(1024)

            def send_bytes(self, content):
                self.request.sendall(content)

            def get_request(self):
                return self.http_request

        self.handler = TCPHandler

    def start(self):
        try:
            with socketserver.TCPServer((self.host, self.port), self.handler) as server:
                print(f"Hosted at http://{self.host}:{self.port}")
                server.serve_forever()
        except KeyboardInterrupt:
            print("exited")

