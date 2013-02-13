'''
Plotting libray, using Qt4 for expEYES
Author  : Georges Khaznadar <georgesk@debian.org>
Based on Ajith Kumar's work
License : GNU GPL version 3
'''

from PyQt4.QtCore import *
from PyQt4.QtGui import *

AXWIDTH = 40   # width of the axis display canvas
AYWIDTH = 50   # width of the axis display canvas
NUMDIV  = 5
NGRID1  = 10
NGRID2  = 10
BGCOL     = Qt.white
PLOTBGCOL = Qt.white
LINEWIDTH = 2 
LINECOL   = [Qt.black, Qt.red, Qt.blue, Qt.green, Qt.cyan, Qt.magenta,
             Qt.yellow, Qt.darkYellow,Qt.gray, Qt.darkGray]
LABELCOL  = Qt.blue
TEXTCOL   = Qt.black

GRIDCOL   = Qt.gray
NGRID1    = 10
NGRID2    = 5

class plotWidget(QGraphicsView):
    border = 2
    pad = 0
    bordcol = Qt.gray     # Border color
    gridcol = Qt.gray     # Grid color
    bgcolor = '#dbdbdb'  # background color for all 
    plotbg  = 'ivory'    # Plot window background color
    textPen = QPen(Qt.blue)
    labelPen = QPen(LABELCOL)
    dotGridPen = QPen(gridcol)
    solidGridPen = QPen(gridcol)
    traces = []
    gridLines=[]
    xaxis = []
    yaxis = []
    legendtext = []
    scaletext = []
    markerval = []
    markertext = None
    xlabel = 'mSec'            # Default axis lables
    ylabel = 'V'

    def __init__(self, parent=None, width=400., height=300.,color = 'white', labels = True, bip=True):
        """
        constructor.
        @param parent a widget (default=None)
        @param width width of the graph (default=400.0)
        @param height height of the graph (default=300.0)
        @param color background color
        @param labels True to display labels (default=True)
        @param bip True if the O V is in the middle (default=True)
        """
        QGraphicsView.__init__(self, parent)
        self.parent = parent
        self.labels = labels
        self.SCX = width 
        self.SCY = height
        self.plotbg = color
        self.bipolar = bip
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(QRectF(0, 0, self.SCX, self.SCY))
        self.setScene(self.scene)
        self.labelFont=QFont("Courier New")
        self.labelFont.setPixelSize(11)
        self.dotGridPen.setStyle(Qt.DotLine)
        self.solidGridPen.setStyle(Qt.SolidLine)
        #TODO: pack self into the parent

        self.setWorld(0 , 0, self.SCX, self.SCY)
        self.grid()

    def setWorld(self, x1, y1, x2, y2):
        '''
        Calculates the scale factors for world to screen coordinate transformation. 
        '''
        self.xmin = float(x1)
        self.ymin = float(y1)
        self.xmax = float(x2)
        self.ymax = float(y2)
        self.xscale = (self.xmax - self.xmin) / (self.SCX)
        self.yscale = (self.ymax - self.ymin) / (self.SCY)   
        self.mark_labels()
        if self.labels == True:
            return
        for txt in self.scaletext:
            self.scene.removeItem(txt)
        self.scaletext = []
        s = '%3.2f %s/div'%( (self.xmax-self.xmin)/NGRID1, self.xlabel)
        t =  self.scene.addSimpleText(s)
        t.setPos(QPointF(2, self.SCY*9/20))
        t.setPen(self.labelPen)
        self.scaletext.append(t)
        s = '%3.2f %s/div'%( (self.ymax-self.ymin)/NGRID1, ylabel)
        t =  self.scene.addSimpleText(s)
        t.setPos(QPointF(self.SCX/2,10))
        t.setPen(self.labelPen)
        self.scaletext.append(t)

    def mark_labels(self):
        '''
        Draws the X and Y axis divisions and labels. Only used internally.
        '''
        if self.labels == False:
            return

        self.xaxis = []
        self.yaxis = []
        pos=QPoint(self.SCX/2, self.SCY-AXWIDTH+15)
        self.xaxis.append((self.textPen, pos, self.labelFont, self.xlabel, "right", "bottom" ))
        dx = float(self.SCX)/NUMDIV
        for x in range(0,NUMDIV+1):
            a = x *(self.xmax - self.xmin)/NUMDIV + self.xmin
            s = '%4.1f'%(a)
            adjust = 0
            if x == 0: adjust = 6
            if x == NUMDIV: adjust = -10
            pos=QPoint(x*dx+adjust, self.SCY-AXWIDTH)
            self.xaxis.append((self.textPen, pos, self.labelFont, s, "center", "bottom"))
        pos=QPoint(2,(self.SCY-AXWIDTH)/2)
        self.yaxis.append((self.textPen, pos, self.labelFont, self.ylabel, "right", "top"))
        dy = float(self.SCY)/NUMDIV
        for y in range(0,NUMDIV+1):
            a = y*(self.ymax - self.ymin)/5    # + self.ymin
            if self.ymax > 99:
                s = '%4.0f'%(self.ymax-a)
            else:
                s = '%4.1f'%(self.ymax-a)
            if y == 0:
                shift=5
            elif y == NUMDIV:
                shift = -6
            else:
                shift = 0
            pos=QPoint(AYWIDTH, int(y*dy)+shift)
            self.yaxis.append((self.textPen, pos, self.labelFont, s, "center", "center"))

    def polyline(self, x, y, pen=0, replaces=None):
        """
        draws a polyline in the grid with the coordinates of the world
        @param x a vector of abscissas
        @param y a vector of ordinates
        @param pen a QPen, or an index to colors in LINECOL
        @param replaces the polyline to replace if any
        @return a reference to the tuple (pen, polygon) which was issued
        """
        if replaces:
            self.traces.delete(replaces)
        ip = self.w2s(x,y)
        pol=QPolygonF(ip)
        if not isinstance(pen,QPen):
            pen=QPen(LINECOL[pen%len(LINECOL)])
        self.traces.append((pen,pol))
        self.update()

    def delete_lines(self):
        """
        removes all the traces
        """
        self.traces=[]
        return

    def paintEvent(self, event=None):
        """
        redefinition of the SLOT which deals with paint events (raised by repaint or update)
        @param event the paint event
        """
        QGraphicsView.paintEvent(self, event)
        painter=QPainter(self.viewport())
        painter.save()
        for pen, pos, font, text, xlayout, ylayout in self.xaxis + self.yaxis:
            painter.setPen(pen)
            painter.setFont(font)
            fm=painter.fontMetrics()
            w=fm.width(text)
            h=fm.height()
            x=pos.x()
            y=pos.y()
            if xlayout == "left":
                x-=w
            elif xlayout == "center":
                x-=w/2
            if ylayout == "bottom":
                y+=h
            elif ylayout == "center":
                y+=h/2
            pos=QPoint(x,y)
            painter.drawText(pos, text)
        for pen, pol in self.gridLines + self.traces:
            painter.setPen(pen)
            painter.drawPolyline(pol)
        painter.restore()

    def grid(self):
        dx = (self.xmax - self.xmin) / NGRID1
        dy = (self.ymax - self.ymin) / NGRID1
        x = self.xmin + dx
        #print(self.ymin)
        if self.bipolar == True:
            ip = self.w2s((self.xmax/2,self.xmax/2),(self.ymin,self.ymax))
            self.gridLines.append((self.solidGridPen,QPolygonF(ip)))
            ip = self.w2s((self.xmin,self.xmax),(self.ymax/2,self.ymax/2))  
            self.gridLines.append((self.solidGridPen,QPolygonF(ip)))

        
        while x < self.xmax:
            ip = self.w2s((x,x),(self.ymin,self.ymax))  
            self.gridLines.append((self.dotGridPen,QPolygonF(ip)))
            x = x +dx
        y = self.ymin + dy
        while y < self.ymax:
            ip = self.w2s( (self.xmin,self.xmax), (y,y) )
            self.gridLines.append((self.dotGridPen,QPolygonF(ip)))
            y = y +dy

    def w2s(self, x,y):
        """
        World to Screen xy conversion before plotting anything
        @param x a vector of abscissas
        @param y a vector of ordinates (same length)
        @return a list of QPoints converted to screen coordinates
        """
        ip = []
        for i in range(len(x)):
            ix = self.border + int( (x[i] - self.xmin) / self.xscale)
            iy = self.border + int( (y[i] - self.ymin) / self.yscale)
            iy = self.SCY - iy
            ip.append(QPointF(ix,iy))
        return ip

                          

if __name__ == '__main__':
    import numpy as np
    app = QApplication(sys.argv)
    view = graph()
    view.show()
    nbPoint=100
    x=np.fromiter((400.0*x/nbPoint for x in range(nbPoint+1)), dtype=np.float)
    def myfunc(a):
        return 100*np.sin(a/20)+150
    vecfunc=np.vectorize(myfunc)
    y=vecfunc(x)
    view.polyline(x,y)
    sys.exit(app.exec_())
