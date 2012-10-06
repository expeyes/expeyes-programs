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
import expeyes.eyesj as eyes, expeyes.eyeplot as eyeplot, expeyes.eyemath as eyemath, time, os, commands

bgcol = 'ivory'

BUFSIZE = 1800		# uC buffer size in bytes
TIMER = 100
WIDTH  = 600   		# width of drawing canvas
HEIGHT = 400   		# height 
VPERDIV = 1.0		# Volts per division, vertical scale
NP = 400			# Number of samples
NC = 1				# Number of channels
MINDEL = 4		
delay = MINDEL		# Time interval between samples
CMERR = False

MAXCHAN = 4
chan4 = [ [1, [], [],0,[],0,0,0,None,None,0.0 ],\
		  [0, [], [],0,[],0,0,0,None,None,0.0 ],\
		  [0, [], [],0,[],0,0,0,None,None,0.0 ],\
		  [0, [], [],0,[],0,0,0,None,None,0.0 ]\
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
DOFFSET = 10

# Data Sources and their names
sources = ['A1','A2','IN1', 'IN2', 'SEN', 'SQ1', 'SQ2', 'OD1', 'CCS']
channels = ['CH1', 'CH2', 'CH3', 'CH4']
chancols = ['black', 'red', 'blue','magenta']
# Actions before capturing waveforms
actions = ['ATR', 'WHI', 'WLO', 'WRE', 'WFE','SHI', 'SLO', 'HTP', 'LTP']
acthelp = [_('Analog Trigger'),_('Wait for HIGH'), _('Wait for LOW'), \
	   _('Wait for Rising Edge'), _('Wait for Falling Edge'),\
	   _('Set HIGH'), _('Set LOW'), _('High True Pulse'), \
	   _('Low True Pulse')]

srchelp = [_('Analog Input -5 to +5 volts. Drag this to CH1 .. CH4 to Display it'),\
	   _('Analog Input -5 to +5 volts. Drag this to CH1 .. CH4 to Display it'),\
	   _('Analog Input  0 to +5 volts. Drag this to CH1 .. CH4 to Display it'),\
	   _('Analog Input  0 to +5 volts. Drag this to CH1 .. CH4 to Display it'),\
	   _('Analog Input  0 to +5 volts. Drag this to CH1 .. CH4 to Display it'),\
	   _('Analog Input  0 to +5 volts. Drag this to CH1 .. CH4 to Display it'),\
	   _('Analog Input  0 to +5 volts. Drag this to CH1 .. CH4 to Display it'),\
	   _('Digital Output 0 to +5 volts. SHI, SLO,HTP or LTP can be assigned to this'),\
	   _('Constant Current Source Output. SHI, SLO,HTP or LTP can be assigned to this')\
	   ]

# Geometry of the left panel, selection of triggers  & channels
LPWIDTH  = 80
LPHEIGHT = 320
VSTEP = 25
VBORD = 10
OFFSET   = VSTEP * len(sources)
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

def set_ch1_offset(val):
	chan4[0][DOFFSET] = int(val) * VPERDIV

def set_ch2_offset(val):
	chan4[1][DOFFSET] = int(val) * VPERDIV

def set_ch3_offset(val):
	chan4[2][DOFFSET] = int(val) * VPERDIV

def set_ch4_offset(val):
	chan4[3][DOFFSET] = int(val) * VPERDIV

def show_ftr(ch):
	fa = eyemath.fit_sine(chan4[ch][TDATA],chan4[ch][VDATA])	# get frequency to decide suitable 'dt'
	if fa != None:
		fr = fa[1][1]*1000			# frequency in Hz
		dt = int(1.e6/ (20 * fr))	# dt in usecs, 20 samples per cycle
		t,v = p.capture(chan4[ch][CHSRC], 1800, dt)
		xa,ya = eyemath.fft(v,dt)
		eyeplot.plot(xa*1000,ya, title = _('Fourier Transform,power spectrum'), xl = _('Freq'), yl = _('Amp'))
		msg(_('%s Fourier transform done, Data saved to "fft.dat"') %(channels[seltag]))
		p.save([[xa,ya]],'fft.dat')

def msg(s, col='blue'):
	msgwin.config(text=s, fg=col)

def set_timebase(w):
	global delay, NP, NC, VPERDIV, chan4
	divs = [0.100, 0.200, 0.500, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0,100.0]
	msperdiv = divs[int(timebase.get())]
	totalusec = int(msperdiv * 1000 * 10)
	chans = []				# Update channel & color information
	for m in range(len(chan4)):
		if chan4[m][0] > 0:
			chans.append(chan4[m][0])		# channel number
	NC = len(chans)
	if NC < 1:
		return
	if totalusec == 1000:
		NP = 250
		delay = 4*NC
	else:
		NP = 400
		delay = (totalusec/NP)*NC

	if delay < MINDEL*NC:
		delay = MINDEL*NC
	elif delay > 1000:
		delay = 1000

	totalmsec = round(0.001 * NP * NC *delay)
	tms = int(totalmsec)
	NP = tms * 1000/NC/delay
	if NP%2 == 1 : NP += 1		# Must be an even number, for fitting
	if NP > 450: NP = 450
	g.setWorld(0,-5*VPERDIV, NP * delay * 0.001, 5*VPERDIV,_('mS'),'V')
	#print _('NP delay = '),NP, delay, 0.0001 * NP*delay, msperdiv

def measure_freq(e):
	w = e.widget
	tag =w.find_closest(e.x, e.y)
	item = w.itemcget(tag,'tag')
	target = int(item.split()[0])
	if e.x < LPWIDTH/2 and e.y < OFFSET and 2 < target < 8:	 # Selected IN1, IN2, SEN, SQR1 or SQR2
		freq = p.get_frequency(target)
		if freq > 0.5:
			r2f = p.r2ftime(target, target)*1.0e-6
			msg(_('%4s : Freq = %5.3f. Duty Cycle = %5.1f %%') %(sources[target-1], freq, r2f*freq*100))
		else:
			msg(_('No squarewave detected on %4s') %(sources[target-1]))
	elif e.x > LPWIDTH/2 and e.y > OFFSET and target < 3:	 # Selected CH1, CH2 or CH3
		if chan4[target][CHSRC] != 0 and chan4[target+1][CHSRC] != 0:  # both channels active
			fa = eyemath.fit_sine(chan4[target][TDATA],chan4[target][VDATA])
			fb = eyemath.fit_sine(chan4[target+1][TDATA],chan4[target+1][VDATA])
			if fa != None and fb != None:
				v1 = fa[1][0]
				v2 = fb[1][0]
				f1 = fa[1][1]*1000	# millisecond x-axis gives frequency in kHz, convert it
				f2 = fb[1][1]*1000
				p1 = fa[1][2]
				p2 = fb[1][2]
				s = _('%s: %5.3f V, %5.2f Hz | %s: %5.2f V, %5.3f Hz | Phase difference = %5.1f degree') \
				    % (channels[target], v1, f1, channels[target+1],v2, f2, (p2-p1)*180/3.1416)
				msg(s)
			else:
				msg(_('Fitting of data failed. Try with Xmgrace'))
		else:
			msg(_('Selected channel and the next one should have data'), 'red')

def release(e):
	global selection, seltag, chan4, NC
	w = e.widget
	w.configure(cursor = 'arrow')
	if selection == 0:
		msg(_('Invalid Action'), 'red')
		return
	tag =w.find_closest(e.x, e.y)
	item = w.itemcget(tag,'tag')
	target = int(item.split()[0])
	if e.x > LPWIDTH/2 and e.y > OFFSET and selection == SELSRC:		# Assign source to channel
		msg(_('Assigned Data Input %4s to Channel %s') %(sources[seltag-1],channels[target]))
		s = '%s:' %(sources[seltag-1])
		chan4[target][WINFO].config(text = s, fg=chancols[target])
		chan4[target][0] = seltag
		set_timebase(0)				# Adding  a channel require recalculation
	elif e.x < LPWIDTH/2 and e.y < OFFSET and selection == SETACT and target > 6:   
		msg(_('%4s effective on Output %s') %(acthelp[seltag], sources[target-1]))
		p.enable_action(seltag, target+2)		# There is an offset of 2 for OD1 & CCS
		#print 'SET ', seltag,target+2
	elif e.x < LPWIDTH/2 and e.y < OFFSET and selection == WAITACT and target <= 7:   
		msg(_('%4s effective on Input %s') %(acthelp[seltag], sources[target-1]))
		p.enable_action(seltag, target)
	elif e.x < LPWIDTH/2 and e.y > OFFSET and selection == SELCHAN:    # Selected channel    
		if target == DEL:
			chan4[seltag][CHSRC] = 0 
			chan4[seltag][FITFLAG] = 0 
			chan4[seltag][WINFO].config(text = '')
			chan4[seltag][WFIT].config(text = '')
			msg('Disabled Display channel %s'%(channels[seltag]))
			set_timebase(0)				# Deleting a channel require recalculation
		elif target == FIT:
			if chan4[seltag][CHSRC] != 0:
				chan4[seltag][FITFLAG] = True
				msg('Selected %s for fitting'%(channels[seltag]))
			else:
				msg(_('Channel %s is Empty') %(channels[seltag]), 'red')
		elif target == FTR:
			if chan4[seltag][CHSRC] != 0:
				show_ftr(seltag)			# Channel for FT
			else:
				msg(_('Channel %s is Empty') %(channels[seltag]), 'red')
		elif target == NORMAL:
			if chan4[seltag][CHSRC] != 0:
				chan4[seltag][FITFLAG] = False
				chan4[seltag][WFIT].config(text = '')
				msg(_('Disabled fitting %s') %(channels[seltag]))
			else:
				msg(_('Channel %s is Empty') %(channels[seltag]), 'red')
	elif e.x < LPWIDTH/2 and e.y < OFFSET and selection == SELSRC:    # Selected Source
		src = sources[target-1]
		val = p.get_voltage(target)
		ss = _('Voltage at %s = %5.3f V') %(src,val)
		if 2 < target < 8:
			level = p.get_state(target)
			ss += _(' (Logic Level = %d)') %level
		msg(ss)
	else:
		msg(_('Invalid selection'), 'red')		

def press(e):
	global selection, seltag
	selection = 0
	w = e.widget
	tag =w.find_closest(e.x, e.y)
	item = w.itemcget(tag,'tag')
	if item == '' or item[0] == 'c': return		# clicked on borders
	seltag = int(item.split()[0])
	if e.x < LPWIDTH/2 and e.y < OFFSET:		# Source selection
		if seltag > 7: 
			msg(_('%4s is an Output') %sources[seltag-1], 'red')
			return
		selection = SELSRC
		msg(_('Selected Data Input %4s. For Trace, Drag this to CH1 .. CH4. To show value release button.') %sources[seltag-1],'black')
		w.configure(cursor = 'pencil')
	elif e.x > LPWIDTH/2 and e.y < OFFSET:		# Trigger selection
		if seltag >= 5:
			selection = SETACT
			msg(_('Selected %4s. Drag cursor to the OD1 or CSS Output') %acthelp[seltag],'black')
			w.configure(cursor = 'hand1')
		else:
			selection = WAITACT
			msg(_('Selected %4s. Drag cursor to desired Data Input') %acthelp[seltag],'black')
			w.configure(cursor = 'hand2')
	elif e.x > LPWIDTH/2 and e.y > OFFSET:		# Channel selection
			selection = SELCHAN
			msg(_('Selected %4s. Drag cursor to NML FIT or DEL') %channels[seltag],'black')
			w.configure(cursor = 'pencil')

def update():
	global delay, NP, NC, VPERDIV, chan4, CMERR
	global NP, NC, delay,chan4
	chans = []						# Update channel & color information
	index = []
	for m in range(len(chan4)):
		if chan4[m][0] > 0:
			 chans.append(chan4[m][0])		# channel number
			 index.append(m)				# Store the used indices, for storing & fitting
	NC = len( chans)
	try:
		if NC == 1:
			chan4[index[0]][TDATA],chan4[index[0]][VDATA] = p.capture_hr(chans[0],NP,delay)
			v1 = []
			for k in range(NP): v1.append( chan4[index[0]][VDATA][k] + chan4[index[0]][DOFFSET])
			g.delete_lines()
			g.line(chan4[index[0]][TDATA],v1, index[0])
		elif NC == 2:
			chan4[index[0]][TDATA],chan4[index[0]][VDATA], \
			chan4[index[1]][TDATA],chan4[index[1]][VDATA] = p.capture2_hr( chans[0],  chans[1],NP,delay)
			v1 = []
			v2 = []
			for k in range(NP): 
				v1.append( chan4[index[0]][VDATA][k] + chan4[index[0]][DOFFSET])
				v2.append( chan4[index[1]][VDATA][k] + chan4[index[1]][DOFFSET])
			g.delete_lines()
			g.line(chan4[index[0]][TDATA], v1, index[0])
			g.line(chan4[index[1]][TDATA], v2, index[1])
		elif NC == 3:
			chan4[index[0]][TDATA],chan4[index[0]][VDATA], chan4[index[1]][TDATA],chan4[index[1]][VDATA], \
			chan4[index[2]][TDATA],chan4[index[2]][VDATA] = p.capture3( chans[0], chans[1], chans[2],NP,delay)
			v1 = []
			v2 = []
			v3 = []
			for k in range(NP): 
				v1.append( chan4[index[0]][VDATA][k] + chan4[index[0]][DOFFSET])
				v2.append( chan4[index[1]][VDATA][k] + chan4[index[1]][DOFFSET])
				v3.append( chan4[index[2]][VDATA][k] + chan4[index[2]][DOFFSET])
			g.delete_lines()
			g.line(chan4[index[0]][TDATA], v1, index[0])
			g.line(chan4[index[1]][TDATA], v2, index[1])
			g.line(chan4[index[2]][TDATA], v3, index[2])
		elif NC == 4:
			chan4[index[0]][TDATA],chan4[index[0]][VDATA], chan4[index[1]][TDATA],chan4[index[1]][VDATA], \
			chan4[index[2]][TDATA],chan4[index[2]][VDATA], chan4[index[3]][TDATA],chan4[index[3]][VDATA] \
				 = p.capture4( chans[0],  chans[1], chans[2], chans[3],NP,delay)
			v1 = []
			v2 = []
			v3 = []
			v4 = []
			for k in range(NP): 
				v1.append( chan4[index[0]][VDATA][k] + chan4[index[0]][DOFFSET])
				v2.append( chan4[index[1]][VDATA][k] + chan4[index[1]][DOFFSET])
				v3.append( chan4[index[2]][VDATA][k] + chan4[index[2]][DOFFSET])
				v4.append( chan4[index[3]][VDATA][k] + chan4[index[3]][DOFFSET])
			g.delete_lines()
			g.line(chan4[index[0]][TDATA], v1, index[0])
			g.line(chan4[index[1]][TDATA], v2, index[1])
			g.line(chan4[index[2]][TDATA], v3, index[2])
			g.line(chan4[index[3]][TDATA], v4, index[3])
		if CMERR == True: 
			CMERR = False
			msg('')
	except:

		msg(_('Communication Error. Check input voltage levels.'),'red')
		CMERR = True
	
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
	if looping.get() == '0':
		root.after(10,update)

def set_vertical(w):
	global delay, NP, NC, VPERDIV
	divs = [5.0, 1.0, 0.5, 0.2]
	VPERDIV = divs[int(Vpd.get())]
	g.setWorld(0,-5*VPERDIV, NP * delay * 0.001, 5*VPERDIV,_('mS'),'V')

def set_trigger(w):
	tv = Trig.get()
	if p != None: p.set_trigger(tv)

def cro_mode():
	state = looping.get()
	if state == '1':
		Loop.config(text=_('ONE '))
		msg(_('Press SCAN Button to do a single Capture'))
	else:
		Loop.config(text=_('LOOP'))
		root.after(10,update)

def scan():
	if looping.get() == '1':
		update()
		msg(_('Captured %d points in %d usecs') %(NP,NP*delay))
	else:
		msg(_('Use this only in Single scan mode'), 'red')

def set_pvs(e):
	try:
		v = float(Pvs.get())
		res = p.set_voltage(v)
		if res == None:
			msg(_('Enter a value between 0 to +5 volts'),'red')
		else:
			msg(_('PVS set to %5.3f volts') %res)
	except:
		msg(_('Enter voltage between -5 and +5 volts'),'red')

def set_sqr1():
	state = int(Sqr1.get())
	if state == 0:
		p.set_sqr1(-1)
		msg(_('SQR1 set to LOW'))
	else:
		try:
			fr = float(Freq.get())
			res = p.set_sqr1(fr)
			if res == None:
				msg(_('Enter a value between .7 to 200000 Hz'))
			else:
				msg(_('SQR1 set to %5.1f Hertz') %res)
		except:
			msg(_('Enter valid frequency, in Hertz'),'red')

def set_sqr2():
	state = int(Sqr2.get())
	if state == 0:
		p.set_sqr2(-1)
		msg(_('SQR2 set to LOW'))
	else:
		try:
			fr = float(Freq.get())
			res = p.set_sqr2(fr)
			if res == None:
				msg(_('Enter a value between .7 to 200000 Hz'))
			else:
				msg(_('SQR2 set to %5.1f Hertz') %res)
		except:
			msg(_('Enter valid frequency, in Hertz'),'red')

def set_sqrs():
	state = int(Both.get())
	if state == 0:
		p.set_sqr1(-1)
		p.set_sqr2(-1)
		msg(_('SQR1 and SQR2 set to LOW'))
	else:
		try:
			fr = float(Freq.get())
			shift = float(Phase.get())
			res = p.set_sqrs(fr,shift)
			if res == None:
				msg(_('Enter a value between .7 to 200000 Hz'))
			else:
				msg(_('SQR1 and SQR2 set to %5.1f Hertz, Shift is %5.2f %% of Period') %(res,shift))
		except:
			msg(_('Enter valid frequency in Hertz and phase shift in percentage'),'red')

def sqr1_slider(w):
	if p == None: return
	freq = SQR1slider.get()
	if freq == 0: 
		p.set_sqr1(-1)
		msg(_('SQR1 set to LOW'))
	else:
		fs = p.set_sqr1(freq)
		msg(_('SQR1 set to %5.1f') %fs)

def control_od1():
	state = int(Od1.get())
	p.set_state(10, state)

def control_ccs():
	state = int(Ccs.get())
	p.set_state(11, state)

def measurecap():
	global stray_cap
	msg(_('Starting Capacitance Measurement..'))
	cap = p.measure_cap()
	if cap == None:
		msg(_('Error: Capacitance too high or short to ground'),'red')
		return
	msg(_('Capacitance = %6.1f pF(%6.1fpF - %6.1fpF of the Socket)')%(cap-stray_cap, cap, stray_cap))

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
	if p.grace(dat) == False:
		msg(_('Could not find Xmgrace or Pygrace. Install them'),'red')
	else:
		msg(_('Traces send to Xmgrace'))

def process_command(e):
	cp = Result.index(INSERT)
	row = int(cp.split('.')[0])
	ss = Result.get("%d.0"%row, "%d.end"%row)	# User's entry
	cmd = 'p.'+ ss								# command
	p.msg = ''
	try:
		res = eval(cmd)
		if res == None: 
			res = p.msg
	except:
		res = 'Invalid command or argument'
	Result.insert("%d.0"%(row+1), '\n'+str(res))		# Result below

def pop_expt_menu(event):
	poped = True
	menu.post(event.x_root, event.y_root)

def reconnect():
	global p
	import expeyes.eyesj
	p=expeyes.eyesj.open()
	if p == None:
		msg(_('expEYES Junior NOT found. Bad connection or another program using it'),'red')
	else:
		Recon.forget()
		s = _('Four Channel CRO+ found expEYES-Junior on %s') %p.device
		root.title(s)
		msg(s)
		root.after(TIMER,update)

#=============================== main program starts here ===================================
root = Tk()    
f1 = Frame(root, width = LPWIDTH, height = HEIGHT)

f1.pack(side=LEFT,  fill = BOTH, expand = 1)				# Left side frame
w = Canvas(f1, width=LPWIDTH, height=LPHEIGHT,bg = bgcol)   # Canvas for drag n drop controls
w.pack(side=TOP, anchor = W)
for k in range(len(sources)):
	if k >6: 
		col = 'blue'
	else:
		col = 'black'
	w.create_text (LPWIDTH/2-10, VBORD+k*VSTEP, anchor = E, text = sources[k], tag = k+1, fill=col)
for k in range(len(actions)):
	if  k >= 5:
		col = 'blue'
	else:
		col = 'black'
	w.create_text (LPWIDTH/2+10, VBORD+k*VSTEP, anchor = W, text = actions[k], tag = k, fill=col)
for k in range(4):
	w.create_text (LPWIDTH/2+10, VBORD + OFFSET + k*VSTEP, anchor = W, text = channels[k], tag = k,\
		fill= chancols[k])
w.create_text (LPWIDTH/2-10, VBORD + OFFSET + 0*VSTEP, anchor = E, text = 'NML', tag = NORMAL)
w.create_text (LPWIDTH/2-10, VBORD + OFFSET + 1*VSTEP, anchor = E, text = 'FTR', tag = FTR)
w.create_text (LPWIDTH/2-10, VBORD + OFFSET + 2*VSTEP, anchor = E, text = 'FIT', tag = FIT)
w.create_text (LPWIDTH/2-10, VBORD + OFFSET + 3*VSTEP, anchor = E, text = 'DEL', tag = DEL)
w.create_line(LPWIDTH/2, 0, LPWIDTH/2, LPHEIGHT)
w.create_line(0, OFFSET, LPWIDTH, OFFSET)
w.bind ("<ButtonPress-1>", press)
w.bind ("<ButtonPress-3>", measure_freq)
w.bind ("<ButtonRelease-1>", release)
offsets = [_('Move UP'), _('CENTER'), _('Move DOWN')]	
offsetmenu = Menu(w, tearoff=0)
for k in range(len(offsets)):
	offsetmenu.add_command(label=offsets[k], background= 'ivory', command = lambda cmd=k :change_offset(cmd))

Label(f1,text = _('mSec/div')).pack(side=TOP, anchor = SW)		# Sliders for Adjusting Axes & Trigger Level
timebase = Scale(f1,command = set_timebase, orient=HORIZONTAL, length=LPWIDTH, showvalue=False,\
	from_ = 0, to=9, resolution=1)
timebase.pack(side=TOP, anchor = SW)

Label(f1,text = _('Volt/div')).pack(side=TOP, anchor = SW)
Vpd = Scale(f1,command = set_vertical, orient=HORIZONTAL, length=LPWIDTH, showvalue=False,\
	from_ = 0, to=3, resolution=1)
Vpd.pack(side=TOP, anchor = SW)
Vpd.set(1)

Label(f1,text = _('Trig level')).pack(side=TOP, anchor = SW)
Trig = Scale(f1,command = set_trigger, orient=HORIZONTAL, length=LPWIDTH, showvalue=False,\
	from_ = 100, to=4000, resolution=10)
Trig.pack(side=TOP, anchor = SW)
Trig.set(2050)


#--------------------------------- Middle Frame ------------------------------
a = Frame(root, width = LPWIDTH, height = HEIGHT)
a.pack(side=LEFT,  fill = BOTH, expand = 1)
f = Frame(a, width = 75, height = HEIGHT)
f.pack(side=TOP,  fill = BOTH, expand = 1)
g = eyeplot.graph(f, width=WIDTH, height=HEIGHT)	# make plot objects using draw.disp
g.setWorld(0, -5, 20, 5,_('mS'),'V')
mf = Frame(a, width = 75, height = HEIGHT)
mf.pack(side=TOP,  fill = BOTH, expand = 1)
msgwin = Label(mf,text = _('Use Left Side Panel to Select Data Sources and Modifiers.'), fg = 'blue')
msgwin.pack(side=LEFT)#, anchor = SW)
Recon = Button(mf,text = _('Search Hardware'), command =reconnect)

#============== Vertical scales for OFFSET adjustment. Lambda not working with Scale callbacks !!! =====
of = Frame(root, width = 1, height = HEIGHT)
of.pack(side=LEFT,  fill = BOTH, expand = 1)

Scale(of, orient=VERTICAL, length=HEIGHT/4, showvalue = False, bg = chancols[0],\
		from_ = 4, to=-4, resolution=1, command = set_ch1_offset).pack(side=TOP)
Scale(of, orient=VERTICAL, length=HEIGHT/4, showvalue = False, bg = chancols[1],\
		from_ = 4, to=-4, resolution=1, command = set_ch2_offset).pack(side=TOP)
Scale(of, orient=VERTICAL, length=HEIGHT/4, showvalue = False, bg = chancols[2],\
		from_ = 4, to=-4, resolution=1, command = set_ch3_offset).pack(side=TOP)
Scale(of, orient=VERTICAL, length=HEIGHT/4, showvalue = False, bg = chancols[3],\
		from_ = 4, to=-4, resolution=1, command = set_ch4_offset).pack(side=TOP)

#========================= Right Side panel ===========================================
rf = Frame(root, width = 75, height = HEIGHT)
rf.pack(side=LEFT,  fill = BOTH, expand = 1)

#---------------------- Extra Features -----------------------------
cf = Frame(rf, border = 1, relief = SUNKEN)
cf.pack(side=TOP,  fill = BOTH, expand = 1)

Label(cf, text = _('Setting Squarewaves'), fg='blue').pack(side=TOP)
f = Frame(cf)
f.pack(side=TOP, anchor = W)
Freq = Entry(f, width = 6)
Freq.pack(side=LEFT, anchor = N)
Freq.insert(0,'1000')
Label(f,text = _('Hz. dphi=')).pack(side=LEFT, anchor = N)
Phase = Entry(f, width=4)
Phase.pack(side=LEFT, anchor=N)
Phase.insert(0,'0')
Label(f,text = '%').pack(side=LEFT, anchor = N)

f = Frame(cf)			# Setting square waves
f.pack(side=TOP)
Sqr1 = IntVar()
Checkbutton(f,text = 'SQR1', command = set_sqr1, variable = Sqr1).pack(side=LEFT, anchor=N)
Sqr2 = IntVar()
Checkbutton(f,text = 'SQR2', command = set_sqr2, variable = Sqr2).pack(side=LEFT, anchor=N)
Both = IntVar()
Checkbutton(f,text = _('BOTH'), command = set_sqrs, variable = Both).pack(side=LEFT, anchor=N)

SQR1slider = Scale(cf,command = sqr1_slider, orient=HORIZONTAL, length=180, showvalue=False, from_ = 0, to=5000, resolution=5)
SQR1slider.pack(side=TOP, anchor=W)
Canvas(cf, height = 5,  width = 100).pack(side=TOP)	# Spacer

f = Frame(cf)			# Setting OD1 and CCS
f.pack(side=TOP)
Label(f, text = _('Set PVS =')).pack(side=LEFT)
Pvs = Entry(f, width = 6)
Pvs.pack(side=LEFT)
Pvs.bind("<Return>",set_pvs)
Pvs.bind("<KP_Enter>",set_pvs)
Pvs.insert(0,'0')
Label(f, text = 'V').pack(side=LEFT)

#Label(cf, text = 'Control OD1 & CCS', fg='blue').pack(side=TOP)
f = Frame(cf)			# Setting OD1 and CCS
f.pack(side=TOP)
Label(f, text = _('Set State')).pack(side=LEFT)
Od1 = IntVar()
Checkbutton(f,text = 'OD1', variable = Od1, command = control_od1).pack(side=LEFT, anchor=N)
Ccs = IntVar()
Checkbutton(f,text = 'CCS', variable = Ccs, command = control_ccs).pack(side=LEFT, anchor=N)
Canvas(cf, height = 5, width= 100).pack(side=TOP)	# Spacer

Button(cf,text =_('Measure C on IN1'), command=measurecap).pack(side=TOP, anchor=N)
Button(cf,text =_('Measure R on SEN'), command=measureres).pack(side=TOP, anchor=N)

Canvas(cf, height = 5, width= 100).pack(side=TOP)	# Spacer

Label(cf, text = _('Type command<Enter>'), fg='blue').pack(side=TOP)
Result = Text(cf, width = 25, height = 6)
Result.pack(side=TOP)
Result.bind("<Return>", process_command)
Result.bind("<KP_Enter>", process_command)

#-----------------------------------------------------------------
looping = 1				# Make Status display Region
for ch in range(4):
	f = Frame(rf)
	f.pack(side=TOP, anchor = W)
	chan4[ch][8] = Label(f, width=4, text = '', fg=chancols[ch])	# 8 is Label, 9 is value
	chan4[ch][8].pack(side=LEFT, anchor = N)
	chan4[ch][9] = Label(f, width=16, text = '')
	chan4[ch][9].pack(side=LEFT, anchor = N)
chan4[0][WINFO].config(text = 'A1')

#---------------
f = Frame(rf)
f.pack(side=TOP, anchor = W)
Save = Button(f,text=_('Save Traces to'), command = save_data)
Save.pack(side=LEFT, anchor=N)
Fname = Entry(f, width=8)
Fname.pack(side=LEFT)
Fname.insert(0,'cro.txt')

f = Frame(rf)
f.pack(side = TOP, anchor=W)
looping = StringVar()
Loop = Checkbutton(f, text=_('LOOP'), variable = looping, command = cro_mode)
Loop.pack(side=LEFT)
looping.set('0')
Scan = Button(f, text=_('SCAN'), command = scan)
Scan.pack(side=LEFT)
Grace = Button(f, text=_('XMG'), command = xmgrace)
Grace.pack(side=LEFT)
#Canvas(rf, height = 5, width= 100).pack(side=TOP)	# Spacer

f = Frame(rf)
f.pack(side=TOP, anchor = W)
Expt = Button(f,text = _('EXPERIMENTS'))
Expt.bind("<ButtonRelease-1>", pop_expt_menu)
Expt.pack(side=LEFT)
q = Button(f,text=_('QUIT'), command = sys.exit)
q.pack(side=LEFT, anchor=N)

p = eyes.open()
if p == None:
	msg(_('Could not open expEYES Junior. Bad connection or another program using it'),'red')
	Recon.pack(side=LEFT)
else:
	p.disable_actions()
	c = p.measure_cap()
	if 25 < c < 45:
		stray_cap = c
	else:
		stray_cap = 30.0
	root.title(_('Four Channel CRO+ found expEYES-Junior on %s') %p.device)
	root.after(TIMER,update)
#------------------------------ experiments menu ------------------------------
expts = [ 
[_('Select Experiment'),''],
[_('Study of AC Circuits'),'ac-circuit'],
[_('RC Circuit'),'RCcircuit'],
[_('RL Circuit'),'RLcircuit'],
[_('RLC Discharge'),'RLCdischarge'],
[_('EM Induction'),'induction'],
[_('Diode IV'),'diode_iv'],
[_('Transistor CE'),'transistor'],
[_('AM and FM'), 'amfm'],
[_('Frequency Response'),'freq-response'],
[_('Velocity of Sound') , 'velocity-sound'],
[_('Interference of Sound') , 'interference-sound'],
[_('Capture Burst of Sound') , 'sound-burst'],
[_('Driven Pendulum'),'driven-pendulum'],
[_('Rod Pendulum') , 'rodpend'],
[_('Pendulum Wavefrorm'),'pendulum'],
[_('PT100 Sensor'), 'pt100'],
[_('Stroboscope'), 'stroboscope'],
[_('Data Logger'), 'logger'],
[_('Calibrate'),'calibrate']
 ]

def run_expt(expt):
	global p
	if expt == '': return
	p.fd.close()	# Free the device from this program, the child will open it
	cmd = sys.executable + ' ' + eyeplot.abs_path() + expt+'.py'
	os.system(cmd)
	msg(_('Finished "')+expt+'.py"')
	p = eyes.open()	# Establish hardware communication again, for the parent
	p.disable_actions()

menu = Menu(Expt, tearoff=0)
for k in range(len(expts)):
	text = expts[k][0]
	cmd = expts[k][1]
	#print text, cmd
	menu.add_command(label=text, background= 'ivory', command = lambda expt=cmd :run_expt(expt))

root.mainloop()

