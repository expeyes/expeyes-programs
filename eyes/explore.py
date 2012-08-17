'''
expEYES Explorer program
Author  : Ajith Kumar B.P, bpajith@gmail.com
License : GNU GPL version 3
'''

import gettext
gettext.bindtextdomain("expeyes")
gettext.textdomain('expeyes')
_ = gettext.gettext

from Tkinter import *
import Image, ImageTk, tkFont, os, sys, commands, math
import expeyes.eyes as eyes, expeyes.eyeplot as eyeplot

try:		
	import expeyes.eyemath as eyemath		# Will fail if scipy is not installed
	EYEMATH = True
except:
	EYEMATH = False


WIDTH  = 555.0 * 0.8
HEIGHT = 677.0 * 0.8
BORDER =  0 #HEIGHT/8
TIMER  = 50
picture = 'pics/eyes.png'
pgreen = '#d1e244'


help = [
_('For help, click on the Terminal Boxes(1 to 32).\nLIZ : Lissajous figure.\n')+\
_('FT : Fourier Transform power spectrum.\nXM : Xmgrace 2D plotting program\n')+\
_('XmGrace is NOT available under MSWindows'),
_('1.Software can read the voltage input level, LOW ( < .8V) or HIGH (>2V).\n') +\
_('If a square wave input is given, click on the Buttons for measuring frequency / duty cycle'),
_('2. Can sense input level'),
_('3. Digital Output.  Can be set to 0 or 5 volts.\nUse the Checkbutton to change the Level'),
_('4. Digital Output.  Can be set to 0 or 5 volts.\nUse the Checkbutton to change the Level'),
_('5. Ground (zero volts)'),
_('6. SQR1: Generates Square Wave. Voltage swings between 0 and 5V. Frequency is programmable from ')+\
_('Hz to1 MHz. All intermediate values of frequency are not possible.'),
_('7. SQR2: Generates Square Wave. The frequency range is controlled by software and fine adjustment ')+\
_('is done by an external 22 kOhm variable resistor. Frequency range is from 0.7 Hz to 90 kHz.'),
_('8. 22 kOhm resistor used for frequency adjustment of SQR2.'),
_('9. 22 kOhm resistor used for frequency adjustment of SQR2.'),
_('10. Programmable Pulse. Frequency is 488.3 Hz. Duty cycle from 0 to 100% in 255 steps.'),
_('11. Ground'),
_('12. Output of Inverting Amplifier with a gain of 47. (Input at 14)'),
_('13. Output of Inverting Amplifier with a gain of 47. (Input at 15)'),
_('14. Input of Inverting Amplifier with a gain of 47. (Output at 12)'),
_('15. Input of Inverting Amplifier with a gain of 47. (Output at 13). Also acts as a Frequency counter, ')+\
_('for a bipolar a signal (amplitude from 100 mV to 5V). If the signal is unipolar feed it ')+\
_('via a series capacitor'),
_('16. Ground'),
_('17. Input of Inverting Amplifier. Default Gain=100. The gain can be reduced by a series resistor at the input. ')+\
_('The gain will be given by G = 10000/(100+R), where R is the value of the external series resistor.'),
_('18. Output of the Inverting Amplifier (Input 17)'),
_('19. Ground'),
_('20. Gain control resistor for Non-Inverting amplifier, from 20 to Ground. Gain = 1 + 10000/Rg.'),
_('21. Input of Non-Inverting Amplifier (Output 22)'),
_('22. Output of Non-Inverting Amplifier(Input 21)'),
_('23. Sensor Input. Connect Photo transistor collector here and emitter to Ground.'),
_('24. Voltage measurement terminal. Input must be in the 0 to 5V range.'),
_('25. Voltage measurement terminal. Input must be in the -5V to 5V range.'),
_('26. Voltage measurement terminal. Input must be in the -5V to 5V range.'),
_('27. Ground'),
_('28. Programmable constant current source. 0.05 to 2 milli ampere range. The load resistor ')+\
_('should be chosen to make the product of I and R less than 2 volts.'),
_('29. Output of 30 through a 1kOhm resistor. Used for doing diode I-V characteristic.'),
_('30. Programmable voltage between -5V to +5V.'),
_('31. Programmable voltage between 0 to +5V.'),
_('32. Sine wave output. Frequency around 90 Hz. Voltage swings between -4V to +4V.')
]
class eyePanel:
	NSIG = 1 + 32						# zeroth element is unused
	tw = [None] * NSIG				    # List to store the widget variables created on the Panel
	LE = [ 6,  7, 10]					# Entry widget on left side
	LL = [ 1, 2, 8, 15]					# Lebel widgets on left side
	RE = [28, 30, 31]					# Entry widget on left side
	RL = [22,23,24,25,26,27]			# Lebel widgets on left side
	doutval = [None] * 2				# IntVar() of CheckButton widgets
	doutCB  = [None] * 2				# Checkbutton widgets
	NOSQR2 = True						# SQR2 is not set
	NOSF = True							# No frequency on SENSOR input
	NOAF = True							# No frequency on Amplifier input, T15
	NODF = True							# No frequency on Digital input 0
	OUTMASK = 0							# Digital outputs to LOW
	trace = None
	poped = False

	def pop_expt_menu(self,event):
		self.poped = True
		menu.post(event.x_root, event.y_root)

	limits = {3:(0,1), 4:(0,1), 6:(0,100000.), 7:(-1,100000.), 10:(0.,100.0), \
					28:(0.020, 3.0), 29:(-5.,5.), 30:(-5.,5.), 31:(0.,5.) }
	def get_fieldvalue(self,i):
		try:
			s = self.tw[i].get()
			val = float(s)
			if self.limits[i][0] <= val <= self.limits[i][1]:
				return val
		except:
			pass

	def __init__(self, parent, handle, width=WIDTH, height = HEIGHT):
		self.eye = handle 
		self.parent = parent
		self.width = width
		self.height = height
		self.border = BORDER				# Top and bottom self.border
		self.fw = float(width)/12.7			# field width
		self.fh = float(height - 2 * self.border)/16	# field height
		im = Image.open(eyeplot.abs_path()+ picture)
		im = im.resize((int(width),int(height)))
		self.image = ImageTk.PhotoImage(im)
		self.panel = Canvas(parent, width = width, height = height)
		self.panel.create_image(0,0,image = self.image, anchor = NW)

		self.popup = Button(text = _('EXPERIMENTS'), bg=pgreen)
		self.popup.bind("<ButtonRelease-1>", self.pop_expt_menu)
		self.panel.create_window(width/2, height-20, window = self.popup, anchor = CENTER)
		
		self.panel.bind("<ButtonRelease-1>", self.clicked)
		self.panel.bind("<ButtonRelease-3>", self.pop_expt_menu)
		self.panel.pack(side=TOP, anchor=SW)

		for i in self.LE:				# Text Entry Fields on left
			x,y = self.xyfromi(i)
			self.tw[i] = Entry(width = 8, bg = 'white', fg='blue')
			self.tw[i].bind("<Return>", self.process)
			self.tw[i].bind("<KP_Enter>", self.process)
			self.panel.create_window(3.5*self.fw, y, window = self.tw[i], anchor = W)

		for i in self.LL:				# Label widgets on left
			x,y = self.xyfromi(i)
			self.tw[i] = Label(width = 8, bg = pgreen, fg='blue', bd=1)
			self.tw[i].bind("<Return>", self.process)
			self.tw[i].bind("<KP_Enter>", self.process)
			if i == 8: y -= 12
			self.panel.create_window(3.5*self.fw, y, window = self.tw[i], anchor = W)

		for i in self.RE:				# Text Entry Fields on right
			x,y = self.xyfromi(i)
			self.tw[i] = Entry(width = 8, bg = 'white', fg='blue')
			self.tw[i].bind("<Return>", self.process)
			self.tw[i].bind("<KP_Enter>", self.process)
			self.panel.create_window(width-3*self.fw, y, window = self.tw[i], anchor = E)

		for i in self.RL:				# Text Entry Fields on right
			x,y = self.xyfromi(i)
			self.tw[i] = Label(width = 8, bg = pgreen, fg='blue', bd=1)
			self.tw[i].bind("<Return>", self.process)
			self.tw[i].bind("<KP_Enter>", self.process)
			if i == 27 or i == 22: y -= 12
			self.panel.create_window(width-3*self.fw, y, window = self.tw[i], anchor = E)

		for i in range(2):
			x,y = self.xyfromi(i+3)
			self.doutval[i] = IntVar()
			self.doutCB[i] = Checkbutton(bg = 'red', variable = self.doutval[i], \
					command = lambda i=i : self.checked(i))
			self.panel.create_window(3.5*self.fw, y, window = self.doutCB[i], anchor = W)
			self.doutCB[i].config(text=_('LO'),bg='gray')

			x,y = self.xyfromi(28)
			self.panel.create_line([width-self.fw, y, width-3*self.fw, y+self.fh/2], fill= pgreen)
			x,y = self.xyfromi(23)
			self.panel.create_line([width-self.fw, y, width-3*self.fw, y+self.fh/2], fill= pgreen)
			x,y = self.xyfromi(7)
			self.panel.create_line([self.fw, y, 3.5*self.fw, y+self.fh/2], fill= pgreen)


		x,y = self.xyfromi(1)
		self.FRB = Button(bg = 'gray', text =_('F'), padx=0, pady=0,	command = self.freq_id0)
		self.panel.create_window(3.0*self.fw, y, window = self.FRB, anchor = W)
		self.DCB = Button(bg = 'gray', text ='%', padx=0, pady=0,	command = self.duty_cycle)
		self.panel.create_window(5.5*self.fw, y, window = self.DCB, anchor = W)
		x,y = self.xyfromi(15)
		self.FRB = Button(bg = 'gray', text =_('F'), padx=0, pady=0,	command = self.freq_ampin)
		self.panel.create_window(3.0*self.fw, y, window = self.FRB, anchor = W)
		x,y = self.xyfromi(22)
		self.FRB = Button(bg = 'gray', text =_('F'), padx=0, pady=0,	command = self.freq_adc5)
		self.panel.create_window(width-6.2*self.fw, y, window = self.FRB, anchor = SW)
		self.looping = True


	def freq_adc5(self):
		fr = self.eye.sensor_frequency()
		if fr < 0:
			self.labset(22, _('0 Hz'))
			self.NOSF = True
		else:
			self.labset(22, '%5.2f Hz'%(fr))
			self.NOSF = False

	def freq_ampin(self):
		fr = self.eye.ampin_frequency()
		if fr < 0:
			self.labset(15, _('0 Hz'))
			self.NOAF = True
		else:
			self.labset(15, '%5.2f Hz'%(fr))
			self.NOAF = False

	def freq_id0(self):
		fr = self.eye.digin_frequency(0)
		if fr < 0:
			self.labset(1, _('0 Hz'))
		else:
			self.labset(1, '%5.2f Hz'%fr)

	def ifromxy(self,e):				# Calculates the Index from the xy coordinates
		#print e.x, e.x_root, e.y, e.y_root
		if self.border < e.y < self.height-self.border and (e.x < 2*self.fw or e.x > self.width-2*self.fw):
			if e.x < self.fw:
				return 1, int(float(e.y-self.border)/self.fh)+1
			elif e.x < 2*self.fw:
				return 2, int(float(e.y-self.border)/self.fh)+1
			elif e.x > self.width - self.fw:
				return 1, 31 - int(float(e.y-self.border)/self.fh)+1
			elif e.x > self.width - 2*self.fw:
				return 2, 31 - int(float(e.y-self.border)/self.fh)+1
		return 0,0	# Implies Invalid Field


	def xyfromi(self,i):		# Calculates the xy coordinates for placing widgets
		if i <= 16:
			return 1, self.border + (i-1)*self.fh + self.fh/2
		elif i <= 32:
			return self.width - self.fw, self.height - (i-16)*self.fh + self.fh/2 - self.border

	def save(self):
		self.eye.save(self.trace,'explore.dat')
		showhelp(_('Traces saved to explore.dat'))

	def xmgrace(self):
		if self.eye.grace(self.trace) == False:
			showhelp(_('Could not find Xmgrace or Pygrace. Install them'),'red')


	def do_fft(self):
		global delay, NP, NC, EYEMATH
		if EYEMATH == False:
			showhelp(_('Could not find scipy package. Install it'),'red')
			return
		if self.trace == None: return
		transform = []
		for xy in self.trace:
			fr,tr = eyemath.fft(xy[1], delay * NC * 0.001)
			transform.append([fr,tr])
		self.eye.save(transform, 'exploreFFT.dat')
		self.eye.grace(transform, _('freq'), _('power'))
		showhelp(_('Fourier transform Saved to exploreFFT.dat.'))

	def labset(self,i,s):
		self.tw[i].config(text=s)

	def twset(self,i,s):
		self.tw[i].delete(0,END)
		self.tw[i].insert(0,s)

	def process(self,e):							# Enter key in any of the Text Entry Fields
		for i in range(self.NSIG):
			if self.tw[i] == e.widget:				# Look for the widget where Enter is pressed			
				fld = i
				break
		msg = ''
		val = self.get_fieldvalue(fld)					# Get the value entered by the user
		if val == None:	
			return
		elif fld == 6:					# Set SQR1
			freq = self.eye.set_sqr1(val)
			self.twset(fld,'%5.1f'%freq)
		elif fld == 7:					# Set SQR2
			self.eye.set_sqr2(val)
			freq = self.eye.get_sqr2()
			if freq > 0:
				self.labset(8,'%5.1f Hz'%freq)
				self.NOSQR2 = False
			else:
				self.labset(8, _('0 Hz'))
				self.NOSQR2 = True
		elif fld == 10:					# Set Pulse duty cycle
			ds = self.eye.set_pulse(val)
			self.twset(fld,'%5.1f'%ds)
		elif fld == 28:					# Set Current
			self.eye.set_current(val)
			self.twset(fld,'%5.3f'%val)
		elif fld == 30:
			self.eye.set_voltage(0,val)
			self.twset(i,'%5.3f'%val)
		elif fld == 31:
			self.eye.set_voltage(1,val)
			self.twset(fld, '%5.3f'%val)

	def clicked(self,e):
		if self.poped == True:		# Remove poped menu by cicking else where
			menu.unpost()
			self.poped = False
		a,i = self.ifromxy(e)
		if a == 1:
			showhelp(help[i])
		#print e.x, e.y, a, i


	def duty_cycle(self):
		hi = self.eye.r2ftime(0,0)
		if hi > 0:
			lo = self.eye.f2rtime(0,0)
			ds = 100*hi/(hi+lo)
			self.labset(1, '%5.2f %%'%(ds))
		else:
			self.labset(1,_('0 Hz'))

	def checked(self, i):		# Clicked Checkbutton
		val  = self.doutval[i].get()
		if val == 0:
			self.OUTMASK &= ~(1 << i)
			self.doutCB[i].config(text=_('LO'),bg='gray')
		elif val == 1:
			self.OUTMASK |= (1 << i)
			self.doutCB[i].config(text=_('HI'), bg='green')
		self.eye.write_outputs(self.OUTMASK & 3)


	def routine_work(self):
		global NP, delay, chanmask, measure, lissa, EYEMATH
		s = ''
		self.trace = []
								# In the final stage, move this to a Try block.
		if lissa == True:
			t,v,tt,vv = self.eye.capture01(NP,delay)
			g.delete_lines()
			g.setWorld(-5,-5,5,5,_('mS'),_('V'))
			g.line(v,vv)
			self.trace.append([v,vv])
		elif chanmask == 1 or chanmask == 2:				# Waveform display code 
			t, v = self.eye.capture(chanmask-1,NP,delay)
			g.delete_lines()
			g.line(t,v,chanmask-1)
			self.trace.append([t,v])
		elif chanmask == 3:
			t,v,tt,vv = self.eye.capture01(NP,delay)
			g.delete_lines()
			g.line(t,v)
			g.line(tt,vv,1)
			self.trace.append([t,v])
			self.trace.append([tt,vv])
		if measure == 1 and EYEMATH == False:
			showhelp(_('python-scipy not installed. Required for data fitting'),'red')
		if measure == 1 and lissa == False and EYEMATH == True:		# Curve Fitting
			if chanmask == 1 or chanmask == 2:			
				fa = eyemath.fit_sine(t, v)
				if fa != None:
					#g.line(t,fa[0], 8)
					rms = self.eye.rms(v)
					f0 = fa[1][1] * 1000
					s = _('CH%d %5.2f V , F= %5.2f Hz') %(chanmask>>1, rms, f0)
				else:
					s = _('CH%d nosig ')%(chanmask>>1)

			elif chanmask == 3:	
				fa = eyemath.fit_sine(t,v)
				if fa != None:
					#g.line(t,fa[0],8)
					rms = self.eye.rms(v)
					f0 = fa[1][1]*1000
					ph0 = fa[1][2]
					s += _('CH0 : %5.2f V , %5.2f Hz ') %(rms, f0)
				else:
					s += _('CH0: no signal ')
				fb = eyemath.fit_sine(tt,vv)
				if fb != None:
					#g.line(tt,fb[0],8)
					rms = self.eye.rms(vv)
					f1 = fb[1][1]*1000
					ph1 = fb[1][2]
					s = s + _('| CH1 %5.2f V , %5.2f Hz') %(rms, f1)
					if fa != None and abs(f0-f1) < f0*0.1:
						s = s + _(' | dphi= %5.1f')%( (ph1-ph0)*180.0/math.pi)
				else:
					s += _('| CH1:no signal ')
		msgwin.config(text=s)			# CRO part over	

		v = self.eye.get_voltage(6)			# CS voltage
		self.labset(27, '%5.3f V'%v)					
		v = self.eye.get_voltage(0)			# A0
		self.labset(26, '%5.3f V'%v)
		v = self.eye.get_voltage(1)			# A1
		self.labset(25, '%5.3f V'%v)
		v = self.eye.get_voltage(2)			# A2
		self.labset(24, '%5.3f V'%v)
		v = self.eye.get_voltage(4)			# SENSOR
		self.labset(23, '%5.3f V'%v)

		res = self.eye.read_inputs()		# Set the color based on Input Levels
		if res & 1:								# ID0
			self.tw[1].config(bg = pgreen)				
		else:
			self.tw[1].config(bg = 'gray')		
		if res & 2:								# ID1
			self.tw[2].config(bg = pgreen)		
		else:
			self.tw[2].config(bg = 'gray')	
		if res & 4:								# T15 input
			self.tw[15].config(bg = pgreen)		
		else:
			self.tw[15].config(bg = 'gray')	
		if res & 8:								# Sensor Input
			self.tw[22].config(bg = pgreen)		
		else:
			self.tw[22].config(bg = 'gray')	

		if self.NOSQR2 == False:
			freq = self.eye.get_sqr2()
			if freq > 0:
				self.labset(8,'%5.1f Hz'%freq)
			else:
				self.labset(8, _('0 Hz'))
				self.NOSQR2 = True

		if self.NOSF == False:
			freq = self.eye.sensor_frequency()
			if freq > 0:
				self.labset(22,'%5.1f Hz'%freq)
			else:
				self.labset(22, _('0 Hz'))
				self.NOSF = True

	def update(self):
		try:
			self.routine_work()
		except:
			showhelp(_('Transaction Error.'),'red')
		root.after(TIMER, self.update)
