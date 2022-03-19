'''
expEYES program
Author  : Ajith Kumar B.P, bpajith@gmail.com
License : GNU GPL version 3
'''
from __future__ import print_function

import gettext
gettext.bindtextdomain("expeyes")
gettext.textdomain('expeyes')
_ = gettext.gettext

from tkinter import *
import expeyes.eyes as eyes, expeyes.eyeplot as eyeplot, expeyes.eyemath as eyemath, time

TIMER = 100
WIDTH  = 600   # width of drawing canvas
HEIGHT = 400   # height 
VPERDIV = 1.0		# Volts per division, vertical scale
delay = 10			# Time interval between samples
NP = 100			# Number of samples
NC = 1				# Number of channels
chanmask = 1		# 01, 10 or 11 binary
measure  = 0
chan = [0,1,2,4]

def select_chan():
	global chanmask, measure
	if SEN.get() == 1:
		CH0.set(0)
		CH1.set(0)
		CH2.set(0)
	elif CH2.get() == 1:
		CH0.set(0)
		CH1.set(0)
		SEN.set(0)
	chanmask = CH0.get() | (CH1.get() << 1) | (CH2.get() << 2) | (SEN.get() << 3)  
	measure = FIT.get()
	msgwin.config(text=_('You can select SEN, A2 or (A1, A0 or both)'))

def set_vertical(w):
	global delay, NP, NC, VPERDIV
	divs = [1.0, 0.5, 0.2]
	VPERDIV = divs[int(vpd.get())]
	g.setWorld(0,-5*VPERDIV, NP * delay * 0.001, 5*VPERDIV,_('mS'),_('V'))
	print (VPERDIV)

def set_timebase(w):
	global delay, NP, NC, VPERDIV
	divs = [0.050, 0.100, 0.200, 0.500, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0]
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
	g.setWorld(0,-5*VPERDIV, NP * delay * 0.001, 5*VPERDIV,_('mS'),_('V'))
	print (_('NP delay = '),NP, delay, 0.0001 * NP*delay, msperdiv)

def update():
	global NP, delay, chanmask, measure, chan
	s = ''
	if chanmask == 8:		# SENSOR
		t,v = p.capture(4,NP,delay)
		g.delete_lines()
		g.line(t,v,3)
		if measure == 1:
			fa = eyemath.fit_sine(t,v)
			if fa != None:
				pa = fa[1]
				s = _('Vpeak = %5.2f V | Freq = %5.2f Hz')%(abs(pa[0]), pa[1]*1000)
	elif chanmask == 4:		# A2
		t,v = p.capture(2,NP,delay)
		g.delete_lines()
		g.line(t,v,2)
		if measure == 1:
			fa = eyemath.fit_sine(t,v)
			if fa != None:
				pa = fa[1]
				s = _('Vpeak = %5.2f V | Freq = %5.2f Hz')%(abs(pa[0]), pa[1]*1000)
			msgwin.config(text = s)
	elif chanmask == 1 or chanmask == 2:
		t,v = p.capture(chanmask-1,NP,delay)
		g.delete_lines()
		g.line(t,v,chanmask-1)
		if measure == 1:
			fa = eyemath.fit_sine(t,v)
			if fa != None:
				pa = fa[1]
				s = _('Vpeak = %5.2f V | Freq = %5.2f Hz')%(abs(pa[0]), pa[1]*1000)
			msgwin.config(text = s)
	elif chanmask == 3:
		t,v,tt,vv = p.capture01(NP,delay)
		g.delete_lines()
		g.line(t,v)
		g.line(tt,vv,1)
		if measure == 1:
			fa = eyemath.fit_sine(t,v)
			if fa != None:
				pa = fa[1]
				s = _('CH0 Vp = %5.2f V | Freq = %5.2f Hz ')%(abs(pa[0]), pa[1]*1000)
			fb = eyemath.fit_sine(tt,vv)
			if fb != None:
				pb = fb[1]
				s = s + _('CH1 Vp = %5.2f V | Freq = %5.2f Hz')%(abs(pb[0]), pb[1]*1000)
			msgwin.config(text = s)
	else:
		g.delete_lines()
	root.after(10,update)


p = eyes.open()
p.loadall_calib()
root = Tk()
Canvas(root, width = WIDTH, height = 5).pack(side=TOP)  # Some space at the top
g = eyeplot.graph(root, width=WIDTH, height=HEIGHT)	# make plot objects using draw.disp
g.setWorld(0, -5, 20, 5,_('mS'),_('V'))

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)
l = Label(cf,text = _('mS/div'))
l.pack(side=LEFT, anchor = SW)
timebase = Scale(cf,command = set_timebase, orient=HORIZONTAL, length=50, showvalue=False,\
	from_ = 0, to=9, resolution=1)
timebase.pack(side=LEFT, anchor = SW)
l = Label(cf,text = _('Volt/div'))
l.pack(side=LEFT, anchor = SW)
vpd = Scale(cf,command = set_vertical, orient=HORIZONTAL, length=50, showvalue=False,\
	from_ = 0, to=2, resolution=1)
vpd.pack(side=LEFT, anchor = SW)

CH0 = IntVar()
cb0 = Checkbutton(cf,text ='A0', command=select_chan, variable=CH0, fg = 'black')
cb0.pack(side=LEFT, anchor = SW)
CH0.set(1)

CH1 = IntVar()
cb1 = Checkbutton(cf,text ='A1', command=select_chan, variable=CH1, fg = 'red')
cb1.pack(side=LEFT, anchor = SW)
CH1.set(0)

CH2 = IntVar()
cb2 = Checkbutton(cf,text ='A2', command=select_chan, variable=CH2, fg = 'blue')
cb2.pack(side=LEFT, anchor = SW)
CH2.set(0)

SEN = IntVar()
sen = Checkbutton(cf,text =_('SEN'), command=select_chan, variable=SEN, fg = 'blue')
sen.pack(side=LEFT, anchor = SW)
SEN.set(0)

FIT = IntVar()
b=Checkbutton(cf,text=_('FIT'), command = select_chan, variable=FIT, fg= 'black')
b.pack(side=LEFT, anchor = SW)
b5 = Button(cf, text = _('QUIT'), command = sys.exit)
b5.pack(side = RIGHT, anchor = N)

mf = Frame(root)				# Message Frame below command frame.
mf.pack(side=TOP, anchor = SW)
msgwin = Label(mf,text = _('Messages'), fg = 'blue')
msgwin.pack(side=LEFT, anchor = SW)

root.title(_('EYES CRO Program'))
root.after(TIMER,update)
root.mainloop()

