'''
Plotting libray, using Qt4 for expEYES
Author  : Georges Khaznadar <georgesk@debian.org>
Based on Ajith Kumar's work
License : GNU GPL version 3
'''

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import time

class axisWidget(QGraphicsView):
    def __init__(self, parent=None, min = -5.0, max = 5.0, label = ''):
        """
        constructor
        @param parent the parent widget
        @param min minimum value
        @param max maximum value
        @param labels text to display as a label
        """
        QGraphicsView.__init__(self, parent)
        self.parent = parent
        self.min=min
        self.max=max
        self.label = label
        self.axis=[]
        self.labelFont=QFont("Courier New")
        self.labelFont.setPixelSize(11)
        self.textPen = QPen(Qt.blue)
        self.labelPen = QPen(Qt.black)
        self.numdiv = 5
        self.t=None # a dummy text to enforce redrawing

    def direction(self):
        """
        @return either 'horizontal' or 'vertical'
        """
        if not self.scene():
            return None
        if self.scene().sceneRect().width() > self.scene().sceneRect().height():
            return 'horizontal'
        else:
            return 'vertical'
    
    def setGeometry(self, rect):
        """
        redefinition of the default setGeometry
        @param rect a QRect
        """
        QGraphicsView.setGeometry(self, rect)
        scene = QGraphicsScene(QRectF(rect), self.parent)
        w, h = rect.width(), rect.height()
        margin = 4
        w-=margin
        h-=margin
        scene.setSceneRect(QRectF(0,0,w,h))
        self.setScene(scene)
        self.drawAxis()

    def setRange(self, min, max, label=''):
        """
        set a new range and label
        @param min minimum value
        @param max maximum value
        @param label a short text
        """
        self.min=min
        self.max=max
        self.label=label
        self.drawAxis()

    def drawAxis(self):
        """
        draws the axis
        """
        self.axis=[]
        if self.direction() == 'horizontal':
            pos=QPoint(0.9*self.width(), 1)
            self.axis.append((self.textPen, pos, self.labelFont, "(%s)"%self.label, "center", "bottom" ))
            dx = float(self.width())/self.numdiv
            align=["right"]+["center"]*(self.numdiv-1)+["left"]
            for x in range(0,self.numdiv+1):
                a = x *(self.max - self.min)/self.numdiv + self.min
                s = '%4.1f'%(a)
                pos=QPoint(x*dx, 1)
                self.axis.append((self.textPen, pos, self.labelFont, s, align[x], "bottom"))
        else: #position != 'horizontal'
            pos=QPoint(2,0.1*self.height())
            self.axis.append((self.textPen, pos, self.labelFont, "(%s)" %self.label, "right", "top"))
            dy = float(self.height())/self.numdiv
            align=["bottom"]+["center"]*(self.numdiv-1)+["top"]
            for y in range(0,self.numdiv+1):
                a = y*(self.max - self.min)/5
                if self.max > 99:
                    s = '%4.0f'%(self.max-a)
                else:
                    s = '%4.1f'%(self.max-a)
                pos=QPoint(self.width(), int(y*dy))
                self.axis.append((self.textPen, pos, self.labelFont, s, "left", align[y]))
        # enforce a repaint
        self.scene().invalidate(self.sceneRect())

    def paintEvent(self, event=None):
        """
        redefinition of the SLOT which deals with paint events (raised
        by repaint or update)
        @param event the paint event
        """
        QGraphicsView.paintEvent(self, event)
        painter=QPainter(self.viewport())
        painter.save()
        for pen, pos, font, text, xlayout, ylayout in self.axis:
            painter.setPen(pen)
            painter.setFont(font)
            fm=painter.fontMetrics()
            w=fm.width(text)+5
            h=fm.height()
            x=pos.x()
            y=pos.y()
            if xlayout == "left":
                x-=w
            elif xlayout == "center":
                x-=w/2
            if ylayout == "bottom":
                y+=h
            elif ylayout == "top":
                y-=h/2
            pos=QPoint(x,y)
            painter.drawText(pos, text)
        painter.restore()
