from .http_objects import HTTPRequest
import re


def handle_header_buffer(handler, request):
    new_request = request

    # check if \r\n\r\n is in request
    # if it isn't, keep requesting chunks

    while not re.search(b"\r\n\r\n", new_request, re.DOTALL):
        new_request = handler.request_bytes()
        request += new_request

    return request


def parse_http_object(request):
    request_parsed = re.match(b"(.+)(?=\r\n\r\n)(.+)", request, re.DOTALL)
    assert request_parsed
    request_head, body = request_parsed.group(1), request_parsed.group(3)

    # parse headers
    data, headers = request_head.split(b"\r\n", maxsplit=1)
    method, path, protocol = data.split(b" ")
    return HTTPRequest(method.decode(), path.decode(), protocol.decode(), headers, body)


def handle_body_buffer(handler, request):
    pass


def get_http_request(handler):
    request = handle_header_buffer(handler)    


def parse_websocket_frame(request: bytes):
    pass
