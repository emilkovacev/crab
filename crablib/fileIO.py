import re
from os import path as ospath

from crabengine.generate import generate_html


def read_file(path: str) -> bytes:
    path = ospath.relpath(path)
    with open(path, 'rb') as f:
        return f.read()

def read_template(path: str, args=None) -> bytes:
    path = ospath.relpath(path)
    if not args:
        args = {}

    with open(path, 'r') as f:
        return generate_html(f.read(), args).encode()
