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

from Tkinter import *
import expeyes.eyes17 as eyes, expeyes.eyeplot17 as eyeplot, expeyes.eyemath17 as eyemath, numpy as np
import time, os, commands, math

bgcol = 'ivory'

BUFSIZE = 1800		# uC buffer size in bytes
TIMER = 100
LPWIDTH = 75
WIDTH  = 600   		# width of drawing canvas
HEIGHT = 400   		# height 
VPERDIV = 1.0		# Volts per division, vertical scale
NP = 400			# Number of samples
delay = 50			# Time interval between samples
CMERR = False
data = [ [[],[]],[[],[]]]  # 2 [t,v] lists


def msg(s, col='blue'):
	msgwin.config(text=s, fg=col)

def set_level(w):
	val = float(Wpv1.get())
	p.set_pv1(val)
	
def update():
	global NP, delay, data, CMERR
	if CMERR == True:
		CMERR = False 
		msg('')
	try:
		data[0][0], data[0][1], data[1][0], data[1][1] = p.capture2(NP,delay)
		g.delete_lines()
		g.line(data[0][0], data[0][1],0)
		g.line(data[1][0], data[1][1],1)
	except:
		msg(_('Capture Error. Check input voltage levels.'),'red')
		CMERR = True
	
	root.after(10,update)


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
p.set_sine(200)
p.select_range('A1', 16)
p.select_range('A2', 16)
p.configure_trigger(0, 'A1', 0.0)

root = Tk()    
f = Frame(root)
f.pack(side=LEFT)

g = eyeplot.graph(f, width=WIDTH, height=HEIGHT)	# make plot objects using draw.disp
g.setWorld(0, -10, 20, 10,_('mS'),_('V'))

f1 = Frame(f)
f1.pack(side=TOP,  fill = BOTH, expand = 1)

Label(f1,text = _('PV1=')).pack(side=LEFT)
Wpv1 = Entry(f1, width = 5)
Wpv1.pack(side=LEFT) 
Wpv1.bind("<Return>",set_level)
Wpv1.delete(0,END)
Wpv1.insert(0,str(1.0))
Label(f1,text = _('V ')).pack(side=LEFT)

Save = Button(f1,text=_('Save Traces to'), command = save_data)
Save.pack(side=LEFT, anchor=N)
Fname = Entry(f1, width=12)
Fname.pack(side=LEFT)
Fname.insert(0,'clamping.txt')

Save = Button(f1,text=_('XmGrace'), command = xmgrace)
Save.pack(side=LEFT, anchor=N)
Quit = Button(f1,text=_('QUIT'), command = sys.exit)
Quit.pack(side=LEFT, anchor=N)

mf = Frame(f)
mf.pack(side=TOP,  fill = BOTH, expand = 1)
msgwin = Label(mf,text = _(''), fg = 'blue')
msgwin.pack(side=LEFT)#, anchor = SW)

eyeplot.pop_image('pics/clamping.png', _('Diode Clamping'))
root.title(_('Diode Clamping'))
root.after(10,update)
root.mainloop()


