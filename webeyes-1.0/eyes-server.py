#!/usr/bin/python
# -*- coding: utf-8 -*-

import cherrypy, os, os.path, time
from commonHTML import head, foot
from eyesWidgets import allADCwidget
import expeyes.eyesj as ej



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
    <div id="allADCwidget">{allADCwidget}</div>
  </form>
""".format(
            allADCwidget=allADCwidget(self,**kw),
            )
        # returns a well-formed HTML file, valid as XHTML-1.0 Strict
        return head.format(
            title="Expeyes-Jr web interface", 
            host="localhost") + \
            body +\
            foot.format(ok=self.ok)

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
