'''
expEYES-17  Oscilloscope program
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
import expeyes.eyes17 as eyes, expeyes.eyeplot17 as eyeplot, expeyes.eyemath17 as eyemath, time, os
import numpy as np

p = None    # No hardware to start with

bgcol = 'ivory'
xlabel = 'milli Seconds'

BUFSIZE = 1800		# uC buffer size in bytes
TIMER = 100
WIDTH  = 500   		# width of drawing canvas  (make 550)
HEIGHT = 400   		# height 
VPERDIV = 1.0		# Volts per division, vertical scale
NP = 400			# Number of samples
NC = 1				# Number of channels
MINDEL = 1			# minimum time between samples, in usecs
MAXDEL = 1000
delay = MINDEL		# Time interval between samples
CMERR = False
TIMER = 100
loopCounter = 0

Ranges12 = ['16 V', '8 V','4 V', '2 V', '1 V', '.5V']	# Voltage ranges for A1 and A2
rangevals12 = [16,8,4,2.5,1,0.5]
Ranges34 = ['4 V', '2 V', '1 V', '.5V']					# Voltage ranges for A3 and MIC
rangevals34 = [4,2,1,0.5]

MAXCHAN = 4
chan4 = [ [1, [], [],0,[],0,0,0,None,None,0.0, 2],\
		  [0, [], [],0,[],0,0,0,None,None,0.0, 2],\
		  [0, [], [],0,[],0,0,0,None,None,0.0, 0],\
		  [0, [], [],0,[],0,0,0,None,None,0.0, 0] \
		] # Source, t, v, fitflag, vfit, amp, freq, phase, widget1, widget2, display offset in volts
CHSRC   = 0		# index of each item in the list above.
TDATA   = 1
VDATA   = 2
FITFLAG = 3
VFDAT   = 4
AMP     = 5
FREQ    = 6
PHASE   = 7
WINFO   = 8
WFIT    = 9
WFITOK  = 10
RANGE   = 11
sources = ['A1','A2','A3', 'MIC'] #, 'SEN', 'SQ1', 'SQ2', 'OD1', 'CCS']
#channels = ['CH1', 'CH2', 'CH3', 'CH4']
chancols = ['black', 'red', 'blue','magenta']


# Geometry of the left panel, selection of triggers  & channels
LPWIDTH  = 40
LPHEIGHT = 320
VSTEP = 25
VBORD = 10
#OFFSET   = VSTEP * len(sources)
SELSRC  = 1
SETACT  = 2
WAITACT = 3
SELCHAN = 4
NORMAL = 100		# Status of Display channel
FIT = 101			# Fit to Sinusoid
DEL = 102		    # Remove entry
FTR = 103			# Fourier transform
selection  = 0
seltag = ''		# selected tag


VAlabels = []
DY = HEIGHT / 8
labelYs = [7*DY, 6*DY, 5*DY, 3*DY, 2*DY, DY]

def connect():
	global p
	if p != None:   # Act only if not connected
		return
	p= eyes.open()
	if p == None:
		msg(_('expEYES-17 NOT found. Bad connection or another program using it'),'red')
	else:
		s = _('Scope17: on expEYES-17 hardware')
		root.title(s)
		msg(s)
		root.after(TIMER,update)

def draw_ylabels():
	global VAlabels
	for lab in VAlabels:		# remove old labels and re-initialize the list
		VAxes.delete(lab)
	VAlabels = []
	NC = 0
	cols = []
	rans = []
	for ch in range(4):
		if chan4[ch][CHSRC] != 0:
			cols.append(chancols[ch])
			if ch < 2:
				rans.append(rangevals12[chan4[ch][RANGE]])
			else:
				rans.append(rangevals34[chan4[ch][RANGE]])
			NC += 1
	
	if NC == 1:
		dy = 0.25 *rans[0] 
		for k in range(3):
			s = '%5.3f'%(-(3-k)*dy)
			t = VAxes.create_text(LPWIDTH, labelYs[k]-8, text = s, anchor=NE, font=("arial", 7),fill = cols[0])
			VAlabels.append(t)
		for k in range(3,6):
			s = '%5.3f'%((k-2)*dy)
			t = VAxes.create_text(LPWIDTH, labelYs[k]-8, text = s, anchor=NE, font=("arial", 7),fill = cols[0])
			VAlabels.append(t)
	elif NC == 2:
		dy = 0.25 *rans[0]
		for k in range(3):
			s = '%5.3f'%(-(3-k)*dy)
			t = VAxes.create_text(LPWIDTH, labelYs[k]-8-4, text = s, anchor=NE, font=("arial", 7),fill = cols[0])
			VAlabels.append(t)
		for k in range(3,6):
			s = '%5.3f'%((k-2)*dy)
			t = VAxes.create_text(LPWIDTH, labelYs[k]-8-4, text = s, anchor=NE, font=("arial", 7),fill = cols[0])
			VAlabels.append(t)
		dy = 0.25 *rans[1]
		for k in range(3):
			s = '%5.3f'%(-(3-k)*dy)
			t = VAxes.create_text(LPWIDTH, labelYs[k]-8+4, text = s, anchor=NE, font=("arial", 7),fill = cols[1])
			VAlabels.append(t)
		for k in range(3,6):
			s = '%5.3f'%((k-2)*dy)
			t = VAxes.create_text(LPWIDTH, labelYs[k]-8+4, text = s, anchor=NE, font=("arial", 7),fill = cols[1])
			VAlabels.append(t)
	elif NC == 3:
		dy = 0.25 *rans[0]
		for k in range(3):
			s = '%5.3f'%(-(3-k)*dy)
			t = VAxes.create_text(LPWIDTH, labelYs[k]-8-4-4, text = s, anchor=NE, font=("arial", 7),fill = cols[0])
			VAlabels.append(t)
		for k in range(3,6):
			s = '%5.3f'%((k-2)*dy)
			t = VAxes.create_text(LPWIDTH, labelYs[k]-8-4-4, text = s, anchor=NE, font=("arial", 7),fill = cols[0])
			VAlabels.append(t)
		dy = 0.25 *rans[1]
		for k in range(3):
			s = '%5.3f'%(-(3-k)*dy)
			t = VAxes.create_text(LPWIDTH, labelYs[k]-8, text = s, anchor=NE, font=("arial", 7),fill = cols[1])
			VAlabels.append(t)
		for k in range(3,6):
			s = '%5.3f'%((k-2)*dy)
			t = VAxes.create_text(LPWIDTH, labelYs[k]-8, text = s, anchor=NE, font=("arial", 7),fill = cols[1])
			VAlabels.append(t)
		dy = 0.25 *rans[2]
		for k in range(3):
			s = '%5.3f'%(-(3-k)*dy)
			t = VAxes.create_text(LPWIDTH, labelYs[k]-8+8, text = s, anchor=NE, font=("arial", 7),fill = cols[2])
			VAlabels.append(t)
		for k in range(3,6):
			s = '%5.3f'%((k-2)*dy)
			t = VAxes.create_text(LPWIDTH, labelYs[k]-8+8, text = s, anchor=NE, font=("arial", 7),fill = cols[2])
			VAlabels.append(t)
	elif NC == 4:
		dy = 0.25 *rans[0]
		for k in range(3):
			s = '%5.3f'%(-(3-k)*dy)
			t = VAxes.create_text(LPWIDTH, labelYs[k]-8-4-4-4, text = s, anchor=NE, font=("arial", 7),fill = cols[0])
			VAlabels.append(t)
		for k in range(3,6):
			s = '%5.3f'%((k-2)*dy)
			t = VAxes.create_text(LPWIDTH, labelYs[k]-8-4-4-4, text = s, anchor=NE, font=("arial", 7),fill = cols[0])
			VAlabels.append(t)
		dy = 0.25 *rans[1]
		for k in range(3):
			s = '%5.3f'%(-(3-k)*dy)
			t = VAxes.create_text(LPWIDTH, labelYs[k]-8-4, text = s, anchor=NE, font=("arial", 7),fill = cols[1])
			VAlabels.append(t)
		for k in range(3,6):
			s = '%5.3f'%((k-2)*dy)
			t = VAxes.create_text(LPWIDTH, labelYs[k]-8-4, text = s, anchor=NE, font=("arial", 7),fill = cols[1])
			VAlabels.append(t)
		dy = 0.25 *rans[2]
		for k in range(3):
			s = '%5.3f'%(-(3-k)*dy)
			t = VAxes.create_text(LPWIDTH, labelYs[k]-8+4, text = s, anchor=NE, font=("arial", 7),fill = cols[2])
			VAlabels.append(t)
		for k in range(3,6):
			s = '%5.3f'%((k-2)*dy)
			t = VAxes.create_text(LPWIDTH, labelYs[k]-8+4, text = s, anchor=NE, font=("arial", 7),fill = cols[2])
			VAlabels.append(t)
		dy = 0.25 *rans[3]
		for k in range(3):
			s = '%5.3f'%(-(3-k)*dy)
			t = VAxes.create_text(LPWIDTH, labelYs[k]-8+8+4, text = s, anchor=NE, font=("arial", 7),fill = cols[3])
			VAlabels.append(t)
		for k in range(3,6):
			s = '%5.3f'%((k-2)*dy)
			t = VAxes.create_text(LPWIDTH, labelYs[k]-8+8+4, text = s, anchor=NE, font=("arial", 7),fill = cols[3])
			VAlabels.append(t)

'''
def set_ch1_offset(val):
	chan4[0][DOFFSET] = int(val) * VPERDIV

