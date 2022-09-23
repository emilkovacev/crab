HTTP_RESPONSE_CODES = {
    100: "Continue",
    101: "Switching Protocols",
    103: "Early Hints",

    200: "OK",
    201: "Created",
    202: "Accepted",
    203: "Non-Authoritative Information",
    204: "No Content",
    205: "Reset Content",
    206: "Partial Content",

    300: "Multiple Choices",
    301: "Moved Permanently",
    302: "Found",
    303: "See Other",
    304: "Not Modified",
    307: "Temporary Redirect",
    308: "Permanent Redirect",

    400: "Bad Request",
    401: "Unauthorized",
    402: "Payment Required",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    406: "Not Acceptable",
    407: "Proxy Authentication Required",
    408: "Request Timeout",
    409: "Conflict",
    410: "Gone",
    411: "Length Required",
    412: "Precondition Failed",
    413: "Payload Too Large",
    414: "URI Too Long",
    415: "Unsupported Media Type",
    416: "Range Not Specified",
    417: "Expectation Failed",
    418: "I'm a teapot",
    422: "Unprocessable Entry",
    426: "Upgrade Required",
    428: "Precondition Required",
    429: "Too Many Requests",
    431: "Request Header Fields Too Large",
    451: "Unavailable For Legal Reasons",
    
    500: "Internal Server Error",
    501: "Not Implemented",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
    505: "HTTP Version Not Supported",
    506: "Variant Also Negotiates",
    510: "Not Extended",
    511: "Network Authentication Required"
}

MIME_TYPES = {
    ".txt": "text/plain",
    ".html": "text/html",
    ".jpg": "image/jpeg",
    ".png": "image/png",
    ".pdf": "application/pdf"
}


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
        return f"{self.protocol} {self.status_code} {self.status_message}"

