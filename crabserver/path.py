from typing import Callable, Any, Union, Optional
from socketserver import BaseRequestHandler

from crablib.http.types import Request, Response, Frame


class Path:
    def __init__(self, regex: str, view: Callable[[Any, Request], None]):
        self.regex = regex
        self.view = view
