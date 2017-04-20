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
WIDTH  = 800        # width of drawing canvas
HEIGHT = 400        # height 
delay = 5		    # Time interval between samples
NP = 500			# Number of samples
data = [] 		    # Of the form, [ [x1,y1], [x2,y2],....] where x and y are vectors
outmask = 1
CMERR = False

def msg(s, col='blue'):
	msgwin.config(text=s, fg=col)
	

def scope_mode():
	if Looping.get() == 1:
		f = float(Freq.get())
		if 100 < f < 4500:
			p.set_sine(f)
		update()
	else:
		p.set_sine(10)


def update():
	global delay, NP, delay, VPERDIV,data, CMERR, Freq
	if Looping.get() == 0:
		return
	if CMERR == True:
		CMERR = False 
		msg('')
	try:
		t1,v1,t2,v2,t3,v3,t4,v4 = p.capture4(NP,delay)
		g.delete_lines()
		g.line(t1,v1,0)
		g.line(t4,v4,3)

		# fitting
		fa = eyemath.fit_sine(t1,v1)
		fb = eyemath.fit_sine(t4,v4)
		if fa != None and fb != None:
			s = 'Frequency = %5f Hz. Phase Difference= %5.1f Deg'%(fa[1][1]*1000, (fa[1][2]-fb[1][2])*180/math.pi)
			msg(_(s))
		else:
			msg(_('Curve Fitfing failed. Try changing Timebase'))
	except:
		msg(_('Capture Error. Check input voltage levels.'),'red')
		CMERR = True
	
	root.after(10,update)


def do_fft():
	global data, delay, NP
	if data == []: return
	fr,tr = eyemath.fft(data[0][1], delay * 0.001)
	p.save([ [fr,tr] ], 'FFT.dat')
	p.grace([ [fr,tr] ], _('freq'), _('power'))
	msgwin.config(text = _('Fourier transform Saved to FFT.dat.'))

def save():
	global data
	s = fn.get()
	if s == '':
		return
	p.save(data, s)
	msgwin.config(text = _('Data saved to file ')+s)

def xmgrace():		# Send the data to Xmgrace
	global data
	eyeplot.grace(data, _('milliSeconds'), _('Volts'))

def quit():
	sys.exit()

p = eyes.open()
if p == None:
	g.text(0, 0,_('EYES Junior Hardware Not Found. Check Connections and restart the program'),1)
	root.mainloop()
	sys.exit()
p.set_sine(10)

root = Tk()
Canvas(root, width = WIDTH, height = 5).pack(side=TOP)  # Some space at the top
g = eyeplot.graph(root, width=WIDTH, height=HEIGHT)	# make plot objects using draw.disp
g.setWorld(0,-5, NP * delay * 0.001, 5,_('mS'),_('V'))

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)

l = Label(cf,text=_('Freq='))
l.pack(side=LEFT, anchor= SW)
Freq = Entry(cf,width = 10, bg = 'white')
Freq.pack(side=LEFT, anchor = SW)
Freq.insert(END,'3500')

b = Button(cf,text =_('Xmgrace'), command=xmgrace)
b.pack(side=LEFT, anchor = SW)

b = Button(cf,text =_('FFT'), command=do_fft)
b.pack(side=LEFT, anchor = SW)

b = Button(cf,text =_('Save to'), command=save)
b.pack(side=LEFT, anchor = SW)
fn = Entry(cf,width = 10, bg = 'white')
fn.pack(side=LEFT, anchor = SW)
fn.insert(END,'sound.dat')

Looping = IntVar()
Loop = Checkbutton(cf, text=_('Enable Measurement'), variable = Looping, command = scope_mode)
Loop.pack(side=LEFT, anchor = SW)
Looping.set('0')

b = Button(cf,text =_('QUIT'), command=quit)
b.pack(side=RIGHT, anchor = SW)


mf = Frame(root)				# Message Frame below command frame.
mf.pack(side=TOP, anchor = SW)
msgwin = Label(mf,text = _('Messages'), fg = 'blue')
msgwin.pack(side=LEFT, anchor = SW)

t = _('Velocity of Sound')
eyeplot.pop_help('sound-velocity', t)
root.title(t)
root.after(10,update)
root.mainloop()

