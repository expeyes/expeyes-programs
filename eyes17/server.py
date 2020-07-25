"""
EYES17 for Young Engineers and Scientists
Python library to communicate by http-enabled sockets
Author  : Georges Khaznadar <georgesk@debian.org>
License : GNU GPL version 3
Started on 2020-07-25
"""

import http.server
import socketserver
from PyQt5.QtCore import QThread
from tempfile import NamedTemporaryFile
import os

INDEX = open("server.html").read()

class EYESRequestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        if "?" in self.requestline:
            # this is a request with parameters, let's parse them
            _, params = self.requestline.split("?")
            params = params.split("&")
            vars={}
            for p in params:
                k,v = p.split("=")
                vars[k] = v
            # params have been parsed into the vars dictionary
            message=""
            width=0
            if vars["format"] == "svg":
                message += "format SVG; "
            elif vars["format"] == "png":
                message += "format PNG; "
                try:
                    width = int(vars["width"])
                except:
                    width = 400 # the default width value
                message += f"width = {width}px; "
            else:
                message += "format UNKNOWN; "
            if vars["shot"].startswith("Full"):
                message += "full Eyes17 snapshot"
            else:
                message += "snapshot of the display only"
            # now, send the response
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(message.encode("utf-8"))
        else: # no parameters, just show the index webpage
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
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.socket.close()
    return

class ScreenShotThread(QThread):
    def __init__(self, parent, port = 45594):
        QThread.__init__(self, parent)
        self.port = port
        return

    def run(self):
        def classFactory(parent):
            """
            creates a closure class which embed the parent
            """
            class thisRequestHandler(http.server.BaseHTTPRequestHandler):

                def do_GET(self):
                    if "?" in self.requestline:
                        # this is a request with parameters, let's parse them
                        _, params = self.requestline.split("?")
                        params = params.split("&")
                        vars={}
                        for p in params:
                            k,v = p.split("=")
                            vars[k] = v
                        # params have been parsed into the vars dictionary
                        message=""
                        width=0
                        tmpFileName = ""
                        with NamedTemporaryFile(prefix="eyes17_") as tmp:
                            tmpFileName=tmp.name
                        # now tmp should be deleted, but the name
                        # tmpFileName is a valid name for a temporary file
                        if vars["format"] == "svg":
                            # should take a look at
                            if vars["shot"].startswith("Full"):
                                parent.screenshot(tmpFileName=tmpFileName)
                            else:
                                parent.screenshotPlot(tmpFileName=tmpFileName)
                            self.send_response(200)
                            self.send_header('Content-type','image/svg+xml')
                            self.end_headers()
                            self.wfile.write(open(tmpFileName,"rb").read())
                            os.unlink(tmpFileName)
                            return
                        elif vars["format"] == "png":
                            message += "format PNG; "
                            with open(tmpFileName,"w") as f: f.write("Sorry, PNG is not yet implemented : "+message+"\n")
                            try:
                                width = int(vars["width"])
                            except:
                                width = 400 # the default width value
                            message += f"width = {width}px; "
                        else:
                            message += "format UNKNOWN; "
                            with open(tmpFileName,"w") as f: f.write("Sorry, not yet implemented : "+message+"\n")
                        # now, send the response
                        self.send_response(200)
                        self.send_header('Content-type','text/html')
                        self.end_headers()
                        self.wfile.write(message.encode("utf-8")+b"<br/>"+open(tmpFileName,"rb").read())
                        os.unlink(tmpFileName)
                    else: # no parameters, just show the index webpage
                        self.send_response(200)
                        self.send_header('Content-type','text/html')
                        self.end_headers()
                        self.wfile.write(INDEX.encode("utf-8"))
                    return
            return thisRequestHandler
        
        requestHandler = classFactory(self.parent())
        with socketserver.TCPServer(("", self.port), requestHandler) as httpd:
            print("EYES17's schreenshot service, at port:", self.port)
            try:
                httpd.serve_forever()
            except Exception(err):
                print("Closing EYESRequestHandler, err =", err)
                httpd.socket.close()
        return
        
if __name__ == "__main__":
    runserver()
