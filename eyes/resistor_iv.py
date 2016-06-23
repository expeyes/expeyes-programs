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
import expeyes.eyes as eyes, expeyes.eyeplot as eyeplot, expeyes.eyemath as eyemath, time, sys, numpy


TIMER = 100
WIDTH  = 600   # width of drawing canvas
HEIGHT = 400   # height    

NP = 30
imin = 0.05
imax = 3.0
vmax = 2.0		    # Nature of the current source
history = []		# Data store
trial = 0			# trial number
data = [ [], [] ]	# Current & Voltage
index = 0
running = False

def start():
	global running, NP, imin, imax, data, index
	v = ph.set_current(0.1)	# 0.1 mA
	if v > 2.0:                # for v = 2V, R = 2.0/0.0001 = 20 kOhm 
		msg.config(text=_('CS (28) is open or the resistor connected is > 20 kOhm'))
		return	
	running = True
	data = [ [], [] ]
	index = 0
	root.after(10,update)

def update():					# Called periodically by the Tk toolkit
	global running, NP, imin, imax, history, data, index, trial
	if running == False:
		return
	di = (imax-imin)/(NP-1)
	i = imin + di*index
	v = ph.set_current(i)
	v = ph.set_current(i)
	if v != None:
		data[0].append(v)
		data[1].append(i)
	if i > imax or v > vmax or v == None:
		running = False
		history.append(data)
		trial += 1
		g.delete_lines()
		for k in range(len(history)):
			g.line(history[k][0], history[k][1], k)
		x = numpy.array(data[0])
		y = numpy.array(data[1])
		xbar = numpy.mean(x)
		ybar = numpy.mean(y)
		b = numpy.sum(y*(x-xbar)) / numpy.sum(x*(x-xbar))
		a = ybar - xbar * b
		msg.config(text = _('Linear Fitting of VI curve gave R = %5.0f Ohm')%(1000.0/b))
		s = _('R = %5.0f Ohm')%(1000.0/b)
		R.config(text = s)
		return

	if index > 1:			# Draw the line
		g.delete_lines()
		g.line(data[0], data[1], trial)
	index += 1
	root.after(TIMER, update)

def xmgrace():		# Send the data to Xmgrace
	global history
	try:
		import pygrace
	except:
		return
        global pg
	pg = pygrace.grace()
	for dat in history:
		pg.plot(dat[0],dat[1])
		pg.hold(1)			# Do not erase the old data
	pg.xlabel(_('Volts'))
	pg.ylabel(_('mA'))
	pg.title(_('Resistor VI curve'))

def save():
	global history, running
	if running == True:
		return
	s = e1.get()
	if s == '':
		return
	f = open(s, 'w')
	for dat in history:
		for k in range(len(dat[0])):
			f.write('%5.3f  %5.3f\n'%(dat[0][k], dat[1][k]))
		f.write('\n')
	f.close()
	msg.config(text = _('Data saved to file ')+s)

def clear():
	global history, trial, running
	if running == True:
		return
	g.delete_lines()
	history = []
	trial = 0

def quit():
	sys.exit()


ph = eyes.open()
ph.loadall_calib()
root = Tk()
Canvas(root, width = WIDTH, height = 5).pack(side=TOP)  # Some space at the top
g = eyeplot.graph(root, width=WIDTH, height=HEIGHT)	# make plot objects using draw.disp
g.setWorld(0, 0, vmax, imax,_('V'),_('mA'))

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)

b1 = Button(cf, text = _('START'), command = start)
b1.pack(side = LEFT, anchor = N)
b3 = Button(cf, text = _('SAVE to'), command = save)
b3.pack(side = LEFT, anchor = N)
filename = StringVar()
e1 =Entry(cf, width=15, bg = 'white', textvariable = filename)
filename.set('resistor_iv.dat')
e1.pack(side = LEFT)
R = Label(cf,text=_('R = '))
R.pack(side=LEFT)
b5 = Button(cf, text = _('QUIT'), command = quit)
b5.pack(side = RIGHT, anchor = N)
b4 = Button(cf, text = _('CLEAR'), command = clear)
b4.pack(side = RIGHT, anchor = N)
b5 = Button(cf, text = _('Grace'), command = xmgrace)
b5.pack(side = RIGHT, anchor = N)

mf = Frame(root, width = WIDTH, height = 10)
mf.pack(side=TOP,  fill = BOTH, expand = 1)
msg = Label(mf,text=_('Message'), fg = 'blue')
msg.pack(side=LEFT)

eyeplot.pop_image('pics/res-measure.png', _('Resistor IV char. Connections'))
root.title(_('EYES: Resistor IV characteristics'))
root.mainloop()

