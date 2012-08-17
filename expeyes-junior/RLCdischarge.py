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
import expeyes.eyesj as eyes, expeyes.eyeplot as eyeplot, expeyes.eyemath as eyemath, time, sys, math


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


def discharge():
	global data, history, trial
	p.set_state(10,1)			# OD1 to HIGH
	p.enable_set_low(10)		# enable LOW for OD1
	time.sleep(0.5)
	t, v = p.capture_hr(1,NP,delay)
	g.delete_lines()
	g.line(t,v)
	data = t,v
	history.append(data)
	trial += 1
	msgwin.config(text = _('Discharge Done'))

def fit_curve():
	global data, trial
	s = _('Fit Failed')
	fa = eyemath.fit_dsine(data[0], data[1],1)
	if fa != None:
		#print fa[1]
		pa = fa[1]
		rc = 1.0 / pa[1]
		damping = pa[4] / (2*math.pi*pa[1]) # unitless damping factor
		s = _('Resonant Frequency = %5.2f kHz Damping = %5.3f')%(pa[1], damping)
		g.line(data[0],fa[0],trial)
	msgwin.config(text = s)

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
root = Tk()
Canvas(root, width = WIDTH, height = 5).pack(side=TOP)  # Some space at the top
g = eyeplot.graph(root, width=WIDTH, height=HEIGHT)	# make plot objects using draw.disp
g.setWorld(0, -5, 20,5,_('V'),_('mA'))

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)

l = Label(cf, text=_('mS/div'))
l.pack(side=LEFT, anchor = SW )
timebase = Scale(cf,command = set_timebase, orient=HORIZONTAL, length=50, showvalue=False,\
	from_ = 0, to=9, resolution=1)
timebase.pack(side=LEFT, anchor = SW)
timebase.set(0)

b = Button(cf,text =_('5->0V STEP'), command = discharge)
b.pack(side=LEFT, anchor = SW)

b = Button(cf,text =_('Save to'), command=save)
b.pack(side=LEFT, anchor = SW)
fn = Entry(cf,width = 10, bg = 'white')
fn.pack(side=LEFT, anchor = SW)
fn.insert(END,'rlc.dat')
b = Button(cf,text =_('QUIT'), command=sys.exit)
b.pack(side=RIGHT, anchor = SW)
b = Button(cf,text =_('Xmgrace'), command=xmgrace)
b.pack(side=RIGHT, anchor = SW)
b4 = Button(cf, text = _('CLEAR'), command = clear)
b4.pack(side = RIGHT, anchor = N)
b4 = Button(cf, text = _('FIT'), command = fit_curve)
b4.pack(side = RIGHT, anchor = N)

mf = Frame(root)				# Message Frame below command frame.
mf.pack(side=TOP, anchor = S)
msgwin = Label(mf,text = _('Messages'), fg = 'blue')
msgwin.pack(side=LEFT, anchor = S, fill=BOTH)
eyeplot.pop_image('pics/LCRcircuit.png', _('RLC Circuit, Transient'))
root.title(_('EYES Junior: RLC Discharge'))
root.mainloop()

