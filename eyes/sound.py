'''
expEYES program
Author  : Ajith Kumar B.P, bpajith@gmail.com
License : GNU GPL version 3
'''
import gettext
gettext.bindtextdomain("expeyes")
gettext.textdomain('expeyes')
_ = gettext.gettext

from tkinter import *
import expeyes.eyes as eyes, expeyes.eyeplot as eyeplot, expeyes.eyemath as eyemath, time, math, sys

TIMER = 100
WIDTH  = 800   # width of drawing canvas
HEIGHT = 400   # height 
delay = 10			# Time interval between samples
NP = 1000			# Number of samples
data = [ [], [] ]
outmask = 1
looping = False

def capture():
	global data, outmask, looping, NP, delay
	if looping == True: 
		msgwin.config(text = _('Already Running'))
		return
	p.write_outputs(outmask)
	time.sleep(0.5)
	t, v = p.capture(0,NP,delay)
	p.write_outputs(0)
	g.delete_lines()
	g.line(t,v)
	data = t,v
	fa = eyemath.fit_sine(t,v)
	if fa != None:
		rms = p.rms(v)
		pa = fa[1]
		s = _('CH0 : %5.1f V , %5.1f Hz ') %(rms, pa[1]*1000)
		msgwin.config(text = s)

def update():
	global data, looping
	if looping == False:
		return
	t, v = p.capture(0,NP,delay)
	g.delete_lines()
	g.line(t,v)
	data = t,v
	root.after(TIMER, update)	

def start():
	global outmask, looping
	outmask = 0
	if M1.get() == 1:
		outmask |= 1
	if M2.get() == 1:
		outmask |= 2
	p.write_outputs(outmask)

	if LOOP.get() == 1:
		if looping == False:
			root.after(TIMER, update)
			looping = True	
	else:
		p.write_outputs(0)
		looping = False

def do_fft():
	global data, delay, NP
	if data == [ [], [] ]: return
	fr,tr = eyemath.fft(data[1], delay * 0.001)
	p.save([ [fr,tr] ], 'FFT.dat')
	p.grace([ [fr,tr] ], _('freq'), _('power'))
	msgwin.config(text = _('Fourier transform Saved to FFT.dat.'))

def save():
	global data
	s = fn.get()
	if s == '':
		return
	p.save([data], s)
	msgwin.config(text = _('Data saved to file ')+s)

def xmgrace():		# Send the data to Xmgrace
	global data
	p.grace([data], _('milliSeconds'), _('Volts'))

def quit():
	p.write_outputs(0)
	sys.exit()

p = eyes.open()
p.loadall_calib()
root = Tk()
Canvas(root, width = WIDTH, height = 5).pack(side=TOP)  # Some space at the top
g = eyeplot.graph(root, width=WIDTH, height=HEIGHT)	# make plot objects using draw.disp
g.setWorld(0,-5, NP * delay * 0.001, 5,_('mS'),_('V'))

if p == None:
	g.text(0, 0,_('EYES Hardware Not Found. Check Connections and restart the program'),1)
	root.mainloop()
	sys.exit()
p.set_voltage(1,5)

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)

M1 = IntVar()
cb1 = Checkbutton(cf,text =_('Buzzer1'), command = start,variable=M1, fg = 'red')
cb1.pack(side=LEFT, anchor = SW)
M1.set(1)
M2 = IntVar()
cb1 = Checkbutton(cf,text =_('Buzzer2'), command = start, variable=M2, fg = 'red')
cb1.pack(side=LEFT, anchor = SW)
M2.set(0)

b = Button(cf,text =_('Capture'), command=capture)
b.pack(side=LEFT, anchor = SW)
LOOP = IntVar()
cb1 = Checkbutton(cf,text =_('FreeRUN'), command = start, variable=LOOP, fg = 'red')
cb1.pack(side=LEFT, anchor = SW)
LOOP.set(0)

b = Button(cf,text =_('Save to'), command=save)
b.pack(side=LEFT, anchor = SW)
fn = Entry(cf,width = 10, bg = 'white')
fn.pack(side=LEFT, anchor = SW)
fn.insert(END,'cap.dat')
b = Button(cf,text =_('QUIT'), command=quit)
b.pack(side=RIGHT, anchor = SW)
b = Button(cf,text =_('Xmgrace'), command=xmgrace)
b.pack(side=RIGHT, anchor = SW)
b = Button(cf,text =_('FFT'), command=do_fft)
b.pack(side=LEFT, anchor = SW)


mf = Frame(root)				# Message Frame below command frame.
mf.pack(side=TOP, anchor = SW)
msgwin = Label(mf,text = _('Messages'), fg = 'blue')
msgwin.pack(side=LEFT, anchor = SW)
root.title(_('EYES: Sound Experiments'))
root.mainloop()