#----------------------------------------Panel class ends ------------------------------------------

VPERDIV = 1.0		# Volts per division, vertical scale
delay = 10			# Time interval between samples
NP = 100			# Number of samples
NC = 1				# Number of channels
chanmask = 1		# 01, 10 or 11 binary
measure  = 0
lissa = 0

def showhelp(s,col='black'):
	helpwin.delete(1.0, END)
	helpwin.config(fg=col)
	helpwin.insert(END, s)

def set_vertical(w):
	global delay, NP, NC, VPERDIV
	divs = [1.1, 1.0, 0.5, 0.2, 0.1, 0.05, 0.02]
	VPERDIV = divs[int(vpd.get())]
	g.setWorld(0,-5*VPERDIV, NP * delay * 0.001, 5*VPERDIV,_('mS'),_('V'))

def set_timebase(w):
	global delay, NP, NC, VPERDIV
	divs = [0.050, 0.100, 0.200, 0.500, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0]
	msperdiv = divs[int(timebase.get())]
	totalusec = int(msperdiv * 1000 * 10)
	NP = 200								# Assume 100 samples to start with
	delay = int(totalusec/100)				# Calculate delay
	if delay < 10:
		sf = 10/delay
		delay = 10
		NP = NP/sf * NC
	elif delay > 1000:
		sf = delay/1000
		delay = 1000
		NP = NP * sf / NC
	g.setWorld(0,-5*VPERDIV, NP * delay * 0.001, 5*VPERDIV,_('mS'),_('V'))
	#print NP, NC, delay

