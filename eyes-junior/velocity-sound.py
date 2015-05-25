'''
expEYES program
Author  : Ajith Kumar B.P, bpajith@gmail.com
License : GNU GPL version 3
'''
import gettext
gettext.bindtextdomain("expeyes")
gettext.textdomain('expeyes')
_ = gettext.gettext

import time, math, sys
if sys.version_info.major==3:
        from tkinter import *
else:
        from Tkinter import *

sys.path=[".."] + sys.path

import expeyes.eyesj as eyes
import expeyes.eyeplot as eyeplot
import expeyes.eyemath as eyemath

TIMER = 100
WIDTH  = 800        # width of drawing canvas
HEIGHT = 400        # height 
delay = 10		    # Time interval between samples
NP = 400			# Number of samples
data = [] 		    # Of the form, [ [x1,y1], [x2,y2],....] where x and y are vectors
outmask = 1

def fset(f):
	s = '%5.1f'%f
	Freq.delete(0,END)
	Freq.insert(0,s)

def measure_phase():
	global data, NP, delay
	data = []
	phsum = 0.0
	n = 0
	try:
		fr = float(Freq.get())
		fs = p.set_sqr1(fr)
	except:
		msgwin.config(text=_('Invalid Frequency'))
		return	
	p.enable_wait_rising(6)
	for k in range(5):
		t,v = p.capture_hr(1,NP,delay)
		fa = eyemath.fit_sine(t, v)
		if fa != None:
			phsum += fa[1][2]
			n += 1
		else:
			msgwin.config(text=_('No Signal'))
	p.set_sqr1(-1)
	if n < 1:
		msgwin.config(text=_('Measurement failed'))
		return

	phase = phsum/n * (180.0/math.pi)
	#print n,phase	
	s = _('Freq = %5.0f Hz Phase = %5.0f deg')%(fs, phase)
	msgwin.config(text=s)			
	data.append([t,v])
	g.delete_lines()
	g.line(t,v)
	p.disable_actions()

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
	p.grace(data, _('milliSeconds'), _('Volts'))

def quit():
	sys.exit()

p = eyes.open()
p.set_sqr1(0)

root = Tk()
Canvas(root, width = WIDTH, height = 5).pack(side=TOP)  # Some space at the top
g = eyeplot.graph(root, width=WIDTH, height=HEIGHT)	# make plot objects using draw.disp
g.setWorld(0,-5, NP * delay * 0.001, 5,_('mS'),_('V'))

if p == None:
	g.text(0, 0,_('EYES Junior Hardware Not Found. Check Connections and restart the program'),1)
	root.mainloop()
	sys.exit()

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)

b1 = Button(cf,text =_('Measure Phase'), command = measure_phase, fg = 'blue')
b1.pack(side=LEFT, anchor = SW)

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
b = Button(cf,text =_('QUIT'), command=quit)
b.pack(side=RIGHT, anchor = SW)


mf = Frame(root)				# Message Frame below command frame.
mf.pack(side=TOP, anchor = SW)
msgwin = Label(mf,text = _('Messages'), fg = 'blue')
msgwin.pack(side=LEFT, anchor = SW)

eyeplot.pop_image('pics/sound.png', _('Velocity of Sound'))
root.title(_('EYES Junior: Velocity of Sound'))
root.mainloop()

