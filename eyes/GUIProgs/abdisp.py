from tkinter import *
import Image, ImageTk, ImageDraw, sys, math
import phm, time

class disp:
    """
    Class for displaying items in a canvas using a global coordinate system.
    """
    border = 2
    pad = 4
    bordcol = '#555555'
    gridcol = '#f0f0f0'
    gridcol2 ='#e0e0e0'
    aw = 30        # width to display axis labels
    traces = []
    line_data = []
    xtext = []
    ytext = []
    markerval = []
    markertext = None
    marker = []

    def __init__(self, parent, width=400., height=300.,color='red'):
        self.parent = parent
        self.SCX = width - self.aw - self.border - self.pad
        self.SCY = height - self.aw - self.border - self.pad
        self.XLIM = self.SCX + 2 * self.border
        self.YLIM = self.SCY + 2 * self.border
        f = Frame(parent, bg = color, borderwidth = self.pad)
        f.pack()
        self.yaxis = Canvas(f, width = self.aw, height = self.SCY, bg = color)
        self.yaxis.pack(side = LEFT, anchor = N, pady = self.border)
        f1 = Frame(f, bg = color)
        f1.pack()
        self.canvas = Canvas(f1, background=color, \
                             width = self.XLIM, height = self.YLIM, )
        self.canvas.pack(side = TOP)
        self.canvas.bind("<Button-1>", self.show_xy)
        self.canvas.bind("<Button-3>", self.show_xy)

        self.xaxis = Canvas(f1, width = self.SCX, height = self.aw, bg = color)
        self.xaxis.pack(side = LEFT, anchor = N, padx = self.border)

        b1 = (self.border - 1, self.border-1)
        b2 = (self.XLIM - self.border + 1, self.YLIM - self.border + 1)
        self.canvas.create_rectangle ([b1,b2], outline = self.bordcol)
        self.canvas.pack()

        self.setWorld(-0.5 * self.SCX, -0.5*self.SCY, 0.5 * self.SCX,\
                      0.5* self.SCY)
        self.grid(10,100)

    def mark_axes(self, xlab='milli seconds', ylab='Volts', numchans=1):
        numchans = 1
        for t in self.xtext:    # display after dividing by scale factors
            self.xaxis.delete(t)
        for t in self.ytext:
            self.yaxis.delete(t)
        self.xtext = []
        self.ytext = []

        dx = float(self.SCX)/5
        for x in range(0,6):
            a = numchans * x *(self.xmax - self.xmin)/5 + self.xmin
            s = '%4.1f'%(a)
            adjust = 0
            if x == 0: adjust = 6
            if x == 5: adjust = -10
            t = self.xaxis.create_text(int(x*dx)+adjust,1,text = s, anchor=N)
            self.xtext.append(t)
        self.xtext.append(self.xaxis.create_text(int(self.SCX/2)\
                                                 ,self.aw,text = xlab,
                                                 anchor=S))

        dy = float(self.SCY)/5
        for y in range(0,6):
            a = y*(self.ymax - self.ymin)/5    # + self.ymin
            if self.ymax > 99:
                s = '%4.0f'%(self.ymax-a)
            else:
                s = '%4.1f'%(self.ymax-a)
            adjust = 0
            if y == 0: adjust = 6
            if y == 5: adjust = -5
            t = self.yaxis.create_text(self.aw, int(y*dy)+adjust, \
                                       text = s,anchor = E)
            self.ytext.append(t)
        self.ytext.append(self.yaxis.create_text(0,self.SCY/2,\
                                                 text = ylab, anchor=W))


    def setWorld(self, x1, y1, x2, y2):
        #Calculate the scale factors to be used by functions drawPoint etc.
        self.xmin = float(x1)
        self.ymin = float(y1)
        self.xmax = float(x2)
        self.ymax = float(y2)
        self.xscale = (self.xmax - self.xmin) / (self.SCX)
        self.yscale = (self.ymax - self.ymin) / (self.SCY)
    

    def w2s(self, p):    # World to Screen conversion
        ip = []
        for xy in p:
            ix = self.border + int( (float(xy[0]) - self.xmin) / self.xscale)
            iy = self.border + int( (float(xy[1]) - self.ymin) / self.yscale)
            iy = self.YLIM - iy
            ip.append((ix,iy))
        return ip
       
    def box(self, x1,  y1,  x2,  y2, col):
        ip = self.w2s([(x1,y1),(x2,y2)])
        self.canvas.create_rectangle(ip, outline=col)

    def grid(self, major, minor):
        dx = (self.xmax - self.xmin) / major
        dy = (self.ymax - self.ymin) / major
        x = self.xmin + dx
        while x < self.xmax:
            self.line([(x,self.ymin),(x,self.ymax)],self.gridcol, True)
            x = x +dx
            y = self.ymin + dy
        while y < self.ymax:
            self.line([(self.xmin,y),(self.xmax,y)],self.gridcol, True)
            y = y +dy

        dx = (self.xmax - self.xmin) / minor
        dy = (self.ymax - self.ymin) / minor
        x = self.xmin + dx
        while x < self.xmax:
           self.line([(x, 0.),(x, dy)],self.gridcol2, True)
           x = x +dx

        y = self.ymin + dy
        while y < self.ymax:
            self.line([(0., y),(dx,y)],self.gridcol2, True)
            y = y +dy

    def show_xy(self,event):
        """
        Prints the XY coordinated of the current cursor position
        """
        ix = self.canvas.canvasx(event.x) - self.border
        iy = self.YLIM - self.canvas.canvasy(event.y) - self.border
        x = ix * self.xscale + self.xmin
        y = iy * self.yscale + self.ymin

        if event.num == 1:
            s = 'x = %5.0f\ny = %5.3f' % (x,y)
            self.marker = [(x,y)]
        elif event.num == 3:
            if self.marker == []: return
        self.marker.append((x,y))
        first = self.marker[0]
        s = 'x = %5.0f  dx = %5.0f\ny = %5.3f  dy = %5.3f' % \
            (first[0], x-first[0], first[1], y - first[1])
        try:
            self.canvas.delete(self.xydisp)
        except:
            pass
        self.xydisp = self.canvas.create_text(self.border+1,self.SCY-1, \
                                              anchor = SW, justify = LEFT,
                                              text = s)

    def auto_scale(self, data):
        xmin = data[0][0]
        xmax = data[-1][0]
        ymin = 1.0e10
        ymax = 1.0e-10
        for k in range(len(data)):
            if data[k][1] > ymax: ymax = data[k][1]
            if data[k][1] < ymin: ymin = data[k][1]
        #    print 'AS ', xmin, ymin, xmax, ymax
        self.setWorld(xmin,ymin,xmax,ymax*1.1)
        for t in self.traces:
            self.canvas.delete(t)
        self.traces = []
        for t in self.line_data:
            ip = self.w2s(t[0])
            t = self.canvas.create_line(ip, fill=t[1], smooth = 0)
            self.traces.append(t)

    def zoom(self):
        if len(self.marker) < 2: return
        xmin = min(self.marker[0][0],self.marker[1][0])
        xmax = max(self.marker[0][0],self.marker[1][0])
        ymin = min(self.marker[0][1],self.marker[1][1])
        ymax = max(self.marker[0][1],self.marker[1][1])
        self.setWorld(xmin,ymin,xmax,ymax)
        #    print 'ZOOM', xmin, ymin, xmax, ymax
        for t in self.traces:
            self.canvas.delete(t)
        self.traces = []
        for t in self.line_data:
            ip = self.w2s(t[0])
            t = self.canvas.create_line(ip, fill=t[1], smooth = 0)
            self.traces.append(t)

    def line(self, points, col, permanent = False, smooth = 0):
        ip = self.w2s(points)
        t = self.canvas.create_line(ip, fill=col, smooth = smooth)
        if permanent == False:
            self.traces.append(t)
            self.line_data.append((points, col))
        # print (self,'NT = ', len(self.traces))

    def delete_lines(self):
        for t in self.traces:
            self.canvas.delete(t)
        self.traces = []
        self.line_data = []
