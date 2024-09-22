from http.server import HTTPServer, BaseHTTPRequestHandler
# from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
import threading
import time


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path == "/sleep":
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

            self.wfile.write(bytes("start... thread %s\n" % (threading.currentThread().getName()), "utf8"))
            time.sleep(8.0)
            self.wfile.write(bytes("after sleeping 8 seconds\n", "utf8"))
            return



        self.send_response(200)
        self.end_headers()
        message = threading.currentThread().getName()
        self.wfile.write(bytes(message, "utf8"))
        self.wfile.write(bytes('\n', "utf8"))
        return



if __name__ == '__main__':
    server = ThreadedHTTPServer(('', 80), Handler)
    print('Starting server, use <Ctrl-C> to stop')
    server.serve_forever()
