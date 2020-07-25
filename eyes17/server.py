"""
EYES17 for Young Engineers and Scientists
Python library to communicate by http-enabled sockets
Author  : Georges Khaznadar <georgesk@debian.org>
License : GNU GPL version 3
Started on 2020-07-25
"""

import http.server
import socketserver

INDEX = open("index.html").read()

class EYESRequestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(INDEX.encode("utf-8"))
        return

def runserver(PORT = 45594):
    """
    Runs a http service on PORT 45594 by default
    """
    with socketserver.TCPServer(("", PORT), EYESRequestHandler) as httpd:
        print("EYES17's schreenshot service, at port:", PORT)
        httpd.serve_forever()

if __name__ == "__main__":
    runserver()