def select_chan():
	global chanmask, measure, NC
	chanmask = CH0.get() | (CH1.get() << 1)
	measure = FIT.get()
	if chanmask == 3: 
		NC =2
	else:
		NC = 1

def lissa_mode():
	global lissa,delay, NP, NC, VPERDIV
	lissa = LIZ.get()
	if lissa == 1:
		lissa = True
	else:
		g.setWorld(0,-5*VPERDIV, NP * delay * 0.001, 5*VPERDIV,_('mS'),_('V'))	# Restore old scale
		lissa = False

#-----------------------------main program starts here-----------------------------
for k in range(20):		# Test the hardware availability by by running another program.
	stat,out = commands.getstatusoutput('python '+ eyeplot.abs_path() + 'hwtest.py')
	print stat
	if stat == 0:
		break

pe = eyes.open()			# Try several times to make a connection
root = Tk()

left = Frame(root)			# Divide root window into Left and Right
left.pack(side=LEFT, anchor = S)
right = Frame(root)
right.pack(side = LEFT, anchor = S, fill = Y),

w=eyePanel(left, pe, WIDTH, HEIGHT)		# Panel photograph to the Left Panel
g = eyeplot.graph(right, WIDTH*1.05, HEIGHT*2./3,color = 'white', labels=False)  # Plot window 
g.setWorld(0,-5*VPERDIV, NP * delay * 0.001, 5*VPERDIV,_('mS'),_('V'))

