"""
EYES17 for Young Engineers and Scientists
Python library to communicate by http-enabled sockets
Author  : Georges Khaznadar <georgesk@debian.org>
License : GNU GPL version 3
Started on 2020-07-25
"""

import unohelper, uno
import http.client
from com.sun.star.beans import PropertyValue
from com.sun.star.awt import Size
from com.sun.star.text.ControlCharacter import PARAGRAPH_BREAK

def svgFromEyes17():
    desktop = XSCRIPTCONTEXT.getDesktop()
    doc = desktop.getCurrentComponent()
    controller = doc.getCurrentController()
    view_cursor = controller.getViewCursor()
    cursor = view_cursor.getEnd()
    if hasattr( doc, "Text" ):
        drawPage = doc.getDrawPage()

        undoManager = doc.getUndoManager()
        undoManager.enterUndoContext( "Insert screenshot from Eyes17" )

        # do the work here
        ctx = uno.getComponentContext()
        smgr = ctx.getServiceManager()
        graphicprovider = smgr.createInstance("com.sun.star.graphic.GraphicProvider")
        
        dpi = 150
        
        # those might become parameters:
        width = None
        height = None
        paraadjust = None
        host = "localhost"
        port = 45594
        
        scale = 1000 * 2.54 / dpi
        istream = ctx.ServiceManager.createInstanceWithContext("com.sun.star.io.SequenceInputStream", ctx)
        fbytes=b''
        conn = http.client.HTTPConnection(host,port)
        try:
            conn.request("GET", "/?format=svg")
        except:
            doc.Text.insertString(cursor, f"Could not connect to {host}:{port}", 0)
            doc.Text.insertControlCharacter(cursor, PARAGRAPH_BREAK, 0)
            return            
        r1 = conn.getresponse()
        if r1.reason != "OK":
            doc.Text.insertString(cursor, f"Could not get http://{host}:{port}. Error: {r1.status} {r1.reason}", 0)
            doc.Text.insertControlCharacter(cursor, PARAGRAPH_BREAK, 0)
            return
        fbytes=r1.read()
        istream.initialize((uno.ByteSequence(fbytes),))
        graphic = graphicprovider.queryGraphic((PropertyValue('InputStream', 0, istream, 0), ))
        if graphic.SizePixel is None:
            # Then we're likely dealing with vector graphics. Then we try to
            # get the "real" size, which is enough information to
            # determine the aspect ratio
            original_size = graphic.Size100thMM
        else:
            original_size = graphic.SizePixel
        graphic_object_shape = doc.createInstance('com.sun.star.drawing.GraphicObjectShape')
        graphic_object_shape.Graphic = graphic
        if width and height:
            size = Size(int(width * scale), int(height * scale))
        elif width:
            size = Size(int(width * scale), int((float(width)/original_size.Width) * original_size.Height * scale))
        elif height:
            size = Size(int((float(height)/original_size.Height) * original_size.Width * scale), int(height * scale))
        else:
            size = Size(int(original_size.Width * scale), original_size.Height * scale)
        graphic_object_shape.setSize(size)
        thisgraphicobject = doc.createInstance("com.sun.star.text.TextGraphicObject")
        thisgraphicobject.Graphic = graphic_object_shape.Graphic
        thisgraphicobject.setSize(size)
        if paraadjust:
            oldparaadjust = cursor.ParaAdjust
            cursor.ParaAdjust = paraadjust
        doc.Text.insertTextContent(cursor, thisgraphicobject, False)
        doc.Text.insertControlCharacter(cursor, PARAGRAPH_BREAK, 0)
        if paraadjust:
            cursor.ParaAdjust = oldparaadjust
        
        undoManager.leaveUndoContext()


        
