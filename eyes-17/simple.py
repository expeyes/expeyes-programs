'''
expEYES-17  simple experiments
Author  : Ajith Kumar B.P, bpajith@gmail.com
License : GNU GPL version 3
Date : Nov-2016
'''

import gettext, sys
gettext.bindtextdomain("expeyes")
gettext.textdomain('expeyes')
_ = gettext.gettext

VER = sys.version[0]
if VER == '3':
	from tkinter import *
else:
	from Tkinter import *
import expeyes.eyes17 as eyes, time, os,sys
import numpy as np


p=eyes.open()
TIMER = 500


def msg(s, col='blue'):
	msgwin.config(text=s, fg=col)


def abs_path():		   # Returns the absolute path of the python program
	name = sys.argv[0]
	dirname = os.path.dirname(name)
	if dirname != '':
		return os.path.dirname(name) + os.sep 
	else:
		return '.' + os.sep


def control_od1():
	state = int(Od1.get())
	p.set_state(OD1=state)

def control_ccs():
	state = int(Ccs.get())
	p.set_state(CCS=state)



SQ2MIN = SQ1MIN = 1
SQ2MAX = SQ1MAX = 5000
PV1MIN = -5.0
PV1MAX = 5.0
PV2MIN = -3.3
PV2MAX = 3.3
AWGMIN = 5
AWGMAX = 5000
AWGval = 150
Waves = ['sine', 'tria', 'SQR2']
Wgains = ['100 mV', '1 V', '3 V']
waveindex = 0
wgainindex = 2

def set_sqr1(w):
	if p == None: return
	fr = SQ1scale.get()
	fs = p.set_sqr1(fr)       
	ss= '%5.1f Hz'%(fs)
	SQ1val.config(text=_(ss))
	

def set_pv1(w):
	if p == None: return
	pos = PV1scale.get()
	vs = (pos-5000)*10.0/10000
	res = p.set_pv1(vs)
	ss= '%5.3f V'%(res)
	PV1val.config(text=_(ss))
	

def set_pv2(w):
	if p == None: return
	pos = PV2scale.get()
	vs = (pos-3300)*6.6/6600
	res = p.set_pv2(vs)
	ss= '%5.3f V'%(res)
	PV2val.config(text=_(ss))

	

def set_awg(w):
	AWGval = Wscale.get()
	fs = p.set_wave(AWGval, Waves[waveindex])
	ss= '%5.1f Hz'%(fs)
	WGval.config(text=_(ss))
	

def pop_Wavemenu(event):
	poped = True
	menuWG.post(WGsel.winfo_rootx(),WGsel.winfo_rooty()) 

def select_wave(index):
	global waveindex
	WGsel.config(text=  Waves[index])
	waveindex = index
	set_wave()

def pop_Wgainmenu(event):
	poped = True
	menuWGgain.post(WGgainsel.winfo_rootx(),WGgainsel.winfo_rooty()) 

def select_wgain(index):
	global wgainindex
	WGgainsel.config(text=  Wgains[index])
	wgainindex = index
	p.set_sine_amp(index)


def update():
	try:
		v = p.get_voltage('A1')
		if v == v:   #is it NaN
			A1.config(text=_('%5.3f'%(v)))
		else:
			print 'A1 nan'
			
		v = p.get_voltage('A2')
		if v == v:   #is it NaN
			A2.config(text=_('%5.3f'%(v)))
		else:
			print 'A2 nan'
		
		v = p.get_voltage('A3')
		if v == v:   #is it NaN
			A3.config(text=_('%5.3f'%(v)))
		else:
			print 'A3 nan'
	except:
		msg(_('Voltage Read Error.'),'red')
	root.after(TIMER,update)


def measure_cap():
	cap = p.get_capacitance()
	if cap == None:
		msg(_('Error'))
		return

	if cap <= 1000e-12:
		ss= '%5.0f pF'%(cap*1e12)
	elif cap <= 1000e-9:
		ss= '%5.0f nF'%(cap*1e9)
	elif cap <= 1000e-6:
		ss= '%5.0f uF'%(cap*1e6)
	IN1.config(text=_(ss))
		
def measure_res():
	vsen = p.get_voltage('SEN')
	if 0.1 < vsen < 3.2:
		i = (3.3 - vsen)/ 5100.0
		res = vsen / i
		ss= '%5.0f Ohm'%(res)
		SEN.config(text=_(ss))
	else:
		msg(_('Resistance on SEN not within limits '))


def measure_freq():
	fr = p.get_freq()
	ss= '%5.1f Hz'%(fr)
	IN2.config(text=_(ss))
		

#=============================== main program starts here ===================================
WIDTH = 600
HEIGHT = 250

root = Tk()    
root.option_add( "*font", "Helvetica 12" ) 

top = Frame(root, width = WIDTH, height = 150)
top.pack(side=TOP,  fill = BOTH, expand = 1)
top.pack_propagate(0)

# Read and display the introductory help
dname = os.path.dirname(sys.argv[0])
fn = os.path.join(dname, 'help','intro.txt')
f = open(fn, 'r')
s = f.read()
L = Label(top,text = _(s),font=("Helvetica", 12), bg='white', padx = 5)
L.pack(side=TOP,  fill = BOTH, expand = 1)

#========================= Bottom panel ===========================================
DATAW =  80
FSIZE = 12
bot = Frame(root)
bot.pack(side=TOP,  fill = BOTH, expand = 1)

