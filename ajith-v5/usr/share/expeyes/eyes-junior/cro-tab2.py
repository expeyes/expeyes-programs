'''
expEYES Junior CRO program
Author  : Ajith Kumar B.P, bpajith@gmail.com
License : GNU GPL version 3
Date : Feb-2013
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
WIDTH  = 400   		# width of drawing canvas  (make 550)
HEIGHT = 300   		# height 
VPERDIV = 1.0		# Volts per division, vertical scale
NP = 400			# Number of samples
NC = 1				# Number of channels
MINDEL = 4		
delay = MINDEL		# Time interval between samples
CMERR = False

MAXCHAN = 4
chan4 = [ [0, [], [],0,[],0,0,0,None,None,0.0 ],\
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
sources = ['A1','A2','IN1', 'IN2', 'SEN', 'SQ1', 'SQ2']
SrcLabs = [None]*7
channels = ['CH1', 'CH2', 'CH3', 'CH4']
chancols = ['black', 'red', 'blue','magenta']
# Actions before capturing waveforms

# Geometry of the left panel, selection of triggers  & channels
LPWIDTH  = 70
VSTEP = 50
VBORD = 25
LPHEIGHT   = VSTEP * len(sources)
XPRESS  = 0
SELSRC = 0

def get_first_empty():
	for k in range(4):
		if chan4[k][0] == 0:
			print k
			return k
	return None	

def release(e):
	global XPRESS, SELSRC, chan4, NC
	#print e.x, e.y, e.y/VSTEP
	if SELSRC != (1+e.y/VSTEP):
		return
	if XPRESS < e.x:				# Assign to some channel
		target = get_first_empty()
		if target == None: 
			return
		for k in range(4):
			if chan4[k][CHSRC] == SELSRC:	# Already assigned to a channel
				return
		msg(_('Assigned Data Input %4s to Channel %s') %(sources[SELSRC-1],channels[target]))
		s = '%s:' %(sources[SELSRC-1])
		chan4[target][0] = SELSRC
		print SELSRC
		k = SELSRC-1
		w.delete(SrcLabs[k])
		SrcLabs[k] = w.create_text (LPWIDTH/2, VBORD+k*VSTEP, text = sources[k], \
			font=(_('Helvetica'), 20), fill = chancols[target])
		set_timebase(0)					# Adding  a channel require recalculation
	elif XPRESS > e.x:					# Remove assignment
		for k in range(4):
			if chan4[k][CHSRC] == SELSRC:		
				chan4[k][CHSRC] = 0 
				chan4[k][FITFLAG] = 0 
				print SELSRC
				src = SELSRC-1
				w.delete(SrcLabs[src])
				SrcLabs[src] = w.create_text (LPWIDTH/2, VBORD+src*VSTEP, text = sources[src], \
					font=(_('Helvetica'), 20), fill = 'gray')
				msg('Disabled Display channel %s'%(channels[k]))
				set_timebase(0)				# Deleting a channel require recalculation

def press(e):
	global XPRESS, SELSRC
	XPRESS = e.x
	SELSRC = 1 + e.y/VSTEP
	return

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
			s=_('%4s\n%5.3f Hz\n%5.1f %%')%(sources[target-1], freq, r2f*freq*100)
			g.disp(s)
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
				s=_('%4s\n%5.3f Hz\n%5.1f %%')%(sources[target-1], freq, r2f*freq*100)
				g.disp(s)
			else:
				msg(_('Fitting of data failed. Try with Xmgrace'))
		else:
			msg(_('Selected channel and the next one should have data'), 'red')

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
	g.delete_lines()
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
	root.after(10,update)

def set_vertical(w):
	global delay, NP, NC, VPERDIV
	divs = [5.0, 1.0, 0.5, 0.2]
	VPERDIV = divs[int(Vpd.get())]
	g.setWorld(0,-5*VPERDIV, NP * delay * 0.001, 5*VPERDIV,_('mS'),'V')

def save_data():
	fn = Fname.get()
	dat = []
	for k in range(4):
		if chan4[k][CHSRC] != 0:
			dat.append( [chan4[k][TDATA],chan4[k][VDATA]])
	p.save(dat,fn)
	msg(_('Traces saved to %s') %fn)

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
top = Frame(root)
top.pack(side=TOP, anchor =W)
f1 = Frame(top, width = LPWIDTH, height = HEIGHT)
f1.pack(side=LEFT,  fill = BOTH, expand = 1)				# Left side frame

w = Canvas(f1, width=LPWIDTH, height=LPHEIGHT,bg = bgcol)   # Canvas for drag n drop controls
w.pack(side=LEFT, anchor = W)
for k in range(len(sources)):
	SrcLabs[k] = w.create_text (LPWIDTH/2, VBORD+k*VSTEP, text = sources[k], \
			tag = k+1,font=(_('Helvetica'), 20), fill = 'grey')

w.bind ("<ButtonPress-1>", press)
w.bind ("<ButtonRelease-1>", release)
#Label(f1,text = _('Volt/div')).pack(side=TOP, anchor = SW)


#--------------------------------- Middle Frame ------------------------------
a = Frame(top, width = LPWIDTH, height = HEIGHT)
a.pack(side=LEFT,  fill = BOTH, expand = 0)
Vpd = Scale(top,command = set_vertical, orient=VERTICAL, length=HEIGHT, showvalue=False,\
	from_ = 0, to=3, resolution=1)
Vpd.pack(side=LEFT, anchor = NW)
Vpd.set(1)

f = Frame(a, width = 75, height = HEIGHT)
f.pack(side=TOP,  fill = BOTH, expand = 1)
g = eyeplot.graph(f, width=WIDTH, height=HEIGHT)	# make plot objects using draw.disp
g.setWorld(0, -5, 20, 5,_('mS'),'V')

#Label(f,text = _('mSec/div')).pack(side=TOP, anchor = SW)		# Sliders for Adjusting Axes & Trigger Level
timebase = Scale(f,command = set_timebase, orient=HORIZONTAL, length=WIDTH, showvalue=False,\
	from_ = 0, to=9, resolution=1)
timebase.pack(side=TOP, anchor = SE)


mf = Frame(root, bg=_('white'))
mf.pack(side=TOP,  fill = BOTH, expand = 1)
msgwin = Label(mf,text = _(''), justify=CENTER, bg = _('white'), fg = _('blue'),font=(_('Helvetica'), 12))
msgwin.pack(side=LEFT, anchor = CENTER)
Recon = Button(mf,text = _('Search Hardware'), command =reconnect)

p = eyes.open()
if p == None:
	msg(_('Could not open expEYES Junior. Bad connection or another program using it'),'red')
	Recon.pack(side=LEFT)
else:
	p.disable_actions()
	root.title(_('Four Channel CRO+ found expEYES-Junior on %s') %p.device)
	root.after(TIMER,update)

p.set_sqrs(100,25)
root.mainloop()

