from Tkinter import *

AXWIDTH = 30   # width of the axis display canvas

class disp:
    """
    Class for displaying items in a canvas using a world coordinate system. The range of the
    world coordinate system is specified by calling the setWorld method.
    """
    border = 0
    pad = 0
    bordcol = 'grey'     # Border color
    gridcol = 'grey'     # Grid color
    bgcolor = '#dbdbdb'  # background color for all 
    plotbg  = 'ivory'    # Plot window background color
    textcolor = 'blue'
    traces = []
    xtext = []
    ytext = []
    markerval = []
    markertext = None
       
    def __init__(self, parent, width=400., height=100.,color = 'ivory'):
	self.parent = parent
	self.SCX = width 
	self.SCY = height
	self.plotbg = color
	f = Frame(parent, bg = self.bgcolor, borderwidth = self.pad)
	f.pack(side=TOP)
	self.yaxis = Canvas(f, width = AXWIDTH, height = height, bg = self.bgcolor)
	self.yaxis.pack(side = LEFT, anchor = N, pady = self.border)
	f1 = Frame(f)
	f1.pack(side=LEFT)
	self.canvas = Canvas(f1, background = self.plotbg, width = width, height = height)
	self.canvas.pack(side = TOP)
        self.canvas.bind("<Button-1>", self.show_xy)
	self.xaxis = Canvas(f1, width = width, height = AXWIDTH, bg = self.bgcolor)
	self.xaxis.pack(side = LEFT, anchor = N, padx = self.border)
	self.canvas.create_rectangle ([(1,1),(width,height)], outline = self.bordcol)
	self.canvas.pack()
	Canvas(f, width = AXWIDTH, height = height, bg = self.bgcolor).pack(side=LEFT) # spacer only
	self.setWorld(0 , 0, self.SCX, self.SCY)   # initialize scale factors 
	self.grid(10,100)

    def setWorld(self, x1, y1, x2, y2):   #Calculates the scale factors 
	self.xmin = float(x1)
	self.ymin = float(y1)
	self.xmax = float(x2)
	self.ymax = float(y2)
	self.xscale = (self.xmax - self.xmin) / (self.SCX)
	self.yscale = (self.ymax - self.ymin) / (self.SCY)
      
    def w2s(self, p):	      # World to Screen xy conversion before plotting anything
	ip = []
	for xy in p:
		ix = self.border + int( (xy[0] - self.xmin) / self.xscale)
		iy = self.border + int( (xy[1] - self.ymin) / self.yscale)
		iy = self.SCY - iy
		ip.append((ix,iy))
	return ip

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
	self.markertext = self.canvas.create_text(self.border + 1,\
	self.SCY-1, anchor = SW, justify = LEFT, text = s)
	self.markerval = [x,y]

    def mark_axes(self, xlab='milli seconds', ylab='mV', numchans=1):
	# Draw the axis labels and values
        numchans = 1
        for t in self.xtext:	# display after dividing by scale factors
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
            t = self.xaxis.create_text(int(x*dx)+adjust,1,text = s, anchor=N, fill = self.textcolor)
            self.xtext.append(t)
        self.xtext.append(self.xaxis.create_text(int(self.SCX/2)\
            ,AXWIDTH, text = xlab, anchor=S, fill = self.textcolor))
            
        dy = float(self.SCY)/5
        for y in range(0,6):
            a = y*(self.ymax - self.ymin)/5	# + self.ymin
            if self.ymax > 99:
                s = '%4.0f'%(self.ymax-a)
            else:
                s = '%4.1f'%(self.ymax-a)
            adjust = 0
            if y == 0: adjust = 6
            if y == 5: adjust = -5
            t = self.yaxis.create_text(AXWIDTH, int(y*dy)+adjust, \
                text = s,anchor = E, fill = self.textcolor)
            self.ytext.append(t)
        self.ytext.append(self.yaxis.create_text(0,self.SCY/2,\
            text = ylab, anchor=W, fill = self.textcolor))

    def box(self, x1,  y1,  x2,  y2, col):
       ip = self.w2s([(x1,y1),(x2,y2)])
       self.canvas.create_rectangle(ip, outline=col)

    def line(self, points, col, permanent = False, smooth = True):
       ip = self.w2s(points)
       t = self.canvas.create_line(ip, fill=col, smooth = smooth)
       if permanent == False:
           self.traces.append(t)

    def delete_lines(self):
       for t in self.traces:
           self.canvas.delete(t)
       self.traces = []

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

#------------------------------- disp class end --------------------------------------

