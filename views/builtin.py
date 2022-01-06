from crablib.fileIO import read_file, read_template
from crablib.http.parse import Request
from crablib.http.response import InvalidRequest
from crablib.http.response import http_200


def html(socket, request: Request):
    root = 'html'
    path = request.path.split(f'/{root}/')[1]
    if request.request_type == 'GET':
        response = http_200('text/html', read_file(f'{root}/{path}'), 'utf-8')
        return socket.sendall(response)
    else:
        raise InvalidRequest


# text/css
def css(socket, request: Request):
    root = 'css'
    path = request.path.split(f'/{root}/')[1]
    if request.request_type == 'GET':
        response = http_200('text/css', read_file(f'{root}/{path}'), 'utf-8')
        socket.sendall(response)

    else:
        raise InvalidRequest


# script/js
def js(socket, request: Request):
    root = 'js'
    path = request.path.split(f'/{root}/')[1]
    if request.request_type == 'GET':
        response = http_200('text/javascript', read_file(f'{root}/{path}'))
        socket.sendall(response)

    else:
        raise InvalidRequest


# image/jpg
def img(socket, request: Request):
    if request.request_type == 'GET':
        response = http_200(
            content_type='image/jpeg',
            content=read_file(request.path.lstrip('/'))
        ).write_raw()

        socket.request.sendall(response)

    else:
        raise InvalidRequest
