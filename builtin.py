from http_objects import HTTPResponse

PROTOCOL = "HTTP/1.1"
STATUS_CODE = 200
STATUS_MESSAGE = "SUCCESSFUL REQUEST"
MIME = "text/plain"

def text_response(body: str):
    base_response = HTTPResponse(
        PROTOCOL, 
        STATUS_CODE, 
        STATUS_MESSAGE
    )
    base_response.add_body(body.encode())
    return base_response

def plain_response(body: str):
    base_response = text_response(body)
    base_response.add_header("Content-Type", "text/plain")
    return base_response.stringify()

def html_response(body: str):
    base_response = text_response(body)
    base_response.add_header("Content-Type", "text/html")
    return base_response.stringify()
