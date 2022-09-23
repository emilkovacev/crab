from .http_objects import HTTPResponse, HTTP_RESPONSE_CODES, MIME_TYPES
import re

PROTOCOL = "HTTP/1.1"
DEFAULT_STATUS_CODE = 200


def get_mime(path: str):
    ext = re.search(r"([\.].+$)", path)

    if ext is None:
        raise ValueError("No Mimetype")

    return MIME_TYPES.get(ext.group(1), "text/plain")

def path(regex_path: str, func):
    return 'path', regex_path, func

def view(regex_path: str, view):
    return 'view', regex_path, view

def text_response(body: str, status: int = DEFAULT_STATUS_CODE):
    base_response = HTTPResponse(
        PROTOCOL, 
        status, 
        HTTP_RESPONSE_CODES[status]
    )
    base_response.add_body(body.encode())
    return base_response

def plain_response(body: str, status: int = DEFAULT_STATUS_CODE):
    base_response = text_response(body, status)
    base_response.add_header("Content-Type", "text/plain")
    return base_response.stringify()

def html_response(body: str, status: int = DEFAULT_STATUS_CODE):
    base_response = text_response(body, status)
    base_response.add_header("Content-Type", "text/html")
    return base_response.stringify()

def file_response(filename: str, status: int = DEFAULT_STATUS_CODE):
    with open(filename, "rb") as f:
        file: bytes = f.read()
   
    response = HTTPResponse(
        PROTOCOL, 
        status, 
        HTTP_RESPONSE_CODES[status]
    )

    response.add_body(file)
    response.add_header("Content-Type", get_mime(filename))
    return response.stringify()

class WSConn:
    def __init__(self, handler):
        self.handler = handler

    def send_http(self, content: bytes):
        self.handler.send(content)

    def request_bytes(self):
        return self.handler.request_bytes

    def __enter__(self):
        pass

    def __exit__(self):
        pass
