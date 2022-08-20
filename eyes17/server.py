"""
EYES17 for Young Engineers and Scientists
Python library to communicate screenshots through sockets, with HTTP
Author  : Georges Khaznadar <georgesk@debian.org>
License : GNU GPL version 3
Started on 2020-07-25
"""

import http.server
import socketserver
from PyQt5.QtCore import QThread
from tempfile import NamedTemporaryFile
import os
from datetime import datetime

this_dir = os.path.dirname(__file__)
INDEX = open(os.path.join(this_dir,"server.html")).read()
WPAGE = open(os.path.join(this_dir,"server.webpage.html")).read()

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
                        if vars.get("mode", "").startswith("webpage"):
                            # return a web page rather raw image data
                            self.send_response(200)
                            self.send_header('Content-type','text/html')
                            self.end_headers()
                            parameters = "&".join([f"{k}={v}" for k, v in vars.items() if "mode" not in k])
                            date = datetime.now().strftime("%Y-%M-%d -- %H:%M:%S")
                            wpage = WPAGE.format(src="/?"+parameters, date=date)
                            self.wfile.write(wpage.encode("utf-8"))
                        else:
                            message=""
                            width=0
                            tmpFileName = ""
                            with NamedTemporaryFile(prefix="eyes17_") as tmp:
                                tmpFileName=tmp.name
                            # now tmp is already deleted, but the name
                            # tmpFileName is a valid name for a temporary file
                            if vars.get("format","").lower().startswith("svg"):
                                # should take a look at
                                if vars.get("shot","").lower().startswith("full"):
                                    parent.screenshot(tmpFileName=tmpFileName)
                                else:
                                    parent.screenshotPlot(tmpFileName=tmpFileName)
                                self.send_response(200)
                                self.send_header('Content-type','image/svg+xml')
                                self.end_headers()
                                self.wfile.write(open(tmpFileName,"rb").read())
                                os.unlink(tmpFileName)
                                return
                            elif vars.get("format","").lower().startswith("png"):
                                message += "format PNG; "
                                with open(tmpFileName,"w") as f: f.write("Sorry, PNG is not yet implemented : "+message+"\n")
                                try:
                                    width = int(vars["width"])
                                except:
                                    width = 400 # the default width value
                                message += f"width = {width}px; "
                            else:
                                message += "format UNKNOWN; "
                                with open(tmpFileName,"w") as f: f.write("Sorry, not yet implemented : "+message+" "+repr(vars)+"\n")
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
        self.httpd = socketserver.TCPServer(("", self.port), requestHandler)
        print("EYES17's schreenshot service, at port:", self.port)
        try:
            self.httpd.serve_forever()
        except Exception(err):
            print("Closing EYESRequestHandler, error =", err)
            self.httpd.socket.close()
        return

    def terminate(self):
        if hasattr(self, "httpd"):
            self.httpd.socket.close()
        super().terminate()
        return
