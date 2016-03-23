'''
expEYES Junior calibration program
Author  : Ajith Kumar B.P, bpajith@gmail.com
License : GNU GPL version 3
'''
from __future__ import print_function

import gettext, sys, os, os.path, time 
if sys.version_info.major==3:
        from tkinter import *
else:
        from Tkinter import *

sys.path=[".."] + sys.path

import expeyes.eyesj as eyes
import expeyes.eyeplot as eyeplot
import expeyes.eyemath as eyemath

gettext.bindtextdomain("expeyes")
gettext.textdomain('expeyes')
_ = gettext.gettext

from numpy import mean, zeros

def msg(s, col='blue'):
	msgwin.config(text=s, fg=col)

def save_calib():	# Saves scale factors of A1 & A2 to calibrationFile
	v = p.set_voltage(2.0)
	v1 = p.get_voltage(1)
	if abs(v1-v) > 0.1:
		msg(_('PVS is NOT connected to A1'),'red')
		return
	v2 = p.get_voltage(2)
	if(abs(v2-v) > 0.1):
		msg(_('PVS is NOT connected to A2'), 'red')
		return

	np = 10
	x = zeros(np)				# Calibrate A1 
	y  = zeros(np)
	iv = 50						# DAC binary value
	for k in range(np):
		p.write_dac(iv)
		time.sleep(0.01)
		x[k] = p.read_adc(1)				# binary from A1, after level shifting
		y[k] = p.read_adc(12)*p.refval/4095		# voltage at PVS (connected to A1)
		iv += 350
	xbar = mean(x)							# Calculate m & c for A1  , 12 bit
	ybar = mean(y)
	m1 = sum(y*(x-xbar)) / sum(x*(x-xbar))
	m1 = float(m1)
	c1 = ybar - xbar * m1
	c1 = float(c1)
	# Do some sanity check here
	ucm = 10.0/4095		# Uncalibrated values of m and c
	ucc = -5.0
	dm = ucm * 0.03			# maximum 3% deviation
	dc = 5 * 0.03
	if abs(m1 - ucm) > dm or abs(c1 - ucc) > dc:
		msg(_('Too much error in A1: m = %f  c=%f')%(m1,c1),'red')
		return

	iv = 10						# Calibrate A2
	for k in range(np):
		p.write_dac(iv)
		time.sleep(0.01)
		x[k] = p.read_adc(2)				# binary from A2, after level shifting
		y[k] = p.read_adc(12)*p.refval/4095	# voltage at PVS (connected to A2)			
		iv += 350
	xbar = mean(x)							# Calculate m & c for A1  , 12 bit
	ybar = mean(y)
	m2 = sum(y*(x-xbar)) / sum(x*(x-xbar))
	m2 = float(m2)
	c2 = ybar - xbar * m2
	c2 = float(c2)
	if abs(m2 - ucm) > dm or abs(c2 - ucc) > dc:	# Error check
		msg(_('Too much error in A2: m = %f  c=%f')%(m2,c2),'red')
		return
	print (m1,c1,m2,c2)
	if p.storeCF_a1a2(m1, c1, m2, c2) == None:	# Store to EEPROM
		msg(_('EEPROM write failed. Old Firmware ?'),'red')
		return	
	ss =_('m1 = %f   c1 = %6.3f\nm2 = %f   c2 = %6.3f')%(m1, c1, m2, c2)
	msg(_('A1&A2 Calibration Saved to EEPROM\n')+ss)
	print (ss)

#------------------------------------------------------------------------------
def save_calibref():	# Saves reference voltage
	try:
		v = float(Rref.get())
	except:
		msg(_('Enter the valid voltage'), 'red')
		return
	print (v)
	if (v < 4.950) or (v > 5.050):
		msg(_('Too much error in reference %5.3f voltage')%v, 'red')
		return
	if p.storeCF_ref(v) == None:					# Store to EEPROM
		msg(_('EEPROM write failed. Old Firmware ?'),'red')
		return
	else:
		msg(_('Calibrated Reference. Vref =%5.0f')%v )

#------------------------------------------------------------------------------
def save_calibsen():	# Saves scale factors of A1 & A2 to file 'eyesj.cal'
	v = p.get_voltage(5)
	try:
		r = float(Rsen.get())
		R = r * (5.0 - v) / v
	except:
		msg(_('Enter the R connected to SEN'), 'red')
		return
	print (R)
	if (R < 4950) or (R > 5250):
		msg(_('Wrong Resistor ??. Calculated Rp =%5.1f Ohm')%R, 'red')
		return
	if p.storeCF_sen(R) == None:					# Store to EEPROM
		msg(_('EEPROM write failed. Old Firmware ?'),'red')
		return
	else:
		msg(_('Calibrated SEN. Rp =%5.0f')%R )

#------------------------- Capacitance calibration ------------------------
socket_cap = 0

