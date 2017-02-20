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
import expeyes.eyes as eyes, expeyes.eyeplot as eyeplot, expeyes.eyemath as eyemath, time, sys

TIMER = 10
WIDTH  = 600   # width of drawing canvas
HEIGHT = 400   # height    

VSET    = 0		# this will change in the loop
VSETMIN = 0		# may change this to -5 for zeners
VSETMAX = 4.5
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
	if ZEN.get() == 1:
		VSETMIN = -5.0
		MINX = -5.0
		MINY = -5
	else:
		VSETMIN = 0.0
		MINX = 0.0
		MINY = 0.0
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
	p.set_voltage(0, VSET)	
	time.sleep(0.001)	
	va = p.get_voltage(0)		# voltage across the diode
	i = (VSET-va)/1.0 	 		# in mA, R= 1k
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
	p.grace(history, _('Volts'), _('mA'), _('Diode IV Curve'))

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
p.loadall_calib()
p.disable_actions()
root = Tk()
Canvas(root, width = WIDTH, height = 5).pack(side=TOP)  # Some space at the top
g = eyeplot.graph(root, width=WIDTH, height=HEIGHT)	# make plot objects using draw.disp
g.setWorld(MINX, MINY, MAXX, MAXY,'V','mA')

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)

ZEN = IntVar()
cb0 = Checkbutton(cf,text =_('ZENER'), variable=ZEN, fg = 'black')
cb0.pack(side=LEFT, anchor = SW)
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

eyeplot.pop_image('pics/diode-iv.png', _('Diode IV Characteristic'))
root.title(_('EYES: Diode IV characteristics'))
root.mainloop()