cf = Frame(right)						# Command Frame, inside the right frame, below plot window
cf.pack(side=TOP, anchor = NW)
l = Label(cf, text=_('mS/div'))
l.pack(side=LEFT, anchor = SW )
timebase = Scale(cf,command = set_timebase, orient=HORIZONTAL, length=50, showvalue=False,\
	from_ = 0, to=9, resolution=1)
timebase.pack(side=LEFT, anchor = SW)
timebase.set(2)

'''
l = Label(text = _('Volt/div'))
vpd = Scale(cf,command = set_vertical, orient=HORIZONTAL, length=50, showvalue=False,\
	from_ = 0, to=2, resolution=1)
vpd.pack(side=LEFT, anchor = SW)
vpd.set(1)
'''

CH0 = IntVar()
cb0 = Checkbutton(cf,text ='A0', command=select_chan, variable=CH0, fg = 'black')
cb0.pack(side=LEFT, anchor = SW)
CH0.set(1)
CH1 = IntVar()
cb1 = Checkbutton(cf,text ='A1', command=select_chan, variable=CH1, fg = 'red')
cb1.pack(side=LEFT, anchor = SW)
CH1.set(0)
LIZ = IntVar()
liz = Checkbutton(cf,text =_('LIZ'), command=lissa_mode, variable=LIZ, fg = 'black')
liz.pack(side=LEFT, anchor = SW)
LIZ.set(0)

