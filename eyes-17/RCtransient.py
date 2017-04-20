'''
expEYES program
Author  : Ajith Kumar B.P, bpajith@gmail.com
License : GNU GPL version 3
'''
import gettext
gettext.bindtextdomain("expeyes")
gettext.textdomain('expeyes')
_ = gettext.gettext

import expeyes.eyes17 as eyes, expeyes.eyeplot17 as eyeplot, expeyes.eyemath17 as eyemath, time, sys, math
VER = sys.version[0]
if VER == '3':
	from tkinter import *
else:
	from Tkinter import *

TIMER = 100
WIDTH  = 500   # width of drawing canvas
HEIGHT = 350   # height 
VPERDIV = 1.0		# Volts per division, vertical scale
delay = 20			# Time interval between samples
NP = 100			# Number of samples
data = [ [], [] ]
history = []		# Data store
trial = 0			# trial number
data = [ [], [] ]	# Current & Voltage
divs = [0.050, 0.100, 0.200, 0.500, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100]


def charge():
	global data, history, trial, divs
	tmax = 0.01*divs[int(timebase.get())]  # in seconds
	s = ''
	p.set_state(OD1=0)		# OD1 to LOW
	time.sleep(tmax)
	t, v = p.capture_action('A1',NP,delay,'SET_HIGH')
	g.line(t,v, trial)
	data = t,v
	history.append(data)
	trial += 1
	msgwin.config(text = _('Done'))



def discharge():
	global data, history, trial, divs
	tmax = 0.01*divs[int(timebase.get())]  # in seconds
	s = ''
	p.set_state(OD1=1)		# OD1 to HIGH
	time.sleep(tmax)
	t, v = p.capture_action('A1',NP,delay,'SET_LOW')
	g.line(t,v, trial)
	data = t,v
	history.append(data)
	trial += 1
	msgwin.config(text = _('Done'))

def cccharge():
	global data, history, trial
	s = ''
	p.set_state(CCS=0)		# CCS disabled
	time.sleep(0.5)
	t, v = p.capture_action('A1',NP,delay, 'SET_STATE', CCS=True, OD1=False)
	g.line(t,v, trial)
	data = t,v
	history.append(data)
	trial += 1
	msgwin.config(text = _('Done'))



def view_all():
	global history
	g.delete_lines()
	c = 0
	for t,v in history:
		g.line(t,v,c)
		c += 1

def fit_curve():
	global data
	fa = eyemath.fit_exp(data[0], data[1])
	if fa != None:
		pa = fa[1]
		rc = abs(1.0 / pa[1])
		g.line(data[0],fa[0],1)
		dispmsg(_('RC = %5.2f mSec')%rc)
	else:
		dispmsg(_('Failed to fit the curve with V=Vo*exp(-t/RC)'))

def dispmsg(s):
	msgwin.config(text=s)

def clear():
	global history, trial
	g.delete_lines()
	history = []
	trial = 0

def save():
	global history
	s = fn.get()
	if s == '':
		return
	p.save(history, s)
	msgwin.config(text = _('Data saved to file ')+s)

def xmgrace():		# Send the data to Xmgrace
	global history
	eyeplot.grace(history, _('milliSeconds'), _('Volts'))

def set_timebase(w):
	global delay, NP, NC, VPERDIV, divs
	msperdiv = divs[int(timebase.get())]
	totalusec = int(msperdiv * 1000 * 10)
	NP = 100								# Assume 100 samples to start with
	delay = int(totalusec/100)				# Calculate delay
	if delay < 10:
		sf = 10/delay
		delay = 10
		NP = NP/sf
	elif delay > 1000:
		sf = delay/1000
		delay = 1000
		NP = NP * sf
	g.setWorld(0.0, 0.0, NP * delay * 0.001, 5.0,_('mS'),_('V'))

p = eyes.open()
root = Tk()
Canvas(root, width = WIDTH, height = 5).pack(side=TOP)  # Some space at the top
g = eyeplot.graph(root, width=WIDTH, height=HEIGHT, bip=False)	# make plot objects using draw.disp
g.setWorld(0, 0, 20,5,_('V'),_('mA'))
if p == None:
	g.text(0, 0,_('EYES Hardware Not Found. Check Connections and restart the program'),1)
	root.mainloop()
	sys.exit()

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)

l = Label(cf, text=_('mS/div'))
l.pack(side=LEFT, anchor = SW )
timebase = Scale(cf,command = set_timebase, orient=HORIZONTAL, length=50, showvalue=False,\
	from_ = 0, to=10, resolution=1)
timebase.pack(side=LEFT, anchor = SW)
timebase.set(3)
b = Button(cf,text =_('0 to 5V STEP'), command= charge)
b.pack(side=LEFT, anchor = SW)
b = Button(cf,text =_('5 to 0V STEP'), command= discharge)
b.pack(side=LEFT, anchor = SW)
b = Button(cf,text =_('CC Charge'), command= cccharge)
b.pack(side=LEFT, anchor = SW)
b = Button(cf,text =_('Calculate RC'), command=fit_curve)
b.pack(side=LEFT, anchor = SW)
b = Button(cf,text =_('QUIT'), command=sys.exit)
b.pack(side=RIGHT, anchor = SW)

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)
b = Button(cf,text =_('ViewAll'), command=view_all)
b.pack(side=LEFT, anchor = SW)
b = Button(cf,text =_('Xmgrace'), command=xmgrace)
b.pack(side=LEFT, anchor = SW)
b4 = Button(cf, text = _('CLEAR'), command = clear)
b4.pack(side = LEFT, anchor = N)
b = Button(cf,text =_('Save to'), command=save)
b.pack(side=LEFT, anchor = SW)
fn = Entry(cf,width = 10, bg = 'white')
fn.pack(side=LEFT, anchor = SW)
fn.insert(END,'rc.dat')

mf = Frame(root)				# Message Frame below command frame.
mf.pack(side=TOP)
msgwin = Label(mf,text = '', fg = 'blue')
msgwin.pack(side=LEFT, anchor = S, fill=BOTH)

t = _('Transient response of RC Circuit')
eyeplot.pop_help('RCtransient', t)
root.title(t)
p.select_range('A1',8)
root.mainloop()

