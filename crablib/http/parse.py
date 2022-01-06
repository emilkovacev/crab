import re
from typing import Dict, List

from crablib.http.types import Headers, Header, Request, Cookie, Frame


def parse_request(request: bytes) -> Request:
    i = re.match(b'^.+?(?=\r\n\r\n)', request, re.DOTALL).end()

    if i is None:
        raise ValueError

    header: str = request[:i].decode()
    lines = header.split('\r\n')

    first_line = lines[0].split(' ')
    request_type, path = first_line[0], first_line[1]
    headers = lines[1:]

    parsed_headers: Headers = Headers()
    for h in headers:
        parts = re.split(':\\s*', h)
        parsed_headers[parts[0]] = parts[1]

    body: bytes = b''
    if 'Content-Length' in parsed_headers:
        body = request[i + 4: i + 4 + int(parsed_headers['Content-Length'])]

    cookies = {}
    if 'Cookie' in parsed_headers:
        parts = re.split('; ', parsed_headers['Cookie'])
        for cookie in parts:
            sections = cookie.split('=')
            cookies[sections[0]] = sections[1]

    return Request(
        request=request,
        request_type=request_type,
        path=path,
        headers=parsed_headers,
        body=body,
        cookies=cookies
    )


def parse_header(s: str) -> Header:
    values = re.split('[;:]\\s*', s)
    name: str = values[0]
    value: str = values[1]

    options = {}
    if len(values) >= 3:
        for option in values[2:]:
            desc = re.match('(?P<opt>.+)="(?P<value>.*)"', option)
            opt, opt_value = desc.groupdict()['opt'], desc.groupdict()['value']
            options[opt] = opt_value

    return Header(name=name, value=value, options=options)


def parse_cookie(cookie: str) -> Dict[str, Cookie]:
    cookie_list = re.split(': ', cookie)
    retval: Dict[str, Cookie] = {}
    for c in cookie_list:
        c_headers = c.split('=')
        retval[c_headers[0]] = Cookie(
            name=c_headers[0],
            value=c_headers[1]
        )
    return retval


def parse_form(request: Request) -> Dict[str, bytes]:
    boundary: str = '--' + re.search('boundary=(?P<boundary>.+);?', request.headers['Content-Type']).group(1)
    content_chunks: List[bytes] = request.body.split(boundary.encode())[1:-1]

    retval: Dict[str, bytes] = {}
    content: bytes
    for content in content_chunks:
        parsed_content: List[bytes] = content.strip(b'\r\n').split(b'\r\n\r\n')
        headers: List[str] = parsed_content[0].decode().split('\r\n')
        body: bytes = b''
        if len(parsed_content) == 2:
            body = parsed_content[1]

        headers_dict: Dict[str, Header] = {}
        header: str
        for header in headers:
            headerobj: Header = parse_header(header)
            headers_dict[headerobj.name] = headerobj
            content_name: str = headers_dict['Content-Disposition'].options['name']
            retval[content_name] = body
    return retval


def unmask(chunk: bytes, masking_key: bytes) -> bytes:
    i = 0
    retval = b''
    for b in chunk:
        if i > 3: i = 0
        retval += (b ^ masking_key[i]).to_bytes(1, 'little')
        i += 1
    return retval


def bytes_to_int(byt: bytes) -> int:
    retval = 0
    for i in range(len(byt)):
        pw = 2 * (len(byt) - i - 1)
        retval += byt[i] * (16 ** pw)
    return retval


def parse_frame(frame: bytes) -> Frame:
    PAYLOAD_SB = 2
    MASK_SB = 2
    payload_len: int = frame[1] & 0x7f

    if payload_len == 126:
        payload_len = bytes_to_int(frame[2:4])
        PAYLOAD_SB = MASK_SB = 4

    payload: bytes = b''
    MASK = (frame[1] & 0x80) >> 7
    if MASK:
        PAYLOAD_SB += 4
        masking_key = bytes(x for x in frame[MASK_SB:MASK_SB + 4])
        payload += unmask(frame[PAYLOAD_SB:], masking_key)

    else:
        payload = frame[PAYLOAD_SB:]

    parsed_frame = Frame(
        fin=(frame[0] & 0x80) >> 7,
        rsv1=(frame[0] & 0x40) >> 6,
        rsv2=(frame[0] & 0x20) >> 5,
        rsv3=(frame[0] & 0x10) >> 4,

        opcode=frame[0] & 0x0f,

        payload_len=payload_len,
        data=payload
    )
    return parsed_frame