FIT = IntVar()
b=Checkbutton(cf,text=_('FIT'), command = select_chan, variable=FIT, fg= 'black')
b.pack(side=LEFT, anchor = SW)
b = Button(cf,text =_('Save'), command=w.save)
b.pack(side=LEFT, anchor = SW)
b = Button(cf,text =_('FT'), command=w.do_fft)
b.pack(side=LEFT, anchor = SW)

b = Button(cf,text =_('XM'), command=w.xmgrace)
b.pack(side=LEFT, anchor = SW)
b = Button(cf,text =_('QUIT'), command=sys.exit)
b.pack(side=LEFT, anchor = SW)

mf = Frame(right)				# Message Frame below command frame.
mf.pack(side=TOP, anchor = SW)
msgwin = Label(mf,text = _('Messages'), fg = 'blue')
msgwin.pack(side=LEFT, anchor = SW)

f = Frame(right, bg= 'white')
f.pack(side = TOP)
font = tkFont.Font(family = 'helvetica', size = 12)
scrollbar = Scrollbar(f)
scrollbar.pack(side=RIGHT, fill=Y)
f.pack(side = TOP, fill = BOTH, expand = 1)
helpwin = Text(f, width = 45, height = 5, font = font, fg = 'black', bg = 'white', spacing2 = 0,\
		wrap=WORD, yscrollcommand=scrollbar.set)
