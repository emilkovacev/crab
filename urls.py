from crablib.http.path import Path
from views import index

urls = [
    Path('^/$', index.index),

    # default paths
    Path('^/(images/[^.]+.(jpg|jpeg))$', index.img),
    Path('^/(style/[^.]+.css)$', index.css),
    Path('^/(script/[^.]+.js)$', index.js),
]
