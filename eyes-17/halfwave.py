'''
expEYES Junior CRO+ program
Author  : Ajith Kumar B.P, bpajith@gmail.com
License : GNU GPL version 3
Date : Apr-2012
'''

import gettext
gettext.bindtextdomain("expeyes")
gettext.textdomain('expeyes')
_ = gettext.gettext

import expeyes.eyes17 as eyes, expeyes.eyeplot17 as eyeplot, expeyes.eyemath17 as eyemath, numpy as np
import time, os, sys, math
VER = sys.version[0]
if VER == '3':
	from tkinter import *
else:
	from Tkinter import *

bgcol = 'ivory'

BUFSIZE = 1800		# uC buffer size in bytes
TIMER = 100
LPWIDTH = 75
WIDTH  = 600   		# width of drawing canvas
HEIGHT = 400   		# height 
VPERDIV = 1.0		# Volts per division, vertical scale
NP = 400			# Number of samples
NC = 1				# Number of channels
MINDEL = 2	
delay = MINDEL		# Time interval between samples
CMERR = False
data = [ [[],[]],[[],[]],[[],[]] ]  # 3 [t,v] lists
timeScales = [0.100, 0.200, 0.500, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0,100.0]

def msg(s, col='blue'):
	msgwin.config(text=s, fg=col)

AWGMIN = 2
AWGMAX = 5000
AWGval = 150

def set_frequency(w):
	global NP, delay
	AWGval = float(Wfreq.get())
	if AWGMIN <= AWGval <= AWGMAX:
		FREQ = p.set_sine(AWGval)
	else:
		return
		
	T = 1.e3/FREQ     # time, in msec, for 1 cycle

	for k in range(len(timeScales)):
		if timeScales[k] >= T/5:
			break
	timebase.set(k)

def set_timebase(w):
	global delay, NP, NC, VPERDIV, chan4, timeScales
	msperdiv = timeScales[int(timebase.get())]
	totalusec = int(msperdiv * 1000 * 10)
	if totalusec == 1000:
		NP = 250
		delay = NC
	else:
		NP = 400
		delay = (totalusec/NP)

	if delay < MINDEL:
		delay = MINDEL
	elif delay > 1000:
		delay = 1000

	totalmsec = round(0.001 * NP * NC *delay)
	tms = int(totalmsec)
	NP = tms * 1000/delay
	if NP%2 == 1 : NP += 1		# Must be an even number, for fitting
	if NP > 500: NP = 500
	g.setWorld(0,-5*VPERDIV, NP * delay * 0.001, 5*VPERDIV,_('mS'),_('V'))
	msg(_('X-scale changed to %d mS/div.Capturing %d samples with %d usec spacing') %(msperdiv,NP,delay))

def rmsval(x):
	return np.sqrt(np.mean(x**2))
	
def update():
	global delay, NP, delay, VPERDIV,data, CMERR, Freq
	if CMERR == True:
		CMERR = False 
		msg('')
	try:
		data[0][0], data[0][1], data[1][0], data[1][1] = p.capture2(NP,delay)
		data[2][0] = data[0][0]
		data[2][1] = np.zeros(NP)
		data[2][1] = data[0][1] - data[1][1]

		g.delete_lines()
		g.line(data[0][0], data[0][1],0)
		g.line(data[1][0], data[1][1],1)
		#g.line(data[1][0], data[0][1]-data[1][1],2)
	except:
		msg(_('Capture Error. Check input voltage levels.'),'red')
		CMERR = True
	
	root.after(10,update)

def set_vertical(w):
	global delay, NP, NC, VPERDIV
	divs = [5.0, 1.0, 0.5, 0.2]
	VPERDIV = divs[int(Vpd.get())]
	g.setWorld(0,-5*VPERDIV, NP * delay * 0.001, 5*VPERDIV,_('mS'),_('V'))

def save_data():	
	global data
	fn = Fname.get()
	p.save(data,fn)
	msg(_('Traces saved to %s') %fn)

def xmgrace():
	global data
	if eyeplot.grace(data) == False:
		msg(_('Could not find Xmgrace or Pygrace. Install them'),'red')
	else:
		msg(_('Traces send to Xmgrace'))

	
		
#=============================== main program starts here ===================================
p = eyes.open()
if p == None: sys.exit()
p.set_sine(AWGval)
p.select_range('A1', 4)
p.select_range('A2', 4)
p.configure_trigger(0, 'A1', 0.0)

root = Tk()    
f = Frame(root)
f.pack(side=LEFT)

g = eyeplot.graph(f, width=WIDTH, height=HEIGHT)	# make plot objects using draw.disp
g.setWorld(0, -5, 20, 5,_('mS'),_('V'))

f1 = Frame(f)
f1.pack(side=TOP,  fill = BOTH, expand = 1)

Label(f1,text = _('Frequency')).pack(side=LEFT)
Wfreq = Entry(f1, width = 5)
Wfreq.pack(side=LEFT) 
Wfreq.bind("<Return>",set_frequency)
Wfreq.delete(0,END)
Wfreq.insert(0,str(AWGval))

Label(f1,text = _('Hz  ')).pack(side=LEFT)

Label(f1,text = _('Timebase')).pack(side=LEFT, anchor = SW)		# Sliders for Adjusting Axes
timebase = Scale(f1,command = set_timebase, orient=HORIZONTAL, length=LPWIDTH, showvalue=False,\
	from_ = 0, to=9, resolution=1)
timebase.pack(side=LEFT, anchor = SW)
timebase.set(5)
Label(f1,text = _('mSec/div')).pack(side=LEFT, anchor = SW)		# Sliders for Adjusting Axes

Save = Button(f1,text=_('Save Traces to'), command = save_data)
Save.pack(side=LEFT, anchor=N)
Fname = Entry(f1, width=8)
Fname.pack(side=LEFT)
Fname.insert(0,'halfwave.txt')

Save = Button(f1,text=_('XmGrace'), command = xmgrace)
Save.pack(side=LEFT, anchor=N)
Quit = Button(f1,text=_('QUIT'), command = sys.exit)
Quit.pack(side=LEFT, anchor=N)

mf = Frame(f)
mf.pack(side=TOP,  fill = BOTH, expand = 1)
msgwin = Label(mf,text = _('Connect WG to A1, Diode from A1 to A2.'), fg = 'blue')
msgwin.pack(side=LEFT)#, anchor = SW)

set_frequency(1)
t = _('Halfwave Rectifier')
eyeplot.pop_help('halfwave', t)
root.title(t)
root.after(TIMER,update)
root.mainloop()


