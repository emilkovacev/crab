def map_headers(header_list: list[bytes]):
    headers = {}
    for header in header_list:
        split_header = header.split(b": ", maxsplit=1)
        headers[split_header[0]] = split_header[1]

    return headers

class HTTPRequest:
    def __init__(self, method, path, protocol, headers=[], body=b''):
        self.method = method
        self.path = path
        self.protocol = protocol
        self.headers = headers
        self.body = body

    def stringify(self):
        request_data = f"{self.method} {self.path} {self.protocol}\n".encode()
        headers = ("\n".join(self.headers)).encode()
        retval = request_data + headers

        if self.body:
            retval += b'\n\n' + self.body

        return retval

    def header_map(self):
        return map_headers(self.headers)

    def add_header(self, key, value):
        self.headers.append(f"{key}: {value}")

    def add_body(self, body: bytes):
        self.body = body
        self.add_header("Content-Length", len(body))

    def __str__(self):
        return f"{self.method} {self.path} {self.protocol}"


class HTTPResponse:
    def __init__(self, protocol, status_code, status_message):
        self.protocol = protocol
        self.status_code = status_code
        self.status_message = status_message
        self.headers = []
        self.body = b''

    def stringify(self):
        response_data = f"{self.protocol} {self.status_code} {self.status_message}\n".encode()
        headers = ("\n".join(self.headers)).encode()
        retval = response_data + headers

        if self.body:
            retval += b'\n\n' + self.body

        return retval

    def header_map(self):
        return map_headers(self.headers)

    def add_header(self, key, value):
        self.headers.append(f"{key}: {value}")

    def add_body(self, body: bytes):
        self.body = body
        self.add_header("Content-Length", len(body))

    def __str__(self):
        return f"<{self.protocol} {self.status_code} {self.status_message}>"