helpwin.pack(side = TOP, fill = BOTH, expand = 1)
scrollbar.config(command=helpwin.yview)
showhelp(help[0])

#------------------------popup menu ---------------------------
expts = [ 
[_('Resistor IV'),'resistor_iv'],
[_('RC Circuit'),'RCcircuit'],
[_('RL Circuit'),'RLcircuit'],
[_('RLC Discharge'),'RLCdischarge'],
[_('EM Induction'),'induction'],
[_('Diode IV'),'diode_iv'],
[_('LED IV'),'LED_iv'],
[_('Transistor CE'),'transistor'],
[_('Frequency Response'),'freq-response'],
[_('Velocity of Sound') , 'velocity-sound'],
[_('Interference of Sound') , 'interference-sound'],
[_('Photo-Transistor CE'),'phototransistor'],
[_('Rod Pendulum') , 'rodpend'],
[_('Gravity TOF'), 'gravity_tof'],
[_('Pendulum Wavefrorm'),'pendulum'],
[_('40 kHz Piezo TOF'),'usound_tof'],
[_('PT100 Sensor'), 'pt100'],
[_('Temp Comptroller'), 'temp-controller'],
[_('Data Logger'), 'logger'],
[_('CRO'),'cro'],
[_('AM and FM'), 'amfm'],
[_('Music'),'janagana'],
[_('Calibrate'),'calibrate']
 ]


