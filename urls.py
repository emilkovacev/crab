from crabserver.path import Path
from views import builtin, index

urls = [
    Path('^/$', index.home),
    Path('^/websocket$', index.websocket),

    # default paths
    Path('^(html/[^.]+.html)$', builtin.html),
    Path('^/(images/[^.]+.(jpg|jpeg))$', builtin.img),
    Path('^/(css/[^.]+.css)$', builtin.css),
    Path('^/(js/[^.]+.js)$', builtin.js),
]
