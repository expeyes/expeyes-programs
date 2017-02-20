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
import expeyes.eyes17 as eyes, expeyes.eyeplot17 as eyeplot, expeyes.eyemath17 as eyemath, time, sys, math


TIMER = 10
WIDTH  = 600   # width of drawing canvas
HEIGHT = 400   # height    

VSET    = 0		# this will change in the loop
VSETMIN = 0		# may change this to -5 for zeners
VSETMAX = 4.5
STEP    = 0.050		# 50 mV
MINX    = 0			# may change this to -5 for zeners
MAXX    = 5         # We have only 5V supply
MINY    = 0			# may change this to -5 for zeners
MAXY    = 5			# Maximum possible current
history = []		# Data store
trial = 0			# trial number
data = [ [], [] ]	# Current & Voltage
index = 0
running = False

def start():
	global VSET, running, index, data, ibase
	if running == True:
		msg.config(text=_('Busy Drawing'))
		return
	p.set_pv1(5.0)				# Collector to 5V
	vbset = float(Bias.get())
	if vbset < .5 or vbset > 3.0:
		msg.config(text=_('Base valtage shold be from .5 to 3V'))
		return
	p.set_pv2(vbset)			# Set base bias on PV2, via 100 KOhm series resistance
	ibase = (vbset-0.6)/100.0e-3    # uA
	msg.config(text=_('Base Current = %5.1f uA')%(ibase))
	data = [ [], [] ]
	VSET = VSETMIN
	index = 0
	running = True
	root.after(TIMER,update)

def load_line():
	global running, history, data, trial
	if running == True:
		msg.config(text=_('Busy Drawing'))
		return
	VSET = 4.5
	p.set_voltage(VSET)            # Questionable action
	index = 0
	data = [ [], [] ]
	for vb in range(1,5):
		p.set_pv1(1,float(vb))
		va = p.get_voltage('A1')		# voltage across the diode
		i = (VSET-va)/1.0 	 		# in mA, R= 1k
		data[0].append(va)
		data[1].append(i)
	history.append(data)
	trial += 1
	g.line(data[0], data[1],trial)

def update():					# Called periodically by the Tk toolkit
	global VSETMAX, VSET, STEP, index, trial, running, data, history
	if running == False:
		return
	vs = p.set_pv1(VSET)	
	time.sleep(0.001)	
	va = p.get_voltage('A1')	# voltage across the diode
	i = (vs-va)/1.0 	 		# in mA, R= 1k
	data[0].append(va)
	data[1].append(i)
	VSET += STEP
	if VSET > VSETMAX or i >= 0.8 * MAXX:  # Graph upto 4V only, leave space for text
		running = False
		history.append(data)
		trial += 1
		g.delete_lines()
		for k in range(len(history)):
			g.line(history[k][0], history[k][1], k)
		g.text(va, i, _('Ib=%4.0f uA') %ibase,k)
		return
	if index > 1:			# Draw the line
		g.delete_lines()
		g.line(data[0], data[1], trial)
	index += 1
	root.after(TIMER, update)

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

def clear():
	global history, trial, running
	if running == True:
		return
	g.delete_lines()
	g.delete_text()
	history = []
	trial = 0

p = eyes.open()

root = Tk()
Canvas(root, width = WIDTH, height = 5).pack(side=TOP)  # Some space at the top
g = eyeplot.graph(root, width=WIDTH, height=HEIGHT, bip=False)	# make plot objects using draw.disp
g.setWorld(MINX, MINY, MAXX, MAXY,_('V'),_('mA'))

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)

l = Label(cf, text=_('Vb (via 200K)='))
l.pack(side=LEFT, anchor = SW )
Bias =StringVar()
Bias.set('1.0')
e =Entry(cf, width=5, bg = 'white', textvariable = Bias)
e.pack(side = LEFT)
l = Label(cf, text='V')
l.pack(side=LEFT, anchor = SW )
b1 = Button(cf, text = _('START'), command = start)
b1.pack(side = LEFT, anchor = N)
b3 = Button(cf, text = _('SAVE to'), command = save)
b3.pack(side = LEFT, anchor = N)
filename = StringVar()
e1 =Entry(cf, width=15, bg = 'white', textvariable = filename)
filename.set('tran_ce.dat')
e1.pack(side = LEFT)

b5 = Button(cf, text = _('QUIT'), command = sys.exit)
b5.pack(side = RIGHT, anchor = N)
b4 = Button(cf, text = _('CLEAR'), command = clear)
b4.pack(side = RIGHT, anchor = N)
b5 = Button(cf, text = _('Grace'), command = xmgrace)
b5.pack(side = RIGHT, anchor = N)
#b5 = Button(cf, text = _('LINE'), command = load_line)
#b5.pack(side = RIGHT, anchor = N)

mf = Frame(root, width = WIDTH, height = 10)
mf.pack(side=TOP,  fill = BOTH, expand = 1)
msg = Label(mf,text=_('Message'), fg = 'blue')
msg.pack(side=LEFT)

eyeplot.pop_image('pics/transistor-ce.png', _('Transistor CE Char (NPN)'))
root.title(_('EYES Junior: Transistor CE characteristics'))
root.mainloop()

