class HttpError(Exception):
    """Base HTTP Error"""
    def __init__(self, status_code: int):
        self.status_code = status_code
