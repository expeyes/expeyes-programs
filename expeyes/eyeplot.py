'''
Plotting libray, using Tkinter for expEYES
Author  : Ajith Kumar B.P, bpajith@gmail.com
License : GNU GPL version 3
'''
from __future__ import print_function

import gettext
gettext.bindtextdomain("expeyes")
gettext.textdomain('expeyes')
_ = gettext.gettext


import os, sys
if sys.version_info.major==3:
        from tkinter import *
else:
        from Tkinter import *

AXWIDTH = 30   # width of the axis display canvas
AYWIDTH = 50   # width of the axis display canvas
NUMDIV  =5
NGRID1	= 10
NGRID2  = 10
BGCOL	  = 'white'
PLOTBGCOL = 'white'
LINEWIDTH = 1.5
LINECOL   = ['black', 'red', 'blue', 'magenta', 'cyan', 'green', 'yellow', 'orange','gray', 'gray2']
LABELCOL  = 'blue'
TEXTCOL   = 'black'

GRIDCOL   = 'gray'
NGRID1	 = 10
NGRID2   = 5

class graph:
    '''
    Class for displaying items in a canvas using a world coordinate
    system. The range of the world coordinate system is specified by
    calling the setWorld method.
    '''
    border = 2
    pad = 0
    bordcol = 'grey'     # Border color
    gridcol = 'grey'     # Grid color
    bgcolor = '#dbdbdb'  # background color for all 
    plotbg  = 'ivory'    # Plot window background color
    textcolor = 'blue'
    traces = []
    xtext = []
    ytext = []
    legendtext = []
    scaletext = []
    markerval = []
    markertext = None
    xlabel = _('mSec')			# Default axis lables
    ylabel = 'V'
    markers = []
       
    def __init__(self, parent, width=400., height=300.,color = 'white', labels = True, bip=True):
        self.parent = parent
        self.labels = labels
        self.SCX = width 
        self.SCY = height
        self.plotbg = color
        self.bipolar = bip
        
        if labels == False:
            f = Frame(self.parent, bg = 'black', borderwidth = self.border, relief = FLAT)
            f.pack(side=TOP, anchor = S)
            self.canvas = Canvas(f, bg = self.plotbg, width = width, height = height)
            self.canvas.pack(side = TOP, anchor = S)
        else:
            f = Frame(parent, bg = self.bgcolor)
            f.pack(side=TOP)
            self.yaxis = Canvas(f, width = AYWIDTH, height = height, bg = self.bgcolor)
            self.yaxis.pack(side = LEFT, anchor = N, pady = self.border)
            f1 = Frame(f)
            f1.pack(side=LEFT)
            self.canvas = Canvas(f1, bg = self.plotbg, width = width, height = height, bd =0, relief=FLAT)
            self.canvas.pack(side = TOP)
            self.canvas.bind("<Button-1>", self.show_xy)
            self.xaxis = Canvas(f1, width = width, height = AXWIDTH, bg = self.bgcolor)
            self.xaxis.pack(side = LEFT, anchor = N, padx = self.border)
            self.canvas.create_rectangle ([(1,1),(width,height)], outline = self.bordcol)
            Canvas(f, width = 4, height = height, bg = self.bgcolor).pack(side=LEFT) # spacer only
            self.setWorld(0 , 0, self.SCX, self.SCY, self.xlabel, self.ylabel)   # initialize scale factors 
            self.grid()
        return

    """----------------- Another window -----------------"""
    def clear_fm(self):
        try:
            self.canvas.delete(self.msg_window)
        except:
            pass

    def disp(self, msg):
        self.clear_fm()
        win = Button(text = msg, bg = 'yellow', fg='blue', font=("Helvetica", 30), command=self.clear_fm)
        self.msg_window = self.canvas.create_window(self.SCX/4, self.SCY/10, window=win, anchor=NW)


    """---------- Manage the Marker's ---------"""
    def enable_marker(self, marker_max = 3):
        self.canvas.bind("<Button-3>", self.show_marker)
        self.CURMAX = marker_max

    def clear_markers(self):
        for k in self.markers:
            self.canvas.delete(k[2])  #third item is the text on the canvas
        self.markers = []

    def show_marker(self, event):
        if len(self.markers) >= self.CURMAX:
            self.clear_markers()
            return
        ix = self.canvas.canvasx(event.x) - self.border
        iy = self.SCY - self.canvas.canvasy(event.y) #- self.border
        x = ix * self.xscale + self.xmin
        y = iy * self.yscale + self.ymin
        m = self.canvas.create_text(ix, self.SCY-iy, text = 'x', fill = 'red')
        self.markers.append((x,y,m))
        print (x,y)

    def get_markers(self):
        x = []
        y = []
        for k in self.markers:
            x.append(k[0])
            y.append(k[1])
        return x,y
    
    """--------------------------------------------------"""

    def setWorld(self, x1, y1, x2, y2, xlabel, ylabel):
        '''
        Calculates the scale factors for world to screen coordinate
        transformation. 
        '''
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.xmin = float(x1)
        self.ymin = float(y1)
        self.xmax = float(x2)
        self.ymax = float(y2)
        self.xscale = (self.xmax - self.xmin) / (self.SCX)
        self.yscale = (self.ymax - self.ymin) / (self.SCY)   
        self.mark_labels()
        if self.labels == True:
            return
        try:
            for txt in self.scaletext:
                self.canvas.delete(txt)
                self.scaletext = []
        except:
            pass
        s = _('%3.2f %s/div')%( (self.xmax-self.xmin)/NGRID1, xlabel)
        t =  self.canvas.create_text(2, self.SCY*11/20,
                                     anchor = SW, justify = LEFT,
                                     fill = LABELCOL, text = s)
        self.scaletext.append(t)
        s = _('%3.2f %s/div')%( (self.ymax-self.ymin)/NGRID1, ylabel)
        t =  self.canvas.create_text(self.SCX/2, self.SCY-10,
                                     anchor = SW, justify = LEFT,
                                     fill = LABELCOL, text = s)
        self.scaletext.append(t)

    def mark_labels(self):
        '''
        Draws the X and Y axis divisions and labels. Only used
        internally.
        '''
        if self.labels == False:
            return

        for t in self.xtext:	# display after dividing by scale factors
            self.xaxis.delete(t)
        for t in self.ytext:
            self.yaxis.delete(t)
        self.xtext = []
        self.ytext = []
        self.xtext.append(self.xaxis.create_text(
            int(self.SCX/2),
            AXWIDTH-2,
            text = self.xlabel,
            anchor=S,
            fill = self.textcolor))
        dx = float(self.SCX)/NUMDIV
        for x in range(0,NUMDIV+1):
            a = x *(self.xmax - self.xmin)/NUMDIV + self.xmin
            s = '%4.1f'%(a)
            adjust = 0
            if x == 0: adjust = 6
            if x == NUMDIV: adjust = -10
            t = self.xaxis.create_text(int(x*dx)+adjust,1,text = s, anchor=N, fill = self.textcolor)
            self.xtext.append(t)

        self.ytext.append(self.yaxis.create_text(
            2,self.SCY/2,
            text = self.ylabel, anchor=W, fill = self.textcolor))
        dy = float(self.SCY)/NUMDIV
        for y in range(0,NUMDIV+1):
            a = y*(self.ymax - self.ymin)/5	# + self.ymin
            if self.ymax > 99:
                s = '%4.0f'%(self.ymax-a)
            else:
                s = '%4.1f'%(self.ymax-a)
            adjust = 0
            if y == 0: adjust = 6
            if y == NUMDIV: adjust = -5
            t = self.yaxis.create_text(
                AYWIDTH, int(y*dy)+adjust,
                text = s,anchor = E, fill = self.textcolor)
            self.ytext.append(t)


    def show_xy(self,event):   #Prints the XY coordinates of the current cursor position
        ix = self.canvas.canvasx(event.x) - self.border
        iy = self.SCY - self.canvas.canvasy(event.y) #- self.border
        x = ix * self.xscale + self.xmin
        y = iy * self.yscale + self.ymin
        s = 'x = %5.3f\ny = %5.3f' % (x,y)
        try:
            self.canvas.delete(self.markertext)
        except:
            pass
        self.markertext = self.canvas.create_text(
            self.border + 1,
            self.SCY-1, anchor = SW, justify = LEFT, text = s)
        self.markerval = [x,y]

    def grid(self):
        dx = (self.xmax - self.xmin) / NGRID1
        dy = (self.ymax - self.ymin) / NGRID1
        x = self.xmin + dx
        print (self.ymin)
        if self.bipolar == True:
            ip = self.w2s((self.xmax/2,self.xmax/2),(self.ymin,self.ymax))  
            self.canvas.create_line(ip, fill=self.gridcol, width=LINEWIDTH)
            ip = self.w2s((self.xmin,self.xmax),(self.ymax/2,self.ymax/2))  
            self.canvas.create_line(ip, fill=self.gridcol, width=LINEWIDTH)
		
            while x < self.xmax:
                ip = self.w2s((x,x),(self.ymin,self.ymax))  
                self.canvas.create_line(ip, fill=self.gridcol, dash= (1,int(dy/NGRID2)-1), width=LINEWIDTH)
                x = x +dx
        y = self.ymin + dy
        while y < self.ymax:
            ip = self.w2s( (self.xmin,self.xmax), (y,y) )
            self.canvas.create_line(ip, fill=GRIDCOL, dash= (1,int(dx/NGRID2)-1), width=LINEWIDTH)
            y = y +dy

    def w2s(self, x,y):	      # World to Screen xy conversion before plotting anything
        ip = []
        for i in range(len(x)):
            ix = self.border + int( (x[i] - self.xmin) / self.xscale)
            iy = self.border + int( (y[i] - self.ymin) / self.yscale)
            iy = self.SCY - iy
            ip.append((ix,iy))
        return ip

    def round4axis(self,n):
        if n == 0:
            return n
        sign = 1
        if n < 0:
            sign = -1
            n = -1 * n
        div = 0
        if n > 10:
            while n > 10:
                n = n/10
                div = div + 1
            res = (int(n)+1)* 10**div		
            return sign * float(res)
        elif n <= 10:
            while n < 1:
                n = n*10
                div = div + 1
            res = (int(n)+1)	
        return sign * float(res) / 10**div

    def auto_scale(self, x,y):
        '''
        Sets the range of the world co-ordinate system from two lists
        of x and y.  The range of y-coordinates are rounded. (for
        ymin=5 and ymax=95 will set the limits from 0 to 100)
        '''
        xmin = x[0]
        xmax = x[-1]
        ymin = 1.0e10
        ymax = 1.0e-10
        for k in y:
            if k > ymax: ymax = k
            if k < ymin: ymin = k
        ymin = self.round4axis(ymin)
        ymax = self.round4axis(ymax)
        if ymin == ymax:	# avoid a divide by zero error
            return
        print (xmin,ymin,xmax,ymax)
        self.setWorld(xmin,ymin,xmax,ymax,self.xlabel,self.ylabel)

    def box(self, x1,  y1,  x2,  y2, col):
        ip = self.w2s((x1,y1),(x2,y2))
        self.canvas.create_rectangle(ip, outline=col)

    def text(self, x,  y, text, col=0):
        ip = self.w2s( [float(x)],[float(y)])
        x = ip[0][0]
        t = self.canvas.create_text(
            ip[0][0],ip[0][1], text = text,
            anchor = W, fill = LINECOL[col%len(LINECOL)])
        self.legendtext.append(t)

    def delete_text(self):
        for t in self.legendtext:
            self.canvas.delete(t)
        self.legendtext = []

    def line(self, x,y, col=0, smooth = True):
        ip = self.w2s(x,y)
        t = self.canvas.create_line(ip, fill=LINECOL[col%len(LINECOL)], width=LINEWIDTH, smooth = smooth)
        self.traces.append(t)

    def delete_lines(self):
        for t in self.traces:
            self.canvas.delete(t)
        self.traces = []
        
    """---------------------- graph class end -------------------"""

    def plot(x,y,title = None, xl = None, yl = None):
        # plot the x,y coordinate list to a new , non-blocking, window.
        if title==None:
            title=_('EYES plot')
        if xl==None:
            xl=_('mS')
        if yl==None:
            yl=_('V')
        w = Tk()
        w.title(title)
        g = graph(w, width=600, height=400)
        g.xlabel = xl
        g.ylabel = yl
        g.auto_scale(x,y)
        g.line(x,y)
        return g


    """------ popup window to displaying image ----------"""
    
def abs_path():	   # Returns the absolute path of the python program
    name = sys.argv[0]
    dirname = os.path.dirname(name)
    print (dirname)
    if dirname != '':
        return os.path.dirname(name) + os.sep 
    else:
        return '.' + os.sep

img = None
def pop_image(sch, title = _('Schematic')):
    global img   	
    try:
        import Image, ImageTk, tkFont
        top = Toplevel()
        Label(top,text=title,fg='blue').pack(side=TOP)
        top.title(_('Schematic'))
        im = Image.open(abs_path() + sch)
        w,h= im.size
        img = ImageTk.PhotoImage(im)
        panel = Canvas(top, bg='white', width = w, height = h)
        panel.create_image(0,0,image = img, anchor = NW)
        panel.pack()

    except:
        pass

# Local Variables:
# python-indent: 4
# End:
