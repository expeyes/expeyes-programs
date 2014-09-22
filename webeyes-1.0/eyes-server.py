#!/usr/bin/python
# -*- coding: utf-8 -*-

import cherrypy, os, os.path, time, types
from commonHTML import head, foot
from widgets import menuADC
import expeyes.eyesj as ej
import eyesJr as ejr



class EyesServer:

    timeout=3 # no more than one self-check during this delay
    
    def __init__(self):
        """
        the constructor
        initializes a few internal variables
        """
        self.lastCheck=time.time()
        self.ok=False
        self.p=ej.open()
        if self.p:
            self.ok=True
        return

    def recheck(self):
        """
        checks that expeyes-Junior is still connected,
        after some delay at least
        """
        if time.time() < self.lastCheck + EyesServer.timeout:
            return
        if self.ok:
            try:
                v=self.p.get_voltage(0)
            except:
                self.ok=False
        if not self.ok:
            self.p=ej.open()
            if self.p:
                self.ok=True
        return

    @cherrypy.expose
    def index(self, **kw):
        # tries to reconnect expeyes-jr box if some issue has occurred
        self.recheck()
        # puts widgets in the body
        body="""\
  <form method="post" action="index">
    <div id="menuadc">{menuadc}</div>
  </form>
""".format(
            menuadc=menuADC(self,**kw),
            )
        # returns a well-formed HTML file, valid as XHTML-1.0 Strict
        return head.format(
            title="Expeyes-Jr web interface", 
            host="localhost") + \
            body +\
            foot.format(ok=self.ok)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def eyesJSON(self, **kw):
        """
        JSON service
        """
        # preconditions: "fun" must be in kw, it must be the name of a
        # function of the module ejr (eyesJr)
        if "fun" in kw:
            if kw["fun"] in dir(ejr):
                fun=getattr(ejr,kw["fun"])
                if type(fun)==types.FunctionType:
                    return fun(self, **kw)
        # in any other case:
        kw["error"]="Could not call the expected function (attribute 'fun') in the module eyesJr"
        return kw

if __name__=="__main__":
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd()),
            },
        '/inc': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './inc',
            },
        }
    cherrypy.quickstart(EyesServer(),'/', conf)
