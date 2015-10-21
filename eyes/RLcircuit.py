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

from Tkinter import *
import expeyes.eyes as eyes, expeyes.eyeplot as eyeplot, expeyes.eyemath as eyemath, time, math, sys

TIMER = 100
WIDTH  = 500   # width of drawing canvas
HEIGHT = 350   # height 
VPERDIV = 1.0		# Volts per division, vertical scale
delay = 10			# Time interval between samples
NP = 100			# Number of samples
data = [ [], [] ]
history = []		# Data store
trial = 0			# trial number
data = [ [], [] ]	# Current & Voltage


def capture(i):
	global data, history, trial
	s = ''
	if i == 0:  # Take OD1 LOW. To HIGH before capture
		p.write_outputs(0)		# OD1 to LOW
		p.enable_set_high(1)	# enable for OD1
	else:  # Take OD1 HI. To HIGH before capture
		p.write_outputs(2)		# OD1 to HI
		p.enable_set_low(1)		# enable for OD1
	time.sleep(0.5)
	t, v = p.capture(0,NP,delay)
	g.line(t,v, trial)
	data = t,v
	history.append(data)
	trial += 1
	msgwin.config(text = _('Done'))

def fit_curve():
	global data
	p.write_outputs(2)			# Do some DC work to find the resistance of the Inductor
	time.sleep(.5)
	Rext = 	float(Res.get())
	vtotal = 5.0				# Assume OD1 = 5 volts
	v = p.get_voltage(2)
	if v > 4.8:					# Means user has connected OD1 to A2
		vtotal = v
	Vind = p.get_voltage(0)     # voltage across the Inductor
	i = (vtotal - Vind)/Rext
	Rind = Vind/i
	print (v,Rind)
	fa = eyemath.fit_exp(data[0], data[1])
	if fa != None:
		pa = fa[1]
		print (pa)
		par1 = abs(1.0 / pa[1])
		g.line(data[0],fa[0],1)
		dispmsg(_('L/R = %5.3f mSec : Rind = %5.0f Ohm : L = %5.1f mH')%(par1, Rind, (Rext+Rind)*par1))
	else:
		dispmsg(_('Failed to Fit. Try fitting V=Vo*exp(-tR/L) with Xmgrace'))

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
	p.grace(history, _('milliSeconds'), _('Volts'))

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

p = eyes.open()
p.loadall_calib()
root = Tk()
Canvas(root, width = WIDTH, height = 5).pack(side=TOP)  # Some space at the top
g = eyeplot.graph(root, width=WIDTH, height=HEIGHT)	# make plot objects using draw.disp
g.setWorld(0, -5, 20,5,_('V'),_('mA'))
if p == None:
	g.text(0, 0,_('EYES Hardware Not Found. Check Connections and restart the program'),1)
	root.mainloop()
	sys.exit()

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)

l = Label(cf, text=_('mS/div'))
l.pack(side=LEFT, anchor = SW )
timebase = Scale(cf,command = set_timebase, orient=HORIZONTAL, length=50, showvalue=False,\
	from_ = 0, to=9, resolution=1)
timebase.pack(side=LEFT, anchor = SW)
timebase.set(0)
b = Button(cf,text =_('0 to 5V STEP'), command= lambda i=0:capture(i))
b.pack(side=LEFT, anchor = SW)
b = Button(cf,text =_('5 to 0V STEP'), command= lambda i=1:capture(i))
b.pack(side=LEFT, anchor = SW)
b4 = Button(cf, text = _('CLEAR'), command = clear)
b4.pack(side = LEFT, anchor = N)
b = Button(cf,text =_('Save to'), command=save)
b.pack(side=LEFT, anchor = SW)
fn = Entry(cf,width = 10, bg = 'white')
fn.pack(side=LEFT, anchor = SW)
fn.insert(END,'rl.dat')

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)
b = Button(cf,text =_('Xmgrace'), command=xmgrace)
b.pack(side=LEFT, anchor = SW)
l = Label(cf, text=_('Rext='))
l.pack(side=LEFT, anchor = SW)
Res = Entry(cf,width = 10, bg = 'white')
Res.pack(side=LEFT, anchor = SW)
Res.insert(END,'1000')
b = Button(cf,text =_('Calculate R/L'), command=fit_curve)
b.pack(side=LEFT, anchor = SW)

b = Button(cf,text =_('QUIT'), command=sys.exit)
b.pack(side=RIGHT, anchor = SW)

mf = Frame(root)				# Message Frame below command frame.
mf.pack(side=TOP)
msgwin = Label(mf,text = '', fg = 'blue')
msgwin.pack(side=LEFT, anchor = S, fill=BOTH)
eyeplot.pop_image('pics/rl-tran.png', _('RL Circuit, Transient'))
root.title(_('Transient response of RL Circuit'))
root.mainloop()

