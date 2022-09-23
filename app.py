from crablib import Crab, path, view, html_response, file_response # init_websocket
import sys

def home(handler):
    return html_response("<h1>Hey there!</h1>")

def pong(handler, year, month, day):
    return html_response(f"<h1>{month}/{day}/{year}</h1>")

def stars(handler):
    return file_response("dog.jpeg")

def starfield(handler):
    return file_response("space.jpg") 

viewsC = [
    path(r'/dog.jpg$', stars)
]

viewsB = [
    view(r'/pathB', viewsC)
]

views = [
    path(r'^/$', home),
    path(r'/(\d){4}-(\d){2}-(\d){2}', pong),
    view(r'/pathA', viewsB),
    path(r'/starfield', starfield)
]

if __name__ == "__main__":
    app = Crab(port=int(sys.argv[1]), views=views)
    app.start()