f = Frame(bot)
f.pack(side=TOP, anchor=NW)
f.columnconfigure(2, minsize=DATAW)
f.columnconfigure(5, minsize=DATAW)
f.columnconfigure(8, minsize=DATAW)
Label(f,text=_('Voltage at A1 = '), font=("Helvetica", FSIZE)).grid(row=1, column=1,sticky=E+W)
Label(f,text=_('Voltage at A2 = '), font=("Helvetica", FSIZE)).grid(row=1, column=4,sticky=E+W)
Label(f,text=_('Voltage at A3 = '), font=("Helvetica", FSIZE)).grid(row=1, column=7,sticky=E+W)
A1 = Label(f,text='', font=("Helvetica", FSIZE), fg = 'blue')
A1.grid(row=1, column=2,sticky=E+W)
A2 = Label(f,text='', font=("Helvetica", FSIZE), fg = 'blue')
A2.grid(row=1, column=5,sticky=E+W)
A3 = Label(f,text='', font=("Helvetica", FSIZE), fg = 'blue')
A3.grid(row=1, column=8,sticky=E+W)
Label(f,text=_(' V  '), font=("Helvetica", FSIZE)).grid(row=1, column=3,sticky=E+W)
Label(f,text=_(' V  '), font=("Helvetica", FSIZE)).grid(row=1, column=6,sticky=E+W)
Label(f,text=_(' V  '), font=("Helvetica", FSIZE)).grid(row=1, column=9,sticky=E+W)


SLIDER = 100
f = Frame(bot)
f.pack(side=TOP, anchor = SW)
f.columnconfigure(3, minsize=DATAW)
f.columnconfigure(6, minsize=DATAW)
Label(f,text = _('WG Frequency')).grid(row=1, column=1)  
Wscale = Scale(f,command = set_awg, orient=HORIZONTAL, length=SLIDER, showvalue=False, from_ = 0, to=AWGMAX, resolution=1)
Wscale.grid(row=1, column=2) 
Wscale.set(1000)
WGval = Label(f,text = _('Hz'))
WGval.grid(row=1, column=3)

Label(f,text = _('SQ1 Frequency')).grid(row=1, column=4) 
SQ1scale = Scale(f,command = set_sqr1, orient=HORIZONTAL, length=SLIDER, showvalue=False, from_ = 0, to=SQ1MAX, resolution=1)
SQ1scale.grid(row=1, column=5) 
SQ1scale.set(1000)
SQ1val = Label(f,text = _('Hz'))
SQ1val.grid(row=1, column=6) 

Label(f,text = _('Voltage at PV1')).grid(row=2, column=1) 
PV1scale = Scale(f,command = set_pv1, orient=HORIZONTAL, length=SLIDER, showvalue=False, from_ = 0, to=10000, resolution=1)
PV1scale.grid(row=2, column=2) 
PV1scale.set(5000)
PV1val = Label(f,text = _('V'))
PV1val.grid(row=2, column=3) 

Label(f,text = _('Voltage at PV2')).grid(row=2, column=4) 
PV2scale = Scale(f,command = set_pv2, orient=HORIZONTAL, length=SLIDER, showvalue=False, from_ = 0, to=6600, resolution=1)
PV2scale.grid(row=2, column=5) 
PV2scale.set(3300)
PV2val = Label(f,text = _('V'))
PV2val.grid(row=2, column=6) 

f = Frame(bot)
f.pack(side=TOP, anchor=NW)
f.columnconfigure(2, minsize=DATAW)
f.columnconfigure(4, minsize=DATAW)
f.columnconfigure(6, minsize=DATAW)
Button(f,text=_('Capacitance on IN1'), command=measure_cap).grid(row=1, column=1,sticky=E+W)
Button(f,text=_('Frequency on IN2'), command=measure_freq).grid(row=1, column=3,sticky=E+W)
Button(f,text=_('Resistance on SEN'), command=measure_res).grid(row=1, column=5,sticky=E+W)
IN1 = Label(f,text=_('     '), font=("Helvetica", FSIZE))
IN1.grid(row=1, column=2,sticky=E+W)
IN2 = Label(f,text=_('     '), font=("Helvetica", FSIZE))
IN2.grid(row=1, column=4,sticky=E+W)
SEN = Label(f,text=_('     '), font=("Helvetica", FSIZE))
SEN.grid(row=1, column=6,sticky=E+W)


f = Frame(bot)
f.pack(side=TOP, anchor=NW)
Od1 = IntVar()
Ccs = IntVar()
Checkbutton(f,text = 'Enable OD1', variable = Od1, command = control_od1).grid(row=1, column=1,sticky=E+W)
Checkbutton(f,text = 'Enable CCS', variable = Ccs, command = control_ccs).grid(row=1, column=2,sticky=E+W)
Label(f,text = _('           ')).grid(row=1, column=3,sticky=E+W)
Quit = Button(f,text=_('QUIT'), command = sys.exit).grid(row=1, column=4,sticky=E+W)

mf = Frame(root, bg=_('white'))
mf.pack(side=TOP,  fill = BOTH, expand = 1)
msgwin = Label(mf,text = '', justify=CENTER, bg = _('white'), fg = _('blue'),font=(_('Helvetica'), 12))
msgwin.pack(side=LEFT, anchor = CENTER)

root.title(_('Simple activities with EYES17'))
root.after(TIMER,update)
root.mainloop()
