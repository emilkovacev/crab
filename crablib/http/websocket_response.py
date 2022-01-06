from crablib.http.types import Frame


def text_response(body: str):
    body = body.encode()
    return Frame(True, False, False, False, 0x1, False, len(body), body)

def binary_response(body: bytes):
    return Frame(True, False, False, False, 0x2, False, len(body), body)

def pong(body: bytes):
    return Frame(True, False, False, False, 0xa, False, len(body), body)

def end_connection():
    return Frame(True, False, False, False, 0x8, False, 0)