def set_ch2_offset(val):
	chan4[1][DOFFSET] = int(val) * VPERDIV

def set_ch3_offset(val):
	chan4[2][DOFFSET] = int(val) * VPERDIV

def set_ch4_offset(val):
	chan4[3][DOFFSET] = int(val) * VPERDIV
'''

def show_ftr():
	for k in range(4):
		if chan4[k][CHSRC] != 0:
			try:
				fa = eyemath.fit_sine(chan4[k][TDATA],chan4[k][VDATA])
				if fa != None:
					fr = fa[1][1]*1000			# frequency in Hz
					dt = int(1.e6/ (20 * fr))	# dt in usecs, 20 samples per cycle
					t,v = p.capture1(sources[k], 3000, dt)
					xa,ya = eyemath.fft(v,dt)
					eyeplot.plot(xa*1000,ya, title = _('Frequency Spectrum (%s)'%sources[k]), xl = _('Freq'), yl = _('Amp'), col=k)
					msg(_('Frequency Spectrum saved to "spectrum.dat"'))
					p.save([[xa,ya]],'fft.dat')
			except:
				msg('fit err')

def msg(s, col='blue'):
	msgwin.config(text=s, fg=col)

def set_timebase(w):
	global delay, NP, NC, VPERDIV, chan4
	divs = [0.05, 0.100, 0.200, 0.500, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0,100.0]
	chans = []								# Update channel & color information
	for m in range(len(chan4)):
		if chan4[m][0] != None:
			chans.append(chan4[m][0])		# channel number
	NC = len(chans)
	if NC < 1:
		return
	NP = 500
	msperdiv = divs[int(timebase.get())]	#millisecs / division
	totalusec = msperdiv * 1000 * 10.0  	# total 10 divisions
	delay = int(totalusec/NP)
	
	if delay < MINDEL:
		delay = MINDEL
	elif delay > MAXDEL:
		delay = MAXDEL

	g.setWorld(0,-5*VPERDIV, NP * delay * 0.001, 5*VPERDIV,_(xlabel),'V')
	#print _('NP delay = '),NP, delay, 0.0001 * NP*delay, msperdiv


def update():
	global delay, NP, NC, VPERDIV, chan4, CMERR, loopCounter
	if Looping.get() == 0:
		return
	chword = 0
	for m in range(len(chan4)):
		chword += (chan4[m][0] << m)

	try:
		if chword & 12:			# channel 3 or 4 is selected
			chan4[0][TDATA],chan4[0][VDATA], \
			chan4[1][TDATA],chan4[1][VDATA], \
			chan4[2][TDATA],chan4[2][VDATA], \
			chan4[3][TDATA],chan4[3][VDATA]  = p.capture4(NP,delay)
		elif chword & 2:    	# channel 2 is selected  	
			chan4[0][TDATA],chan4[0][VDATA], \
			chan4[1][TDATA],chan4[1][VDATA] = p.capture2(NP,delay)
		elif chword == 1: 		# only A1 selected
			chan4[0][TDATA],chan4[0][VDATA] = p.capture1('A1',NP,delay)

		
		g.delete_lines()		# Remove existing lines
		if chword & 1:
			Vrange = rangevals12[chan4[0][RANGE]]
			g.setWorld(0,-Vrange, NP * delay * 0.001, Vrange,_(xlabel),'V')	
			g.line(chan4[0][TDATA], chan4[0][VDATA], 0); 

		if chword & 2:
			Vrange = rangevals12[chan4[1][RANGE]]
			g.setWorld(0,-Vrange, NP * delay * 0.001, Vrange,_(xlabel),'V')	
			g.line(chan4[1][TDATA], chan4[1][VDATA], 1); 

		if chword & 4:
			Vrange = rangevals34[chan4[2][RANGE]]
			g.setWorld(0,-Vrange, NP * delay * 0.001, Vrange,_(xlabel),'V')	
			g.line(chan4[2][TDATA], chan4[2][VDATA], 2); 

		if chword & 8:
			Vrange = rangevals34[chan4[3][RANGE]]
			g.setWorld(0,-Vrange, NP * delay * 0.001, Vrange,_(xlabel),'V')	
			g.line(chan4[3][TDATA], chan4[3][VDATA], 3); 
		
		if CMERR == True: 
			CMERR = False
			msg('')
		
		
		for k in range(4):
			chan4[k][FITFLAG] = Fitvars[k].get()
			chan4[k][WFIT].config(text = '')
			chan4[k][WFITOK] = 0
		
		for k in range(4):
			if chan4[k][CHSRC] != 0 and chan4[k][FITFLAG] == 1:
				fa = eyemath.fit_sine(chan4[k][TDATA],chan4[k][VDATA])
				if fa != None:
					chan4[k][VFDAT] = fa[0]
					chan4[k][AMP] = abs(fa[1][0])
					chan4[k][FREQ] = fa[1][1]*1000
					chan4[k][PHASE] = fa[1][2] * 180/eyemath.pi
					s = _('%5.2f V, %5.1f Hz')%(chan4[k][AMP],chan4[k][FREQ])
					chan4[k][WFIT].config(text = s, fg= chancols[k])
					chan4[k][WFITOK] = 1
		
		
		if chan4[0][WFITOK] == 1 and chan4[1][WFITOK] == 1:
			Dphi.config(text= _('Phase Shift (A1,A2) = %5.1f deg'%(chan4[1][PHASE]-chan4[0][PHASE])))
		else:
			Dphi.config(text= '')
		
		loopCounter += 1
		if loopCounter % 5 == 0:
			v = p.get_voltage('A1')				# Voltmeter functions
			A1DC.config(text=_('%5.3f V'%(v)))
				
			v = p.get_voltage('A2')
			if v == v:   #is it NaN
				A2DC.config(text=_('%5.3f V'%(v)))
			
			
			v = p.get_voltage('A3')
			if v == v:   #is it NaN
				A3DC.config(text=_('%5.3f V'%(v)))
				
			res = p.get_resistance()
			if res != np.Inf:
				SENres.config(text=_('Resistance on SEN = %5.0f Ohm'%(res)))
			else:
				SENres.config(text=_('Resistance on SEN = Out of range'))
			
	except:
		msg(_('Capture or data fitting error occured.'),'red')
		CMERR = True
	
	root.after(TIMER,update)


def scope_mode():
	if Looping.get() == 1:
		update()

def control_od1():
	state = int(Od1.get())
	p.set_state(OD1=state)

def control_ccs():
	state = int(Ccs.get())
	p.set_state(CCS=state)

def measure_cap():
	cap = p.get_capacitance() * 1.e12
	if cap == None:
		msg(_('Capacitance too high or short to ground'))
	else:
		msg(_('Capacitance on IN1 = %6.1f pF  '%cap))

def measure_freq():
	fr = p.get_freq()
	msg(_('Frequency on IN2 = %6.1f Hz  '%fr))

def save_data():
	fn = Fname.get()
	dat = []
	for k in range(4):
		if chan4[k][CHSRC] != 0:
			dat.append( [chan4[k][TDATA],chan4[k][VDATA]])
	p.save(dat,fn)
	msg(_('Traces saved to %s') %fn)


def xmgrace():
	dat = []
	for k in range(4):
		if chan4[k][CHSRC] != 0:
			dat.append( [chan4[k][TDATA],chan4[k][VDATA]])
	if eyeplot.grace(dat,xlab='Time(mS)', ylab='Voltage (V)', title='Scope Traces') == False:
		msg(_('Could not find Xmgrace or Pygrace. Install them'),'red')
	else:
		msg(_('Traces send to Xmgrace'))
		

#=============================== main program starts here ===================================

root = Tk()    
root.option_add( "*font", "arial 9" ) 

top = Frame(root)
top.pack(side=TOP, anchor =W)
f1 = Frame(top, width = LPWIDTH, height = HEIGHT)
f1.pack(side=LEFT,  fill = BOTH, expand = 1)				# Left side frame

VAxes = Canvas(f1, width = LPWIDTH, height = HEIGHT)
VAxes.pack(side = LEFT, anchor = N, pady = 0)
VAxes.create_text(LPWIDTH, HEIGHT/2-10, text = 'V', anchor=NE, font=("arial", 10),fill = 'blue')

#--------------------------------- Middle Frame ------------------------------
a = Frame(top, width = LPWIDTH, height = HEIGHT)
a.pack(side=LEFT,  fill = BOTH, expand = 1)
f = Frame(a, width = 75, height = HEIGHT)
f.pack(side=TOP,  fill = BOTH, expand = 1)
g = eyeplot.graph(f, width=WIDTH, height=HEIGHT,drawYlab=False)	# make plot objects using draw.disp
g.setWorld(0, -5, 20, 5,_(xlabel),'V')


'''
#============== Vertical scales for OFFSET adjustment. Lambda not working with Scale callbacks !!! =====
of = Frame(top, width = 1, height = HEIGHT)
of.pack(side=LEFT,  fill = BOTH, expand = 1)

