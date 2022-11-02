import http.server
import socket
import sys
import time
import multiprocessing
import base64
import random


def get_best_family(*address):
    infos = socket.getaddrinfo(
        *address,
        type=socket.SOCK_STREAM,
        flags=socket.AI_PASSIVE,
    )
    family, type, proto, canonname, sockaddr = next(iter(infos))
    return family, sockaddr


def run_server(httpd):
    host, port = httpd.socket.getsockname()[:2]
    url_host = f'[{host}]' if ':' in host else host
    print(
        f"Serving HTTP on {host} port {port} "
        f"(http://{url_host}:{port}/) ..."
    )
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received, exiting.")
        sys.exit(0)


"""
A template webpage that polls the server for updates every second.
It will display the image returned by the server, and will refresh the page if a new image is available.
"""
template = """
    <html lang="en">
        <head>
            <title>Remote Plot</title>
            <script>
            async function fetchWithTimeout(resource, options = {{}}) {{
                const {{ timeout = 3000 }} = options;
                
                const controller = new AbortController();
                const id = setTimeout(() => controller.abort(), timeout);
                const response = await fetch(resource, {{
                    ...options,
                    signal: controller.signal  
                }});
                clearTimeout(id);
                return response;
            }}
            const pollInterval = {};
            const poll = () => {{
                fetchWithTimeout('/poll?token={}', {{timeout: 3000}}).then((response) => {{
                    if (response.status == 200) {{
                        setTimeout(poll, pollInterval);
                    }} else {{
                        window.location.reload(1);
                    }}
                }}).catch(() => {{
                    console.log("Error polling server");
                    setTimeout(poll, pollInterval);
                }});
            }}
            setTimeout(poll, pollInterval);
            </script>
        </head>
        <body>
            <img src="data:image/png;base64,{}">
        </body>
    </html>
"""

class ImageHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"

    def do_GET(self):
        poll_interval = 100
        if self.path.startswith('/poll'):
            # get token query param
            token = int(self.path.split('?token=')[1])
            if token == self.server.SHARED['token']:
                self.send_response(200)
            else:
                self.send_response(205)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"success")
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            token = self.server.SHARED['token']
            src = base64.b64encode(self.server.SHARED['image']).decode('utf-8')
            message = template.format(poll_interval, token, src)
            self.wfile.write(message.encode('utf-8'))

    def do_POST(self):
        self.server.SHARED['image'] = self.rfile.read(int(self.headers["Content-Length"]))
        self.server.SHARED['token'] = random.randint(0, 1000000)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"success")

    def log_message(self, format, *args):
        return


class SharedDataServer(http.server.ThreadingHTTPServer):
    manager = multiprocessing.Manager()
    SHARED = manager.dict()