def measure_socketcap():
	global socket_cap
	sc = p.measure_cap_raw()
	if 10 < sc < 60:
		socket_cap = sc
		msg(_('Empty Socket is %5.1f pF')%socket_cap)
	else:
		msg(_('IN1 not empty'), 'red')

def save_calibcap():
	global socket_cap
	if socket_cap == 0:
		msg(_('Measure Socket capacitance first'), 'red')
		return
	try:
		creal = float(Cin.get())
	except:
		msg(_('Enter the C connected to IN1'), 'red')
		return
	try:
		cm = p.measure_cap_raw() - socket_cap
		error = creal/cm
	except:
		msg(_('Mesuring capacitor failed'),'red')
		return

	print (creal, cm, error, cm*error)
	if error < 0.7 or error > 1.3 or socket_cap > 60:	# Error check
		msg(_('Too much error: Socket C= %f CF=%f')%(socket_cap, error),'red')
		return
	if p.storeCF_cap(socket_cap, error) == None:		# Store to EEPROM
		msg(_('Write to EEPROM failed'),'red')
	else:
		msg(_('Saved: Socket C = %5.1f pF. CF = %5f %%')%(socket_cap, error))

#---------------------------------------------------------------------------------
root = Tk()
Label(root, text = _('Reference Calibration'),font=('Helvetica', 14),\
		fg='blue').pack(side=TOP)
f = Frame(root, relief = SUNKEN)
f.pack(side=TOP)
Label(f, text = _('Enter measured value of Vref')).pack(side=LEFT)
Refval = StringVar()
Rref = Entry(f, width=6, textvariable=Refval)
Rref.pack(side=LEFT)
Refval.set('5.000')
Label(f, text = _('V')).pack(side=LEFT)
Button(root,text = _("and Click here to Set Reference"), \
	command = save_calibref).pack(side = TOP)
separator = Frame(height=2, bd=1, relief=SUNKEN)

separator.pack(fill=X, padx=5, pady=5)
Label(root, text = _('Calibration of Inputs A1 & A2'), fg='blue',\
			font=('Helvetica', 14)).pack(side=TOP)
Label(root, text = _('Connect PVS to both A1 and A2')).pack(side=TOP)
Button(root, text = _("Calibrate A1 & A2"), command = save_calib).pack(side = TOP)
separator = Frame(height=2, bd=1, relief=SUNKEN)
separator.pack(fill=X, padx=5, pady=5)

Label(root, text = _('Calibration of Resistor on SEN'),font=('Helvetica', 14),\
		fg='blue').pack(side=TOP)
f = Frame(root, relief = SUNKEN)
f.pack(side=TOP)
Label(f, text = _('Enter the Resistance connected from SEN to GND=')).pack(side=LEFT)
Rval = StringVar()
Rsen = Entry(f, width=6, textvariable=Rval)
Rsen.pack(side=LEFT)
#Rval.set('4984')
Label(f, text = _('Ohm')).pack(side=LEFT)
Button(root,text = _("and Click here to Calibrate SEN"), \
	command = save_calibsen).pack(side = TOP)
separator = Frame(height=2, bd=1, relief=SUNKEN)
separator.pack(fill=X, padx=5, pady=5)

Label(root, text = _('Calibration of IN1 for Capacitance'),font=('Helvetica', 14),\
		fg='blue').pack(side=TOP)
Button(root,text = _("First, Click Here without Capacitor on IN1"), \
	command = measure_socketcap).pack(side = TOP)
f = Frame(root)
f.pack(side=TOP)
Label(f, text = _('Enter the Capacitance connected to IN1')).pack(side=LEFT)
Cval = StringVar()
Cin = Entry(f, width=6, textvariable = Cval)
Cin.pack(side=LEFT)
#Cval.set('980')
Label(f, text = _('pF')).pack(side=LEFT)
Button(root,text = _("and Click Here to Calibrate IN1"), command = save_calibcap).pack(side = TOP)
separator = Frame(height=2, bd=1, relief=SUNKEN)
separator.pack(fill=X, padx=5, pady=5)

msgwin = Label(root, text = '')
msgwin.pack(side=TOP)
separator = Frame(height=2, bd=1, relief=SUNKEN)
separator.pack(fill=X, padx=5, pady=5)

Button(text = _("Exit"), command = sys.exit).pack(side = TOP)

p = expeyes.eyesj.open()
if p == None:
	root.title(_('EYES Junior Hardware not found'))
eyeplot.pop_image('pics/calibrate.png', _('Calibrate A1 & A2'))

cfvals = _('Existing calibration Data\n')+\
_('Ref=%5.3fV\nm1=%6.3f c1=%6.3f\nm2=%6.3f c2=%6.3f\nIN1: CF=%6.3f Socket=%6.3fpF\n SEN pullup=%6.1fOhm')\
		%(p.refval,p.m12[1], p.c[1],p.m12[2], p.c[2], p.cap_calib, p.socket_cap,p.sen_pullup)
msg(cfvals)
root.title(_('EYES Junior Calibration'))
root.mainloop()

