from crablib.server import startserver


def error(e: Exception) -> bytes:
    return b'Error 404!'


startserver('0.0.0.0', 7998, error)
