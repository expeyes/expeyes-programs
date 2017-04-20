'''
expEYES program
Author  : Ajith Kumar B.P, bpajith@gmail.com
License : GNU GPL version 3
'''

import gettext
gettext.bindtextdomain("expeyes")
gettext.textdomain('expeyes')
_ = gettext.gettext

from Tkinter import *
import expeyes.eyes17 as eyes, expeyes.eyeplot17 as eyeplot, expeyes.eyemath17 as eyemath, time, sys
VER = sys.version[0]
if VER == '3':
	from tkinter import *
else:
	from Tkinter import *

TIMER = 10
WIDTH  = 600   # width of drawing canvas
HEIGHT = 400   # height    

VSET    = 0		# this will change in the loop
VSETMIN = 0		# may change this to -5 for zeners
VSETMAX = 4.8
STEP    = 0.050		# 50 mV
MINX    = 0			# may change this to -5 for zeners
MAXX    = 3         # No diode will go beyond this
MINY    = 0			# may change this to -5 for zeners
MAXY    = 5			# Maximum possible current
history = []		# Data store
trial = 0			# trial number
data = [ [], [] ]	# Current & Voltage
index = 0
running = False

def start():
	global VSET, running, index, data
	VSETMIN = 0.0
	MINX = 0.0
	MINY = 0.0
	p.select_range('A1',4)
	g.setWorld(MINX, MINY, MAXX, MAXY,'V',_('mA'))
	running = True
	data = [ [], [] ]
	VSET = VSETMIN
	index = 0
	root.after(TIMER,update)

def update():					# Called periodically by the Tk toolkit
	global VSETMAX, VSET, STEP, index, trial, running, data, history
	if running == False:
		return
	vs = p.set_pv1(VSET)	
	time.sleep(0.001)	
	va = p.get_voltage('A1')		# voltage across the diode
	i = (vs-va)/1.0 	 		   # in mA, R= 1k
	data[0].append(va)
	data[1].append(i)
	VSET += STEP
	if VSET > VSETMAX:
		running = False
		history.append(data)
		trial += 1
		g.delete_lines()
		for k in range(len(history)):
			g.line(history[k][0], history[k][1], k)
		return
	if index > 1:			# Draw the line
		g.delete_lines()
		g.line(data[0], data[1], trial)
	index += 1
	root.after(TIMER, update)
	msg.config(text=_('Starting to plot I-V'))

def xmgrace():		# Send the data to Xmgrace
	global history
	eyeplot.grace(history, _('Volts'), _('mA'), _('Diode IV Curve'))

def save():
	global history, running
	if running == True:
		return
	s = e1.get()
	if s == '':
		return
	p.save(history, s)
	msg.config(text = _('Data saved to file ')+s)

def fit_curve():
	global data, running
	if running == True or len(data[0])==0:
		return
	f = eyemath.fit_exp(data[0], data[1])
	if f != None:
		g.line(data[0], f[0], 1)
		k = 1.38e-23    # Boltzmann const
		q = 1.6e-19     # unit charge
		Io = f[1][0]
		a1 = f[1][1]
		T = 300.0		# Room temp in Kelvin
		n = q/(a1*k*T)
		s = _('Fitted with Diode Equation : Io = %5.2e mA , Ideality factor = %5.2f')%(Io,n)
		msg.config(text = s)

def clear():
	global history, trial, running
	if running == True:
		return
	g.delete_lines()
	history = []
	trial = 0

p = eyes.open()
root = Tk()
Canvas(root, width = WIDTH, height = 5).pack(side=TOP)  # Some space at the top
g = eyeplot.graph(root, width=WIDTH, height=HEIGHT, bip=False)	# make plot objects using draw.disp
g.setWorld(MINX, MINY, MAXX, MAXY,_('V'),_('mA'))

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)

b1 = Button(cf, text = _('START'), command = start)
b1.pack(side = LEFT, anchor = N)
b3 = Button(cf, text = _('SAVE to'), command = save)
b3.pack(side = LEFT, anchor = N)
filename = StringVar()
e1 =Entry(cf, width=15, bg = 'white', textvariable = filename)
filename.set('diode_iv.dat')
e1.pack(side = LEFT)

b5 = Button(cf, text = _('QUIT'), command = sys.exit)
b5.pack(side = RIGHT, anchor = N)
b4 = Button(cf, text = _('CLEAR'), command = clear)
b4.pack(side = RIGHT, anchor = N)
b5 = Button(cf, text = _('Grace'), command = xmgrace)
b5.pack(side = RIGHT, anchor = N)
b5 = Button(cf, text = _('FIT'), command = fit_curve)
b5.pack(side = RIGHT, anchor = N)

mf = Frame(root, width = WIDTH, height = 10)
mf.pack(side=TOP,  fill = BOTH, expand = 1)
msg = Label(mf,text=_('Message'), fg = 'blue')
msg.pack(side=LEFT)

t = _('Diode IV Characteristic')
eyeplot.pop_help('diode_iv', t)
root.title(t)
root.mainloop()