def run_expt(expt):
	global w
	if os.name == 'nt':		# For windows OS
		w.eye.fd.close()	# Close hardware port
		cmd = sys.executable + ' ' + eyeplot.abs_path() + expt+'.py'
		os.system(cmd)
		w.eye = eyes.open()	# Open hardware port again
		showhelp(_('Finished ') + expt)
	else:
		#print abs_path() + expt+'.py'
		stat,out = commands.getstatusoutput('python '+ eyeplot.abs_path() + expt+'.py')
		if stat != 0:
			showhelp(out)
		else:
			showhelp(_('Finished "')+expt+'.py"')
	w.eye.disable_actions()

menu = Menu(w.panel, tearoff=0)
for k in range(len(expts)):
	text = expts[k][0]
	cmd = expts[k][1]
	#print text, cmd
	menu.add_command(label=text, background= 'ivory', command = lambda expt=cmd :run_expt(expt))

# Check Hardware
if pe == None:	
	root.title(_('EYES Hardware NOT found.'))
	showhelp(_('EYES Hardware Not Found.\nRe-Connect USB cable and restart the program.'), 'red')
	root.mainloop()
	sys.exit()
else:
	root.title(_('EYES Hardware found on ') + str(pe.device))
	pe.write_outputs(0)
	pe.disable_actions()
	pe.loadall_calib()
	root.after(TIMER,w.update)
root.mainloop()
  
