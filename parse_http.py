from http_objects import HTTPRequest

def parse_http_request(request: bytes):
    request_data, body = request.split(b"\r\n\r\n") 
    data, headers = request_data.split(b"\r\n", maxsplit=1)
    method, path, protocol = data.split(b" ")
    return HTTPRequest(method.decode(), path.decode(), protocol.decode(), headers, body)