Scale(of, orient=VERTICAL, length=HEIGHT/4, showvalue = False, bg = chancols[0],\
		from_ = 4, to=-4, resolution=1, command = set_ch1_offset).pack(side=TOP)
Scale(of, orient=VERTICAL, length=HEIGHT/4, showvalue = False, bg = chancols[1],\
		from_ = 4, to=-4, resolution=1, command = set_ch2_offset).pack(side=TOP)
Scale(of, orient=VERTICAL, length=HEIGHT/4, showvalue = False, bg = chancols[2],\
		from_ = 4, to=-4, resolution=1, command = set_ch3_offset).pack(side=TOP)
Scale(of, orient=VERTICAL, length=HEIGHT/4, showvalue = False, bg = chancols[3],\
		from_ = 4, to=-4, resolution=1, command = set_ch4_offset).pack(side=TOP)

'''

#========================= Right Side panel ===========================================

SQ2MIN = SQ1MIN = -1
SQ2MAX = SQ1MAX = 5000
SQ2val = SQ1val = 1000

def set_sqr1_slider(w):
	global SQ1val
	if p == None: return
	SQ1val = SQ1scale.get()
	if p != None: fr = p.set_sqr1(SQ1val)       # should return actual value set
	ss = '%6.1f'%fr          # 
	SQ1text.delete(0,END)
	SQ1text.insert(0, ss)
	msg(_('SQ1 set to' + ss))
	
def set_sqr1_text(w):
	global SQ1val
	SQ1val = float(SQ1text.get())
	if SQ1MIN <= SQ1val <= SQ1MAX:
		SQ1scale.set(SQ1val)
		p.set_sqr1(SQ1val)
	
PV1MIN = -5.0
PV1MAX = 5.0
PV1val = 0.0

def set_pv1_slider(w):
	global PV1val
	pos = PV1scale.get()
	PV1val = (pos-5000)*10.0/10000
	PV1text.delete(0,END)
	PV1text.insert(0,str(PV1val))
	if p != None: p.set_pv1(PV1val)
	
def set_pv1_text(w):
	global PV1val
	PV1val = float(PV1text.get())
	if PV1MIN <= PV1val <= PV1MAX:
		p.set_pv1(PV1val)
		x = (PV1val + 5.0)*10000/10
		PV1scale.set(int(x))

PV2MIN = -3.3
PV2MAX = 3.3
PV2val = 0.0

def set_pv2_slider(w):
	global PV2val
	pos = PV2scale.get()
	PV2val = (pos-3300)*6.6/6600
	PV2text.delete(0,END)
	PV2text.insert(0,str(PV2val))
	if p != None: p.set_pv2(PV2val)
	
def set_pv2_text(w):
	global PV2val
	PV2val = float(PV2text.get())
	if PV2MIN <= PV2val <= PV2MAX:
		p.set_pv2(PV2val)
		x = (PV2val + 3.3)*6600/6.6
		PV2scale.set(int(x))


AWGMIN = 5
AWGMAX = 5000
AWGval = 150
Waves = ['sine', 'tria', 'SQR2']
Wgains = ['80 mV', '1 V', '3 V']
waveindex = 0
wgainindex = 2
	
def set_wave():
	global AWGval, waveindex
	if p == None: return 
	WGsel.config(text = _(Waves[waveindex]))
	if waveindex <= 1:
		fs = p.set_wave(AWGval, Waves[waveindex])
		ss = '%5.1f'%fs
		Wfreq.delete(0,END)
		Wfreq.insert(0,ss)
		msg(_('Wave set to' + ss))
	else:
		p.set_sqr2(AWGval)
		msg(_('Output Changed from WG to SQ2 '))

def set_awg_slider(w):
	global AWGval
	AWGval = Wscale.get()
	Wfreq.delete(0,END)
	Wfreq.insert(0,str(AWGval))
	set_wave()
	
def set_awg_text(w):
	global AWGval
	AWGval = float(Wfreq.get())
	if AWGMIN <= AWGval <= AWGMAX:
		Wscale.set(AWGval)
		set_wave()

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

RPWIDTH = 260
rf = Frame(top, width = RPWIDTH, height = HEIGHT, bd=2)
rf.pack(side=LEFT,  fill = BOTH, expand=True)
rf.pack_propagate(0)

Label(rf,text = _('Measurements & Controls'),fg='blue').pack(side=TOP, anchor = SW)

#Frame(rf,width=120, height=5).pack()    # Spacer
f = Frame(rf)
f.pack(side=TOP, anchor = SW)
f.columnconfigure(2, minsize=50)
f.columnconfigure(4, minsize=50)
f.columnconfigure(6, minsize=50)
Label(f,text=_('A1 = ')).grid(row=1, column=1)
A1DC = Label(f, text = '',fg='blue')
A1DC.grid(row=1, column=2)
Label(f,text=_('A2 = ')).grid(row=1, column=3)
A2DC = Label(f, text ='',fg='blue')
A2DC.grid(row=1, column=4)
Label(f,text=_('A3 = ')).grid(row=1, column=5)
A3DC = Label(f, text ='',fg='blue')
A3DC.grid(row=1, column=6)

f = Frame(rf)
f.pack(side=TOP, anchor = SW)

SENres = Label(f,text =_('Resistance on SEN = out of range'),borderwidth=1,padx=2,pady=2)
SENres.pack()

f = Frame(rf)
f.pack(side=TOP, anchor = SW)
b=Button(f,text =_('Capacitance on IN1'),command=measure_cap,borderwidth=1,pady=2)
b.grid(row=2, column=1,sticky=E+W)
eyeplot.CreateToolTip(b,_('Click to measure capacitace on IN1'))
b=Button(f,text =_('Frequency on IN2'),  command=measure_freq,borderwidth=1,padx=2,pady=2)
b.grid(row=2, column=2,sticky=E+W)
eyeplot.CreateToolTip(b,_('Click to measure Frequency on IN2'))

Frame(rf,width=120, height=5).pack()    # Spacer

f = Frame(rf)
f.pack(side=TOP, anchor = SW)
Od1 = IntVar()
Ccs = IntVar()
OD=Checkbutton(f,text = 'Enable OD1', variable = Od1, command = control_od1)
OD.pack(side=LEFT)
eyeplot.CreateToolTip(OD,_('Set OD1 to 0 or 5 volts'))
CC = Checkbutton(f,text = 'Enable CCS', variable = Ccs, command = control_ccs)
CC.pack(side=LEFT)
eyeplot.CreateToolTip(CC,_('Enable the 1.1mA Current Source'))

f = Frame(rf)
f.pack(side=TOP, anchor = SW)
Label(f,text = _('WG Shape')).pack(side=LEFT)
WGsel = Button(f,text = _('sine'),borderwidth=1,pady=1)
WGsel.bind("<ButtonRelease-1>", pop_Wavemenu) 
WGsel.pack(side=LEFT) 
eyeplot.CreateToolTip(WGsel,_('Click to select WG wave type'))
menuWG = Menu(WGsel, tearoff=0)
for k in range(len(Waves)):
	menuWG.add_command(label=Waves[k], background= 'ivory', command = lambda index=k :select_wave(index))


Label(f,text = _('Amplitude')).pack(side=LEFT)
WGgainsel = Button(f,text = _('3 V'),borderwidth=1,pady=1)
WGgainsel.bind("<ButtonRelease-1>", pop_Wgainmenu) 
WGgainsel.pack(side=LEFT) 
eyeplot.CreateToolTip(WGgainsel,_('Click to select WG Amplitude'))
menuWGgain = Menu(WGgainsel, tearoff=0)
for k in range(len(Waves)):
	menuWGgain.add_command(label=Wgains[k], background= 'ivory', command = lambda index=k :select_wgain(index))


SLIDER = 80
Frame(rf,width=120, height=5).pack()    # Spacer

f = Frame(rf)
f.pack(side=TOP, anchor = SW)
l=Label(f,text = _('WG'))
l.grid(row=1, column=1)  
eyeplot.CreateToolTip(l,_('To set the WG frequency use slider or type the value followed by Enter key'))
Wscale = Scale(f,command = set_awg_slider, orient=HORIZONTAL, length=SLIDER, showvalue=False, from_ = 0, to=AWGMAX, resolution=1)
Wscale.grid(row=1, column=2) 
Wscale.set(1000)
Wfreq = Entry(f, width = 6)
Wfreq.grid(row=1, column=3) 
Wfreq.bind("<Return>",set_awg_text)
Label(f,text = _('Hz')).grid(row=1, column=4)
 

l=Label(f,text = _('SQ1'))
l.grid(row=2, column=1) 
eyeplot.CreateToolTip(l,_('To set the SQ1 frequency use slider or type the value followed by Enter key'))
SQ1scale = Scale(f,command = set_sqr1_slider, orient=HORIZONTAL, length=SLIDER, showvalue=False, from_ = 0, to=SQ1MAX, resolution=1)
SQ1scale.grid(row=2, column=2) 
SQ1scale.set(1000)
SQ1text = Entry(f, width = 6)
SQ1text.grid(row=2, column=3) 
SQ1text.bind("<Return>",set_sqr1_text)
Label(f,text = _('Hz')).grid(row=2, column=4) 

l=Label(f,text = _('PV1'))
l.grid(row=3, column=1) 
eyeplot.CreateToolTip(l,_('To set PV1 (from -5 to 5 volts) use slider or type the value followed by Enter key'))
PV1scale = Scale(f,command = set_pv1_slider, orient=HORIZONTAL, length=SLIDER, showvalue=False, from_ = 0, to=10000, resolution=1)
PV1scale.grid(row=3, column=2) 
PV1scale.set(5000)
PV1text = Entry(f, width = 6)
PV1text.grid(row=3, column=3) 
PV1text.bind("<Return>",set_pv1_text)
Label(f,text = _('V')).grid(row=3, column=4) 

l=Label(f,text = _('PV2'))
l.grid(row=4, column=1) 
eyeplot.CreateToolTip(l,_('To set PV2 (from -3.3 to +3.3 volts) use slider or type the value followed by Enter key'))
PV2scale = Scale(f,command = set_pv2_slider, orient=HORIZONTAL, length=SLIDER, showvalue=False, from_ = 0, to=6600, resolution=1)
PV2scale.grid(row=4, column=2) 
PV2scale.set(3300)
PV2text = Entry(f, width = 5)
PV2text.grid(row=4, column=3) 
PV2text.bind("<Return>",set_pv2_text)
Label(f,text = _('V')).grid(row=4, column=4) 

Frame(rf,width=120, height=5).pack()    # Spacer

#------------------ Scope control ---------------------------
Looping = IntVar()				
Selectvars = [IntVar(),IntVar(),IntVar(),IntVar()]
Selectvars[0].set(1)
Fitvars = [IntVar(),IntVar(),IntVar(),IntVar()]

def selectA1():
	chan4[0][CHSRC] = Selectvars[0].get()
	draw_ylabels()

def selectA2():
	chan4[1][CHSRC] = Selectvars[1].get()
	draw_ylabels()
	
def selectA3():
	chan4[2][CHSRC] = Selectvars[2].get()
	draw_ylabels()
	
def selectA4():
	chan4[3][CHSRC] = Selectvars[3].get()
	draw_ylabels()

def pop_A1ranges(event):
	poped = True
	menuA1.post(RanA1.winfo_rootx(),RanA1.winfo_rooty()) 
	
def pop_A2ranges(event):
	poped = True
	menuA2.post(RanA2.winfo_rootx(),RanA2.winfo_rooty()) 

def pop_A3ranges(event):
	poped = True
	menuA3.post(RanA3.winfo_rootx(),RanA3.winfo_rooty()) 
	
def pop_A4ranges(event):
	poped = True
	menuA4.post(RanA4.winfo_rootx(),RanA4.winfo_rooty()) 

def select_A1range(index):
	chan4[0][RANGE] = index
	RanA1.config(text=  Ranges12[index])
	p.select_range('A1', rangevals12[index])
	draw_ylabels()
	
def select_A2range(index):
	chan4[1][RANGE] = index
	RanA2.config(text=  Ranges12[index])
	p.select_range('A2', rangevals12[index])
	draw_ylabels()
	
def select_A3range(index):
	chan4[2][RANGE] = index
	RanA3.config(text=  Ranges34[index])
	draw_ylabels()
	
def select_A4range(index):
	chan4[3][RANGE] = index
	RanA4.config(text=  Ranges34[index])
	draw_ylabels()
	

def pop_trigmenu(event):
	poped = True
	menuTrig.post(Trigsrc.winfo_rootx(),Trigsrc.winfo_rooty()) 

trigindex = 0
trigval = 0

def select_trig(index):
	global trigindex, trigval
	trigindex = index
	v = trigval - 500
	v *= 3.3/500
	Trigsrc.config(text= sources[index])
	if p != None: p.configure_trigger(index, sources[index], v)

def set_trigger(w):
	global trigval
	trigval = Trig.get()		# returns a number between 0 to 1000
	select_trig(trigindex)

#---------------------- Oscilloscope Channels -----------------------------

f = Frame(rf)			# Analog Channel A1 and range selection
f.pack(side=TOP, anchor = SW)
Label(f,text = _('Oscilloscope Channels, Range and Analysis '),fg='blue').pack(side=LEFT, anchor = SW)

	
f = Frame(rf)			# Analog Channel A1 and range selection
f.pack(side=TOP, anchor = SW)
f.columnconfigure(2, minsize=55)
Ch1 = Checkbutton(f,text = 'A1 ', variable = Selectvars[0], command = selectA1)
Ch1.grid(row=1, column=1)
eyeplot.CreateToolTip(Ch1,_('Enable A1'))
RanA1 = Button(f,text = _('4V'),borderwidth=1,pady=1)
RanA1.bind("<ButtonRelease-1>", pop_A1ranges)
RanA1.grid(row=1, column=2,sticky=E+W)
eyeplot.CreateToolTip(RanA1,_('Button to select the input range of A1. Same method for other channels also'))
menuA1 = Menu(RanA1, tearoff=0)
for k in range(len(Ranges12)):
	menuA1.add_command(label=Ranges12[k], background= 'ivory', command = lambda index=k :select_A1range(index))
CB=Checkbutton(f,text = '', variable = Fitvars[0])
CB.grid(row=1, column=3)
eyeplot.CreateToolTip(CB,_('Checkbox to display Amplitude and Frequency of signal at A1. Similar for other channels also'))
chan4[0][WFIT] = Label(f, text ='')
chan4[0][WFIT].grid(row=1, column=4)

A2var = IntVar()
Ch2 = Checkbutton(f,text = 'A2 ', variable = Selectvars[1], command = selectA2)
Ch2.grid(row=2, column=1)
eyeplot.CreateToolTip(Ch2,_('Enable A2'))
RanA2 = Button(f,text = _('4V'),borderwidth=1,pady=1)
RanA2.bind("<ButtonRelease-1>", pop_A2ranges)
RanA2.grid(row=2, column=2,sticky=E+W)
menuA2 = Menu(RanA2, tearoff=0)
for k in range(len(Ranges12)):
	menuA2.add_command(label=Ranges12[k], background= 'ivory', command = lambda index=k :select_A2range(index))
CB=Checkbutton(f,text = '', variable = Fitvars[1])
CB.grid(row=2, column=3)
chan4[1][WFIT] = Label(f, text ='')
chan4[1][WFIT].grid(row=2, column=4)

A3var = IntVar()
Ch3 = Checkbutton(f,text = 'A3 ', variable = Selectvars[2], command = selectA3)
Ch3.grid(row=3, column=1)
eyeplot.CreateToolTip(Ch3,_('Enable A3'))
RanA3 = Button(f,text = _('4V'),borderwidth=1,pady=1)
RanA3.bind("<ButtonRelease-1>", pop_A3ranges)
RanA3.grid(row=3, column=2, sticky=E+W)
menuA3 = Menu(RanA3, tearoff=0)
for k in range(len(Ranges34)):
	menuA3.add_command(label=Ranges34[k], background= 'ivory', command = lambda index=k :select_A3range(index))
CB=Checkbutton(f,text = '', variable = Fitvars[2])
CB.grid(row=3, column=3)
chan4[2][WFIT] = Label(f, text ='')
chan4[2][WFIT].grid(row=3, column=4)

A4var = IntVar()
Ch4 = Checkbutton(f,text = 'MIC', variable = Selectvars[3], command = selectA4)
Ch4.grid(row=4, column=1)
eyeplot.CreateToolTip(Ch4,_('Enable MIC'))
RanA4 = Button(f,text = _('4V'),borderwidth=1,pady=1)
RanA4.bind("<ButtonRelease-1>", pop_A4ranges)
RanA4.grid(row=4, column=2, sticky=E+W)
menuA4 = Menu(RanA4, tearoff=0)
for k in range(len(Ranges34)):
	menuA4.add_command(label=Ranges34[k], background= 'ivory', command = lambda index=k :select_A4range(index))
CB=Checkbutton(f,text = '', variable = Fitvars[3])
CB.grid(row=4, column=3)

chan4[3][WFIT] = Label(f, text ='')
chan4[3][WFIT].grid(row=4, column=4)

Frame(rf,width=120, height=5).pack()    # Spacer

f = Frame(rf)			# Timebase and Trigger
f.pack(side=TOP, anchor = SW)
f.columnconfigure(1, minsize=50)
l=Label(f,text = _('Timebase'))
l.grid(row=1, column=1)
eyeplot.CreateToolTip(l,_('use slider to set the time axis. From .05 to 50 mS/division'))

timebase = Scale(f,command = set_timebase, orient=HORIZONTAL, length=SLIDER, showvalue=False,\
	from_ = 0, to=9, resolution=1)
timebase.grid(row=1, column=2)
timebase.set(4)

Label(f,text = _('mS/div')).grid(row=1, column=3)	
Loop = Checkbutton(f, text=_('LOOP'), variable = Looping, command = scope_mode)
Loop.grid(row=1, column=4)
eyeplot.CreateToolTip(Loop,_('Update traces in a loop or Freeze'))
Looping.set('1')

l=Label(f,text = _('Trig Level'))
l.grid(row=2, column=1)
eyeplot.CreateToolTip(l,_('Use slider to set the Trigger level'))

Trig = Scale(f,command = set_trigger, orient=HORIZONTAL, length=SLIDER, showvalue=False,\
	from_ = 0, to=1000, resolution=1)
Trig.grid(row=2, column=2)
Trig.set(500)

Label(f,text = _('Source')).grid(row=2, column=3)
Trigsrc = Button(f,text = _('A1'),borderwidth=1,pady=1)
Trigsrc.bind("<ButtonRelease-1>", pop_trigmenu)
Trigsrc.grid(row=2, column=4)
eyeplot.CreateToolTip(Trigsrc,_('Select the Trigger Source'))
menuTrig = Menu(Trigsrc, tearoff=0)
for k in range(len(sources)):
	menuTrig.add_command(label=sources[k], background= 'ivory', command = lambda index=k :select_trig(index))

Frame(rf,width=120, height=5).pack()    # Spacer

#---------------------------------

f = Frame(rf)
f.pack(side=TOP, anchor = W)
Save = Button(f,text=_('SaveTo'), command = save_data,borderwidth=1,pady=1,padx=5)
Save.pack(side=LEFT, anchor=N)
eyeplot.CreateToolTip(Save,_('Saves the traces to a text file'))
Fname = Entry(f, width=12)
Fname.pack(side=LEFT)
Fname.insert(0,_('traces.txt'))
eyeplot.CreateToolTip(Fname,_('Edit the filename'))

FFT = Button(f,text=_('FFT'), command = show_ftr,borderwidth=1,pady=1)
FFT.pack(side=LEFT, anchor=N)
eyeplot.CreateToolTip(FFT,_('Do Fourier Transform and show Frequency spectrum of the traces'))
Grace = Button(f, text=_('Grace'), command = xmgrace,borderwidth=1,pady=1)
Grace.pack(side=LEFT)
eyeplot.CreateToolTip(Grace,_('Show the traces in Xmgrace program'))

Frame(rf,width=120, height=5).pack()    # Spacer
f = Frame(rf)			
f.pack(side=TOP, anchor = SW)
Dphi = Label(f,text = '', fg='blue')
Dphi.pack(side=LEFT, anchor = SW)

#------------------------------Message Frame---------
mf = Frame(root, bg=_('white'))
mf.pack(side=TOP,  fill = BOTH, expand = 1)
msgwin = Label(mf,text = '', justify=CENTER, bg = _('white'), fg = _('blue'),font=(_('Helvetica'), 12))
msgwin.pack(side=LEFT, anchor = CENTER)
	
connect()

#------------------------------Menu Items------------------------------
HelpWin =None

def run_expt(expt):
	global p, HelpWin
	if HelpWin != None: HelpWin.destroy()
	if expt == '': return
	p.H.disconnect()		# Free the device from this program, the child will open it
	fn = os.path.join(os.path.dirname(sys.argv[0]), expt+'.py')
	cmd = sys.executable + ' ' + fn
	os.system(cmd)
	p = eyes.open()			# Establish hardware communication again, for the parent
	p.select_range('A1', 4)
	p.select_range('A2', 4)

def disp_help(h):
	global HelpWin
	if HelpWin != None: HelpWin.destroy()
	HelpWin = eyeplot.pop_help(h[1],h[0])
	
dummyEntry = [            # A dummy entry to reconnect the device 
[_('Reconnect'),'connect']
]

electronicsExpts = [ 
[_('Halfwave Rectifier'),'halfwave'],
[_('Fullwave Rectifier'),'fullwave'],
[_('Diode Clipping'),'clipping'],
[_('Diode Clamping'),'clamping'],
[_('IC555 Multivibrator'),'osc555'],
[_('Diode IV Char.'),'diode_iv'],
[_('NPN Output Char.'),'transistor_out'],
[_('AM and FM'), 'amfm']
]

opAmpExpts = [ 
[_('Inverting Amplifier'),'opamp-inv'],
[_('Non-Inverting Amplifier'),'opamp-noninv'],
[_('Integrator using Op-Amp'),'opamp-int']
]

digitalExpts = [ 
[_('Logic Gates'),'and-gate'],
[_('Clock Divider Circuit'),'clock-divider']
]


electricalExpts = [ 
[_('RC Steady state response'),'RCsteadystate'],
[_('RLC Steady state response'),'RLCsteadystate'],
[_('RC Transient response'),'RCtransient'],
[_('RL Transient response'),'RLtransient'],
[_('RLC transient response'),'RLCtransient'],
[_('EM Induction'),'induction']
]

soundExpts = [
[_('Frequency Response of Piezo Buzzer'),'Piezo-freq-resp'],
[_('Velocity of Sound') , 'sound-velocity'],
[_('Sound beats') , 'sound-beats']
]

mechanicsExpts = [
[_('Driven Pendulum resonance'),'driven-pendulum'],
[_('Rod Pendulum with Light barrier') , 'rod-pendulum'],
[_('Pendulum Wavefrorm'),'pendulum-velocity'],
[_('Distance by HY-SRF04'), 'sr04-dist']
]

otherExpts = [ 
[_('Temperatue, PT100 Sensor'), 'pt100'],
[_('Stroboscope'), 'stroboscope'],
[_('Data Logger'), 'logger']
]

schoolExpts = [ 
[_("Resistance measurement"), 'res-measure'],
[_("Resistors in Series"), 'res-series'],
[_("Resistors in Parallel"), 'res-parallel'],
[_("Capacitance measurement"), 'cap-measure'],
[_("Capacitors in Series"), 'cap-series'],
[_("Capacitors in Parallel"), 'cap-parallel'],
[_("Resistance by Ohm's law"), 'res-compare'],
[_('Resistance of Human body'), 'res-body'],
[_('Direct & Alternating Currents'), 'ac-dc'],
[_('Separating AC & DC'), 'acdc-separating'],
[_('Lemon Cell'), 'lemon-cell'],
[_('Simple AC generator'), 'ac-generator'],
[_('Transformer'), 'transformer'],
[_('Resistance of Water'), 'res-water'],
[_('Sound Generator'), 'sound-generator'],
[_('Light Dependent Resistor'), 'ldr'],
[_('Capturing Sound'), 'sound-capture']
]


menubar = Menu(root)				# menubar will populated later

reconnMenu = Menu(menubar, tearoff=0)
for ex in dummyEntry:
	reconnMenu.add_command(label=ex[0], command = lambda expt=ex[1] :run_expt(expt))
reconnMenu.add_command(label='Exit', command = sys.exit)
menubar.add_cascade(label="EYES17", menu=reconnMenu)


electronicsMenu = Menu(menubar, tearoff=0)
for ex in electronicsExpts:
	electronicsMenu.add_command(label=ex[0], command = lambda expt=ex[1] :run_expt(expt))
menubar.add_cascade(label="Electronics", menu=electronicsMenu)

opAmpMenu = Menu(electronicsMenu, tearoff=0)
for ex in opAmpExpts:
	opAmpMenu.add_command(label=ex[0], command = lambda expt=ex :disp_help(expt))
electronicsMenu.add_cascade(label='Op-Amp Circuits', menu=opAmpMenu, underline=0)

digitalMenu = Menu(electronicsMenu, tearoff=0)
for ex in digitalExpts:
	digitalMenu.add_command(label=ex[0], command = lambda expt=ex :disp_help(expt))
electronicsMenu.add_cascade(label='Digital Circuits', menu=digitalMenu, underline=0)

electricalMenu = Menu(menubar, tearoff=0)
for ex in electricalExpts:
	electricalMenu.add_command(label=ex[0], command = lambda expt=ex[1] :run_expt(expt))
menubar.add_cascade(label="Electrical", menu=electricalMenu)

soundMenu = Menu(menubar, tearoff=0)
for ex in soundExpts:
	soundMenu.add_command(label=ex[0], command = lambda expt=ex[1] :run_expt(expt))
menubar.add_cascade(label="Sound", menu=soundMenu)

mechanicsMenu = Menu(menubar, tearoff=0)
for ex in mechanicsExpts:
	mechanicsMenu.add_command(label=ex[0], command = lambda expt=ex[1] :run_expt(expt))
menubar.add_cascade(label="Mechanics", menu=mechanicsMenu)

otherMenu = Menu(menubar, tearoff=0)
for ex in otherExpts:
	otherMenu.add_command(label=ex[0], command = lambda expt=ex[1] :run_expt(expt))
menubar.add_cascade(label="Misc Expts", menu=otherMenu)

schoolMenu = Menu(menubar, tearoff=0)
for ex in schoolExpts:
	schoolMenu.add_command(label=ex[0], command = lambda expt=ex :disp_help(expt))
menubar.add_cascade(label="SchoolLevel", menu=schoolMenu)


root.config(menu=menubar)
draw_ylabels()
root.protocol("WM_DELETE_WINDOW", sys.exit)
root.mainloop()
