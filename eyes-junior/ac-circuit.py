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
import expeyes.eyesj as eyes, expeyes.eyeplot as eyeplot, expeyes.eyemath as eyemath, time, os, commands, math

bgcol = 'ivory'

BUFSIZE = 1800		# uC buffer size in bytes
TIMER = 100
LPWIDTH = 75
WIDTH  = 600   		# width of drawing canvas
HEIGHT = 400   		# height 
VPERDIV = 1.0		# Volts per division, vertical scale
NP = 400			# Number of samples
NC = 1				# Number of channels
MINDEL = 8		
delay = MINDEL		# Time interval between samples
CMERR = False
data = [ [[],[]],[[],[]],[[],[]] ]  # 3 [t,v] lists

def msg(s, col='blue'):
	msgwin.config(text=s, fg=col)

def set_timebase(w):
	global delay, NP, NC, VPERDIV, chan4
	divs = [0.100, 0.200, 0.500, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0,100.0]
	msperdiv = divs[int(timebase.get())]
	totalusec = int(msperdiv * 1000 * 10)
	NC = 2
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
	g.setWorld(0,-5*VPERDIV, NP * delay * 0.001, 5*VPERDIV,_('mS'),_('V'))
	msg(_('X-scale changed to %d mS/div.Capturing %d samples with %d usec spacing') %(msperdiv,NP,delay))


def update():
	global delay, NP, delay, VPERDIV,data, CMERR, Freq
	if CMERR == True:
		CMERR = False 
		msg('')
	try:
		t0,v0,t1,v1 = p.capture2_hr(1,2,NP,delay)
		g.delete_lines()
		vp.delete_lines()
		g.line(t0,v0,0)
		g.line(t1,v1,1)
		data[0][0] = t0
		data[0][1] = v0
		data[1][0] = t1
		data[1][1] = v1

		t2 = [0]*NP		# Calculate voltages A1 - A2
		v2 = [0]*NP
		for k in range(NP):
			t2[k] = t1[k]
			v2[k] = v0[k] - v1[k]
		g.line(t2,v2,2)
		data[2][0] = t2
		data[2][1] = v2
		# fitting
		fa = eyemath.fit_sine(t0,v0)
		fb = eyemath.fit_sine(t1,v1)
		fc = eyemath.fit_sine(t2,v2)
		if fa != None and fb != None and fc != None:
			rmsv0 = p.rms(v0)
			dv0 = 100 * abs( (rmsv0-p.rms(fa[0])) /rmsv0 )
			rmsv1 = p.rms(v1)
			dv1 = 100 * abs( (rmsv1-p.rms(fb[0])) /rmsv1 )
			a0 = fa[1][0]
			a1 = fb[1][0]
			a2 = fc[1][0]
			pd01 = math.atan(a2/a1)
			pd01_fit = fb[1][2]-fa[1][2]
			sign = pd01_fit / abs(pd01)
			pherr = abs(pd01) - abs(pd01_fit)
			pherr = abs(pherr/pd01) * 100
			#print 180./math.pi*pd01, 180./math.pi*pd01_fit, pherr
			if dv0 > 2.0 or dv1 > 2.0 or pherr > 100.0:		# Check for error in FIT
				g.line(t0, fa[0], col = 6)
				g.line(t1, fb[0], col = 5)
				msg(_('Error in Fit (A0: Black &Yellow, A1-Red & Green). Try Changing X-scale'))
			# Display even if there is an error in fitted results
			fr = fa[1][1]*1000		
			Fit0.config(text = _('Frequency = %5.1f Hz') %fr)
			Fit1.config(text = _('A1:Total voltage = %5.2f V') %(a0))
			Fit2.config(text = _('A2:Voltage across R = %5.2f V') %(a1))
			Fit3.config(text = _('A1-A2:Voltage across LC = %5.2f V') %(a2))
			Fit4.config(text = _('Phase Shift = %5.1f deg') %(pd01_fit*180./math.pi))
			#Fit5.config(text = _('arc tan(Vx/Vr)= %5.1f deg') %(pd01*180./math.pi))
			vp.line((0,0),(0, a1), col =1)
			rx = a0 * math.sin(pd01_fit)
			ry = a0 * math.cos(pd01_fit) 
			vp.line((0,rx),(0,ry))
			vp.line((0,sign*a2),(0, 0), col=2)
		else:
			msg(_('Curve Fitfing failed. Try changing X scale'))
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
	if p.grace(data) == False:
		msg(_('Could not find Xmgrace or Pygrace. Install them'),'red')
	else:
		msg(_('Traces send to Xmgrace'))


def calc():
	try:
		f = float(Freq.get())
		C = float(Cap.get())
		L = float(Ind.get())
		R = float(Res.get())
		Xl = 2*math.pi*f*L*1.e-3
		if C != 0:
			Xc = 1./(2*math.pi*f*C*1.e-6)
		else:
			Xc = 0.0
		dphi = math.atan( (Xc-Xl)/R)*180./math.pi
		s = _('XC = %5.1f   XL = %5.1f\nDphi = %5.1f degree') %(Xc, Xl, dphi)
		Calc2.config(text = s, fg='blue')
	except:
		Calc2.config(text = _('Wrong Input'), fg='red')

