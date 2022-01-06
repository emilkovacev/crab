from collections.abc import MutableMapping
from typing import Dict


# opcode list
# 0x0:  continuation
# 0x1:  text
# 0x2:  binary/control codes
# 0x8:  connection close
# 0x9:  ping frame
# 0xa:  pong frame


class Frame:
    def __init__(self, fin: bool, rsv1: bool, rsv2: bool, rsv3: bool,
                 opcode: int, mask: bool, payload_len: int, data: bytes = None):
        self.fin = fin
        self.rsv1 = rsv1
        self.rsv2 = rsv2
        self.rsv3 = rsv3

        self.opcode = opcode
        self.mask = mask

        self.payload_len = payload_len
        self.data = data

    def write_raw(self):
        fin = (self.fin & 0x1) << 3
        rsv1 = (self.rsv1 & 0x1) << 2
        rsv2 = (self.rsv2 & 0x1) << 1
        rsv3 = (self.rsv3 & 0x1)
        opcode = self.opcode & 0xf

        byte_1 = (((fin | rsv1 | rsv2 | rsv3) << 4) | opcode).to_bytes(1, 'big')    # converts first 4 args into bytes

        mask = (self.mask & 0x1) << 7
        payload_len = self.payload_len
        extended_payload_len: bytes = b''

        if 126 < payload_len < (1 << 16):
            payload_len = 126
            extended_payload_len = (self.payload_len & ~(1 << 15)).to_bytes(2, 'big')

        elif payload_len > 1 << 16:
            payload_len = 127
            extended_payload_len = (self.payload_len & ~(1 << 63)).to_bytes(8, 'big')

        byte_2 = (mask | (payload_len & 0x7f)).to_bytes(1, 'big')
        frame = byte_1 + byte_2
        if extended_payload_len: frame += extended_payload_len
        if self.data: frame += self.data

        return frame

    def __str__(self):
        raw = self.write_raw()
        output = ''
        i = 1
        for b in raw:
            output += (format(b, '08b')) + ' '
            if i % 4 == 0: output += '\n'
            i += 1
        return output


# header storage class
class Headers(MutableMapping):
    def __init__(self):
        self.store = dict()

    def __len__(self):
        ...

    def __iter__(self):
        ...

    def __getitem__(self, key: str):
        if type(key) == str:
            return self.store[self._keytransform(key.lower())]
        else:
            raise ValueError

    def __setitem__(self, key: str, value):
        if type(key) == str:
            self.store[self._keytransform(key.lower())] = value
        else:
            raise ValueError

    def __delitem__(self, key: str):
        if type(key) == str:
            del self.store[self._keytransform(key.lower())]
        else:
            raise ValueError

    def __contains__(self, item):
        return type(item) == str and item in self.store.items()

    def _keytransform(self, key):
        return key.lower()

    def __str__(self):
        return str(self.store)


# singular header value
class Header:
    def __init__(self, name: str, value: str, options: Dict[str, str]):
        self.name: str = name
        self.value: str = value
        self.options: Dict[str, str] = options


class Cookie:
    def __init__(self, name: str, value: str, expires: str = None,
                 max_age: int = None, secure: bool = True, http_only: bool = True,
                 same_site: str = 'Strict', path: str = None):
        self.name: str = name
        self.value: str = value
        self.expires = expires
        self.max_age = str(max_age)
        self.secure = secure
        self.http_only = http_only
        self.path = path
        self.same_site = same_site

    def write(self) -> str:
        response: str = f'{self.name}={self.value}'
        if self.expires:
            response += f'; Expires={self.expires}'
        if self.max_age:
            response += f'; Max-Age={self.max_age}'
        if self.secure:
            response += f'; Secure'
        if self.http_only:
            response += f'; HttpOnly'
        if self.path:
            response += f'; Path={self.path}'
        if self.same_site:
            response += f'; SameSite={self.same_site}'
        return response

    def __str__(self) -> str:
        return self.write()


class Request:
    def __init__(self, request: bytes, request_type: str,
                 path: str, headers: Headers, http_version: str = 'HTTP/1.1',
                 cookies=None, body: bytes = b''):
        self.request = request
        self.request_type = request_type
        self.path = path
        self.http_version = http_version
        self.headers = headers
        self.body = body

        if cookies is None:
            cookies = []
        self.cookies: Dict[str, str] = cookies


class Response:
    def __init__(self, status_code: int, status_message: str, headers,
                 body: bytes = None, http_version: str = 'HTTP/1.1'):
        self.status_code = status_code
        self.status_message = status_message
        self.headers = headers
        self.body = body
        self.http_version = http_version
        self.cookies: Dict[str, Cookie] = {}

    def write_raw(self) -> bytes:
        response: bytes = f'{self.http_version} {self.status_code} {self.status_message}\r\n'.encode()
        for (key, value) in self.headers.items():
            response += f'{key}: {str(value)}\r\n'.encode()

        for cookie in self.cookies.values():
            response += f'Set-Cookie: {cookie.write()}\r\n'.encode()

        response += b'\r\n'

        if self.body:
            response += self.body

        return response

    def add_cookie(self, cookie: Cookie):
        self.cookies[cookie.name] = cookie
