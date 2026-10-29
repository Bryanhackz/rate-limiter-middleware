from security.headers import get_security_headers
from handlers import pages, static

def application(environ: dict, start_response: callable) -> list[bytes]:
    path = environ.get("PATH_INFO", "/")
    
    if path == "/":
        status, content_type, body = pages.render_index()
    else:
        static_result = static.serve_static(path)
        if static_result:
            status, content_type, body = static_result
        else:
            status, content_type, body = pages.not_found()

    headers = [("Content-Type", content_type)]
    for h, v in get_security_headers().items():
        headers.append((h, v))

    body_bytes = body.encode("utf-8") if isinstance(body, str) else body
    start_response(status, headers)
    return [body_bytes]