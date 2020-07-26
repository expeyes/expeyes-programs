"""
EYES17 for Young Engineers and Scientists
Python library to communicate by http-enabled sockets
Author  : Georges Khaznadar <georgesk@debian.org>
License : GNU GPL version 3
Started on 2020-07-25
"""

import uno
from com.sun.star.awt import Size, Point

def add5Graphics():
    oDesktop = XSCRIPTCONTEXT.getDesktop()
    oDoc = oDesktop.getCurrentComponent()
    if hasattr( oDoc, "Text" ):
        oDrawPage = oDoc.getDrawPage()

        oUndoManager = oDoc.getUndoManager()
        oUndoManager.enterUndoContext( "Add Five Graphic Objects" )

        from com.sun.star.awt import Size
        from com.sun.star.awt import Point

        for i in range(5):
            oGraphic = oDoc.createInstance( "com.sun.star.drawing.GraphicObjectShape" )
            oGraphic.setSize( Size(3000,2000) )
            oGraphic.setPosition( Point( i*3000, 1000 ) )
            oDrawPage.add( oGraphic )

        oUndoManager.leaveUndoContext()
        
