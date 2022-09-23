import socketserver
from .http_objects import HTTPRequest
from .builtin import html_response
import re

MAX_HEADER_REFRESH = 20
DEFAULT_REQUEST_SIZE = 1024


class Crab:
    def __init__(self, views=[], host="0.0.0.0", port=5000, print_requests=False):
        self.host = host
        self.port = port
        self.views = views

        class TCPHandler(socketserver.BaseRequestHandler):
            def handle(self):
                try:
                    http_request = self.http_request()
                    self.find(http_request.path, views)

                    if print_requests:
                        print(http_request)

                except IndexError:
                    self.send(html_response("404: Request Not Found", 404))
            
            def find(self, path, views, path_prefix=""):
                for view_type, regex_path, actor in views:
                    paths_match = re.match(path_prefix + regex_path, path)
                    paths_full_match = re.fullmatch(path_prefix + regex_path, path)

                    # Handles returns from regex paths
                    if paths_full_match and view_type == "path":
                        groups = paths_full_match.groups()
                        try:
                            result = actor(self, *groups)
                        except TypeError:
                            raise TypeError("path takes [str, Callable] as arguments")
                        if result:
                            self.request.sendall(result)
                        return path_prefix + regex_path

                    # Handles recursive call to deeper regex views
                    elif paths_match and view_type == "view":
                        if type(actor) != list:
                            raise TypeError("view takes [str, List] as arguments")
                        self.find(path, actor, path_prefix=path_prefix + regex_path)
                        return

                raise IndexError("view does not exist")
                    
            def request_bytes(self, count: int = DEFAULT_REQUEST_SIZE):
                return self.request.recv(count)

            def http_request(self):

                # check if \r\n\r\n is in request
                # if it isn't, keep requesting chunks

                request = self.request_bytes()
                new_request = request 
                header_refresh = 0
                while not re.search(b"\r\n\r\n", new_request, re.DOTALL) and header_refresh < MAX_HEADER_REFRESH:
                    new_request = self.request_bytes()
                    request += new_request
                    header_refresh += 1

                # Parse header and body
                # Convert to HTTPRequest object

                request_parsed = re.match(b"(.+)(\r\n\r\n)(.*)", request, re.DOTALL)

                if not request_parsed:
                    raise IndexError

                request_head, body = request_parsed.group(1), request_parsed.group(3)

                # parse headers
                request_head = request_head.split(b"\r\n")
                data, headers = request_head[0], request_head[1:]
                method, path, protocol = data.split(b" ")
                http_request = HTTPRequest(
                    method.decode(), 
                    path.decode(), 
                    protocol.decode(), 
                    headers, 
                    body
                )

                # Expand the rest of the body
                if http_request.body:
                    header_map = http_request.header_map()
                    content_length = header_map["Content-Length"]
                    body_length = len(http_request.body)

                    while body_length < content_length:
                        http_request.body += self.request_bytes(
                            min(content_length - body_length, DEFAULT_REQUEST_SIZE)
                        )

                return http_request
    
            def send(self, content: bytes):
                self.request.sendall(content)

        self.handler = TCPHandler

    def start(self):
        try:
            with socketserver.TCPServer((self.host, self.port), self.handler) as server:
                print(f"Hosted at http://{self.host}:{self.port}")
                server.serve_forever()
        except KeyboardInterrupt:
            print("exited")

