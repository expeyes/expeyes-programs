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

TIMER = 10
WIDTH  = 800        # width of drawing canvas
HEIGHT = 400        # height 
delay = 50		    # Time interval between samples
NP = 500			# Number of samples
data = [] 		    # Of the form, [ [x1,y1], [x2,y2],....] where x and y are vectors
outmask = 1
looping = False


def update():
	global data, looping, NP, delay
	if looping == False:
		return
	data = []
	if NP <= 900:
		t,v = p.capture_hr(1,NP,delay)
	else:
		t,v = p.capture(1,NP,delay)
	g.delete_lines()
	g.line(t,v)
	data.append([t,v])
	fa = eyemath.fit_sine(t, v)
	if fa != None:
		#g.line(t,fa[0], 8)
		rms = p.rms(v)
		f0 = fa[1][1] * 1000
		s = _('Freq = %5.0f Hz')%(fa[1][1]*1000)
	else:
		s = _('No Signal')
	msgwin.config(text=s)			# CRO part over	
	root.after(TIMER, update)	

def start():
	global looping, NP, delay
	if looping == True:
		return
	p.disable_actions()
	ns = int(Nsam.get())
	if 100 <= ns <=1800:			# Number of samples
		NP = ns
		g.setWorld(0,-5, NP * delay * 0.001, 5,_('mS'),_('V'))
	if A0.get() == 1:
		f = float(Freq0.get())
		fr = p.set_sqr1(f)
		Freq0.delete(0,END)
		Freq0.insert(0,'%5.1f'%fr)
	else:
		p.set_sqr1(-1)
	if A1.get() == 1:
		f = float(Freq.get())
		fr = p.set_sqr2(f)
		Freq.delete(0,END)
		Freq.insert(0,'%5.1f'%fr)
	else:
		p.set_sqr2(-1)
	looping = True
	root.after(TIMER, update)

def stop():
	global looping
	looping = False
	p.set_sqr1(-1)
	p.set_sqr2(-1)

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
	g.text(0, 0,_('EYES Hardware Not Found. Check Connections and restart the program'),1)
	root.mainloop()
	sys.exit()

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)

l = Label(cf,text='NS =')
l.pack(side=LEFT, anchor=SW)
Nsam = Entry(cf,width = 4, bg = 'white')
Nsam.pack(side=LEFT, anchor = SW)
Nsam.insert(END,'400')

A0 = IntVar()
cb1 = Checkbutton(cf,text =_('SQR1='), variable=A0, fg = 'blue')
cb1.pack(side=LEFT, anchor = SW)
A0.set(0)

Freq0 = Entry(cf,width = 10, bg = 'white')
Freq0.pack(side=LEFT, anchor = SW)
Freq0.insert(END,'3500')

A1 = IntVar()
cb1 = Checkbutton(cf,text =_('SQR2='), variable=A1, fg = 'blue')
cb1.pack(side=LEFT, anchor = SW)
A1.set(0)
Freq = Entry(cf,width = 10, bg = 'white')
Freq.pack(side=LEFT, anchor = SW)
Freq.insert(END,'3600')

Start = Button(cf,text =_('START'), command = start, fg = 'blue')
Start.pack(side=LEFT, anchor = SW)
Stop = Button(cf,text =_('STOP'), command = stop, fg = 'blue')
Stop.pack(side=LEFT, anchor = SW)

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

eyeplot.pop_image('pics/sound-inter.png', _('Sound Interference'))
root.title(_('EYES: Interference of Sound'))
root.mainloop()

