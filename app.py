from crab import Crab, path
from builtin import html_response

views = [
    path(r'^/$', lambda _: html_response("<h1>Hey there!</h1>")),
    path(r'^/(.*)$', lambda response, endpoint: html_response(f"<h1>{endpoint}</h1>"))
]

app = Crab(port=7999, views=views)
app.start()
