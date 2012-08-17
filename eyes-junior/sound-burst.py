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
import expeyes.eyesj as eyes, expeyes.eyeplot as eyeplot, expeyes.eyemath as eyemath, time, math, sys

TIMER = 100
WIDTH  = 700   # width of drawing canvas
HEIGHT = 300   # height 
VPERDIV = 1.0		# Volts per division, vertical scale
delay = 15			# Time interval between samples
NP = 1800			# Number of samples
data = [ [], [] ]
history = []		# Data store
trial = 0			# trial number
data = [ [], [] ]	# Current & Voltage


def find_peaks(ta,va):   # returns the index of the peaks found
	vmin = 5.0
	vmax = -5.0
	p1 = 0		# index of the peaks
	p2 = 0
	t1 = t2 = 0
	size = len(ta)
	for i in range(size):
		if va[i] < vmin:
			vmin = va[i]
			p1 = i
		if va[i] > vmax:
			vmax = va[i]
			p2 = i
	#print p1,p2,vmin, vmax
	if p1 < p2:			# return left side peak first
		return p1,p2
	else:
		return p2,p1

def base_scan():
	global data, history, trial, NP, delay, noise
	p.disable_actions()
	t, v = p.capture(1,NP,delay)
	g.delete_lines()
	g.line(t,v,trial)
	running = True
	data = [ [], [] ]
	p1,p2 = find_peaks(t,v)
	noise = abs(v[p1])
	msgwin.config(text = _('Volatge Scan Done. Noise Level = %5.3f V')%noise)
	print WAIT.get()
	if WAIT.get() == '1':
		print _('wait')
		p.enable_wait_high(3)
	root.after(TIMER, update)

def update():
	global data, history, trial, NP, delay, noise
	t, v= p.capture(1,NP,delay)		
	p1,p2 = find_peaks(t,v)
	#print v[p1], v[p2], NP
	if abs(v[p1] - noise) > 0.5 and p1 < NP:  # Signal at least 0.5 volts above noise
		g.delete_lines()
		g.line(t,v,trial)
		data = [t,v]
		#s = _('Peak voltages %5.2f and %5.3f separated by %5.3f msec') %(v[p1], v[p2], t[p2]-t[p1])
		msgwin.config(text = _('Captured Sound Burst'))
		#print len(tn), len(vn), v[p1], v[p2]
		history.append(data)
		trial += 1
		return				
	root.after(TIMER, update)

def xmgrace():		# Send the data to Xmgrace
	global data
	p.grace([data], _('milliSeconds'), _('Volts'))

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

def viewall():		# Send the data to Xmgrace
	global history
	g.delete_lines()	
	i = 0
	for t,v in history:
		g.line(t,v,i)
		i += 1
def quit():
	p.disable_actions()
	sys.exit()

p = eyes.open()
root = Tk()
Canvas(root, width = WIDTH, height = 5).pack(side=TOP)  # Some space at the top
g = eyeplot.graph(root, width=WIDTH, height=HEIGHT)	# make plot objects using draw.disp
g.setWorld(0,-5*VPERDIV, NP * delay * 0.001, 5*VPERDIV,_('mS'),_('V'))

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)
WAIT = IntVar()
cb1 = Checkbutton(cf,text =_('Wait for HIGH on IN1'), variable=WAIT, fg = 'blue')
cb1.pack(side=LEFT, anchor = SW)
WAIT.set(0)

b = Button(cf,text =_('Start Scanning'), command= base_scan)
b.pack(side=LEFT, anchor = SW)
b4 = Button(cf, text = _('CLEAR'), command = clear)
b4.pack(side = LEFT, anchor = N)
b = Button(cf,text =_('VIEW'), command=viewall)
b.pack(side=LEFT, anchor = SW)
b = Button(cf,text =_('XmGrace'), command=xmgrace)
b.pack(side=LEFT, anchor = SW)

b = Button(cf,text =_('Save to'), command=save)
b.pack(side=LEFT, anchor = SW)
fn = Entry(cf,width = 10, bg = 'white')
fn.pack(side=LEFT, anchor = SW)
fn.insert(END,'sound.dat')
b = Button(cf,text =_('QUIT'), command=quit)
b.pack(side=LEFT, anchor = SW)

mf = Frame(root)				# Message Frame below command frame.
mf.pack(side=TOP, anchor = SW)
msgwin = Label(mf,text = _('Messages'), fg = 'blue')
msgwin.pack(side=LEFT, anchor = SW)

eyeplot.pop_image('pics/sound-burst.png', _('Capture a burst of sound'))
root.title(_('EYESJUN: Capturing burst of sound'))
root.mainloop()

