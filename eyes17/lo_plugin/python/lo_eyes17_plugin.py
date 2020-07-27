"""
EYES17 for Young Engineers and Scientists
Python library to communicate by http-enabled sockets
Author  : Georges Khaznadar <georgesk@debian.org>
License : GNU GPL version 3
Started on 2020-07-25
"""

import unohelper, uno
import traceback
import http.client
from com.sun.star.beans import PropertyValue
from com.sun.star.awt import Size
from com.sun.star.text.ControlCharacter import PARAGRAPH_BREAK
from com.sun.star.task import XJobExecutor

class EYES17 (unohelper.Base, XJobExecutor):
    def __init__(self, ctx):
        self.ctx = ctx
        self.smgr = ctx.getServiceManager()
        return
    
    def trigger(self, arg):
        try:
            if arg == "full":
                self.fullSVGscreenShot()
            else:
                self.smallSVGscreenShot()
        except:
            traceback.print_exc()
        return
    
    def fullSVGscreenShot(self):
        """
        Take and paste a full screenshot from Eyes17
        """
        return self.screenshotFromEyes17()

    def smallSVGscreenShot(self):
        """
        Take and paste a screenshot of "just the display part", from Eyes17
        """
        return self.screenshotFromEyes17(shot="")

    def screenshotFromEyes17(
            self,
            host = "localhost",
            port = 45594,
            the_format = "svg",
            shot = "full",
            width = "",
            height = "",
            paraadjust = ""
    ):
        """
        Communicate with ExpEYES17 through a socket to request a screenshot,
        then pastes it into the Tex document.

        :param host: an IP address, "localhost" by default
        :param port: a port for the socket, 45594 by default
        :param the_format: format for the screen shot, "svg" by default
        :param shot: this parameter decides whether on wants a full scrren shot
          or a screen shot containing the display of Eyes17; defaults to "full"
        :param width: might be used later
        :param height: might be used later
        :param paraadjust: might be used later
        """
        url = f"/?format={the_format}&shot={shot}&width={width}&height={height}&paraadjust={paraadjust}"
        return self.queryImageAndPaste(host, port, url, width, height, paraadjust)

    def queryImageAndPaste(self, host, port, url, width, height, paraadjust):
        """
        Query an image trough a socket, then pastes it into the Text document

        :param host: an IP address, "localhost" by default
        :param port: a port for the socket, 45594 by default
        :param url: a well-formed url, to GET a response containing an
          image in SVG format (maybe later, also PNG?)
        :param width: might be used later
        :param height: might be used later
        :param paraadjust: might be used later
        """
        #msg = dir(self.smgr)
        #raise Exception(msg)
        ctx =  self.smgr.DefaultContext
        doc = ctx.getDesktop().getCurrentComponent()
        cursor = doc.getCurrentController().getViewCursor().getEnd()
        if hasattr( doc, "Text" ):
            undoManager = doc.getUndoManager()
            undoManager.enterUndoContext("Insert screenshot from Eyes17")

            # do the work here
            ctx = uno.getComponentContext()
            graphicprovider = ctx.ServiceManager.createInstance(
                "com.sun.star.graphic.GraphicProvider")
            istream = ctx.ServiceManager.createInstanceWithContext(
                "com.sun.star.io.SequenceInputStream", ctx)
            conn = http.client.HTTPConnection(host,port)
            try:
                conn.request("GET", url)
            except:
                doc.Text.insertString(
                    cursor, f"Could not connect to {host}:{port}", 0)
                doc.Text.insertControlCharacter(cursor, PARAGRAPH_BREAK, 0)
                return            
            r1 = conn.getresponse()
            if r1.reason != "OK":
                doc.Text.insertString(
                    cursor,
                    f"Could not get http://{host}:{port}. Error: {r1.status} {r1.reason}", 0)
                doc.Text.insertControlCharacter(cursor, PARAGRAPH_BREAK, 0)
                return
            fbytes=r1.read()
            istream.initialize((uno.ByteSequence(fbytes),))
            graphic = graphicprovider.queryGraphic((PropertyValue(
                'InputStream', 0, istream, 0), ))
            if graphic.SizePixel is None:
                # Then we're likely dealing with vector graphics. Then we try to
                # get the "real" size, which is enough information to
                # determine the aspect ratio
                original_size = graphic.Size100thMM
            else:
                original_size = graphic.SizePixel
            graphic_object_shape = doc.createInstance(
                'com.sun.star.drawing.GraphicObjectShape')
            graphic_object_shape.Graphic = graphic

            size = self.adjustSize(original_size, width=width, height=height)
            graphic_object_shape.setSize(size)
            thisgraphicobject = doc.createInstance("com.sun.star.text.TextGraphicObject")
            thisgraphicobject.Graphic = graphic_object_shape.Graphic
            thisgraphicobject.setSize(size)

            ## for future enhancements: take in account paraadjust ##
            if paraadjust:                                         ##
                oldparaadjust = cursor.ParaAdjust                  ##
                cursor.ParaAdjust = paraadjust                     ##
            #########################################################

            doc.Text.insertTextContent(cursor, thisgraphicobject, False)
            doc.Text.insertControlCharacter(cursor, PARAGRAPH_BREAK, 0)

            ## for future enhancements: take in account paraadjust ##
            if paraadjust:                                         ##
                cursor.ParaAdjust = oldparaadjust                  ##
            #########################################################

            undoManager.leaveUndoContext()
        return

    def adjustSize(self, size, dpi=150, width="", height=""):
        """
        Adjust the size of an image to fit the TextDocument
        :param size: the image's native size
        :param dpi: dots per inch, defaults to 150 dpi
        :param width: maybe used in future enhancements
        :param height: maybe used in future enhancements
        :return: a Size object for the Text document
        """
        scale = 1000 * 2.54 / dpi
        w = int(size.Width * scale)
        h = int(size.Height * scale)

        ## for future enhancements: take in account width and height ##
        if width and height:                                         ##
            w = int(float(width) * scale)                            ##
            h = int(float(height) * scale)                           ##
        elif width:                                                  ##
            w = int(float(width) * scale)                            ##
            h = int(w / size.Width * size.Height)                    ##
        elif height:                                                 ##
            h = int(float(height) * scale)                           ##
            w = int(h / size.Height * size.Width)                    ##
        ###############################################################

        return Size(w,h)

g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(
    EYES17,
    'org.example.EYES17',
    ())