#=============================== main program starts here ===================================
p = eyes.open()
if p == None: sys.exit()
root = Tk()    
f = Frame(root)
f.pack(side=LEFT)
g = eyeplot.graph(f, width=WIDTH, height=HEIGHT)	# make plot objects using draw.disp
g.setWorld(0, -5, 20, 5,_('mS'),_('V'))

f1 = Frame(f)
f1.pack(side=TOP,  fill = BOTH, expand = 1)
Label(f1,text = _('mSec/div')).pack(side=LEFT, anchor = SW)		# Sliders for Adjusting Axes
timebase = Scale(f1,command = set_timebase, orient=HORIZONTAL, length=LPWIDTH, showvalue=False,\
	from_ = 0, to=9, resolution=1)
timebase.pack(side=LEFT, anchor = SW)
timebase.set(3)

Label(f1,text = _('Volt/div')).pack(side=LEFT, anchor = SW)
Vpd = Scale(f1,command = set_vertical, orient=HORIZONTAL, length=LPWIDTH, showvalue=False,\
	from_ = 0, to=3, resolution=1)
Vpd.pack(side=LEFT, anchor = SW)
Vpd.set(1)

Save = Button(f1,text=_('Save Traces to'), command = save_data)
Save.pack(side=LEFT, anchor=N)
Fname = Entry(f1, width=8)
Fname.pack(side=LEFT)
Fname.insert(0,'cro.txt')

Save = Button(f1,text=_('XmGrace'), command = xmgrace)
Save.pack(side=LEFT, anchor=N)
Quit = Button(f1,text=_('QUIT'), command = sys.exit)
Quit.pack(side=LEFT, anchor=N)

mf = Frame(f)
mf.pack(side=TOP,  fill = BOTH, expand = 1)
msgwin = Label(mf,text = _('Connect SINE to A1, R from A2 to GND. Inductor and/or Capacitor from A1 to A2.'), fg = 'blue')
msgwin.pack(side=LEFT)#, anchor = SW)

#========================= Right Side panel ===========================================
RFWIDTH = 150
rf = Frame(root, width = RFWIDTH, height = HEIGHT)
rf.pack(side=LEFT,  fill = BOTH, expand = 1)
vp = eyeplot.graph(rf, width=RFWIDTH, height=RFWIDTH, labels=True)	# make plot objects using draw.disp
vp.setWorld(-5, -5, 5, 5,'','')
Label(rf,text = _('Phasor Plot')).pack(side=TOP)

Fit0 = Label(rf, text = '', fg='magenta')
Fit0.pack(side = TOP, anchor = W)
Fit1 = Label(rf, text = '', fg='black')
Fit1.pack(side = TOP, anchor = W)
Fit2 = Label(rf, text = '', fg='red')
Fit2.pack(side = TOP, anchor = W)
Fit3 = Label(rf, text = '', fg='blue')
Fit3.pack(side = TOP, anchor = W)
Fit4 = Label(rf, text = '', fg='magenta')
Fit4.pack(side = TOP, anchor = W)
Fit5 = Label(rf, text = '', fg='magenta')
Fit5.pack(side = TOP, anchor = W)

Label(rf,text = _('Calculator')).pack(side=TOP, anchor=N)
f = Frame(rf)
f.pack(side=TOP, anchor = W)
Label(f,text = _('Freq=')).pack(side=LEFT)
Freq = Entry(f, width = 4)
Freq.pack(side=LEFT, anchor = N)
Freq.insert(0,'150')
Label(f,text = _('Hz R=')).pack(side=LEFT)
Res = Entry(f, width = 4)
Res.pack(side=LEFT, anchor = N)
Res.insert(0,'1000')
Label(f,text = _('Ohm')).pack(side=LEFT)

f = Frame(rf)
f.pack(side=TOP, anchor = W)
Label(f,text = _('C=')).pack(side=LEFT)
Cap = Entry(f, width = 4)
Cap.pack(side=LEFT, anchor = N)
Cap.insert(0,'1')
Label(f,text = _('uF. L=')).pack(side=LEFT)
Ind = Entry(f, width = 4)
Ind.pack(side=LEFT, anchor = N)
Ind.insert(0,'100')
Label(f,text = _('mH')).pack(side=LEFT)

Calc = Button(rf,text=_('Calculate XL, XC and Angle'),command = calc)
Calc.pack(side=TOP)
Calc2 = Label(rf,text = '')
Calc2.pack(side=TOP)
#---------------

eyeplot.pop_image('pics/ac-circuit.png', _('Study of AC Circuit'))
root.title(_('Study of AC Circuits'))
root.after(10,update)
root.mainloop()


