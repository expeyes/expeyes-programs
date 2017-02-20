'''
expEYES program
Author  : Ajith Kumar B.P, bpajith@gmail.com
License : GNU GPL version 3
'''

from Tkinter import *
import expeyes.mca
import expeyes.eyeplot as eyeplot, expeyes.eyemath as eyemath, time

TIMER = 1000
WIDTH  = 600   # width of drawing canvas
HEIGHT = 400   # height 
VPERDIV = 1.0  # Volts per division, vertical scale
NCHAN  = 512
running = False
automode = False
xmax = NCHAN -1 
ymax = 100
xlabel = 'Channel'
xscale = 1.0	# before calibration
ch = []
ee = []

def set_ymax(w):
	global xmax, ymax, xlabel
	ymax = 10.0**float(scale.get())
	g.setWorld(0, 0, xmax, ymax, xlabel, 'dN')	

def calibrate():
	global xscale, xmax, ymax, xlabel, ee, nn, NCHAN
	if ee == []:
		msg('No data yet','red')
		return  
	if g.markerval == []:
		msg('Mark a Peak before calibration','red')
		return  
	if xscale == 1.0:   # Not calibrated yet
		chan = g.markerval[0]
		en = float(Energy.get())
		xscale = en/chan
		xmax = xmax * xscale
		for k in range(NCHAN):
			ee[k] *= xscale
		xlabel = 'Energy (MeV)'
		g.setWorld(0, 0, xmax, ymax,'Energy(MeV)','dN')
		g.delete_lines()
		g.line(ee,nn)
		msg('Calibration done')
	else:  							# Remove the existing calibration
		ee = range(NCHAN)
		xscale = 1.0
		xmax = NCHAN - 1
		g.setWorld(0, 0, xmax, ymax,'Channel','dN')
		msg('Existing Calibration Removed. Do it again')
		g.markerval = []
	
def zoom():
	global running, ch, nn
	if running == True: return
	m = p.maximum(nn)
	x,y = g.get_markers()
	g.setWorld(x[0], 0, x[1], m*1.1,'E','dN')
	g.delete_lines()
	g.line(ch,nn)

def fit():
	global ofp, strt, ee,nn, counter
	if ee == []:
		msg('No data to fit','red')
		return  
	nf, par = eyemath.fit_gauss(ee,nn)
	g.line(ee,nf,1)
	s ='Amplitude= %5.1f  %s= %5.2f  sigma = %5.2f'%(par[0], xlabel, par[1], par[2])
	msg(s)
	#except: 		msg('Fit Failed. Try using xmgrace')

def set_mode():
	global automode 
	if AUTO.get() == 1:
		automode = True
		root.after(TIMER,update)
	else:
		automode = False

def update():
	global running, automode, ee, nn
	if running == True:
		ch,nn = p.read_hist()
		#m = p.maximum(nn)
		g.setWorld(0,0, xmax, ymax, xlabel,'dN')
		g.delete_lines()
		ee = []
		for k in ch:
			ee.append(k*xscale)
		g.line(ee,nn,smooth = False)
		if automode == True:
			root.after(TIMER,update)

def start():
	global running
	p.start_hist()
	running = True
	root.after(TIMER,update)
	msg('Acquisition Started')

def stop():
	global running
	running = False
	p.stop_hist()
	msg('Acquisition stopped by user')

def clear():
	p.clear_hist()
	g.delete_lines()
	msg('Spectrum Cleared by user')

def save():
	global ch,ee
	p.save([[ee,nn]], filename.get())
	msg('Histogram saved')

def xmgrace():
	global ch,ee
	p.grace([[ee,nn]], xlabel, 'dN')
	msg('Called xmgrace')

def msg(s, col = 'blue'):
	msgwin.config(text=s, fg=col)

p = expeyes.mca.open()
root = Tk()
Canvas(root, width = WIDTH, height = 5).pack(side=TOP)  # Some space at the top
g = eyeplot.graph(root, width=WIDTH, height=HEIGHT)	    # make plot objects using draw.disp
g.enable_marker(2)
g.setWorld(0, -5, 20, 5,'E','dN/dE')

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)
l = Label(cf, text = 'y-scale')
l.pack(side=LEFT, anchor = SW)

scale = Scale(cf,command = set_ymax, orient=HORIZONTAL, length=50, showvalue=False,\
	from_ = 1, to=5, resolution=1)
scale.pack(side=LEFT, anchor = SW)
scale.set(2)

AUTO = IntVar()
b1=Checkbutton(cf,text='Auto/Man', command = set_mode, variable=AUTO, fg= 'black')
b1.pack(side=LEFT, anchor = SW)
b1 = Button(cf, text = 'UPDATE', command = update)
b1.pack(side = LEFT, anchor = N)
b1 = Button(cf, text = 'START', command = start)
b1.pack(side = LEFT, anchor = N)
b1 = Button(cf, text = 'STOP', command = stop)
b1.pack(side = LEFT, anchor = N)
b4 = Button(cf, text = 'CLEAR', command = clear)
b4.pack(side = LEFT, anchor = N)
b4 = Button(cf, text = 'FIT', command = fit)
b4.pack(side = LEFT, anchor = N)
b4 = Button(cf, text = 'xmGrace', command = xmgrace)
b4.pack(side = LEFT, anchor = N)

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)
b3 = Button(cf, text = 'Calibrate using Peak at', command = calibrate)
b3.pack(side = LEFT, anchor = N)
Energy = StringVar()
e1 =Entry(cf, width=6, bg = 'white', textvariable = Energy)
Energy.set('8.955')
e1.pack(side = LEFT)
l = Label(cf, text = 'MeV')
l.pack(side = LEFT, anchor = S)

b3 = Button(cf, text = 'SAVE Histogram to', command = save)
b3.pack(side = LEFT, anchor = N)
filename = StringVar()
e1 =Entry(cf, width=15, bg = 'white', textvariable = filename)
filename.set('hist.dat')
e1.pack(side = LEFT)

#b4 = Button(cf, text = 'ZOOM', command = zoom)
#b4.pack(side = LEFT, anchor = N)

b5 = Button(cf, text = 'QUIT', command = sys.exit)
b5.pack(side = RIGHT, anchor = N)

mf = Frame(root)				# Message Frame below command frame.
mf.pack(side=TOP, anchor = SW)
msgwin = Label(mf,text = 'Messages', fg = 'blue')
msgwin.pack(side=LEFT, anchor = SW)

if p == None:
	root.title('ERROR: Spectrometer hardware NOT found')
	msg('ERROR: Spectrometer hardware NOT found', 'red')
else:
	root.title('PHOENIX Alpha Spectrometer')
root.after(TIMER,update)
root.mainloop()

