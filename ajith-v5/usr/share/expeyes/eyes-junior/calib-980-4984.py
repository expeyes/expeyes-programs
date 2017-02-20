'''
expEYES Junior calibration program
Author  : Ajith Kumar B.P, bpajith@gmail.com
License : GNU GPL version 3
'''

import gettext, sys, os, os.path

gettext.bindtextdomain("expeyes")
gettext.textdomain('expeyes')
_ = gettext.gettext

from numpy import mean, zeros
from Tkinter import *
import expeyes.eyesj, time, expeyes.eyeplot as eyeplot

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
		y[k] = p.read_adc(12)*5.0/4095		# voltage at PVS (connected to A1)
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
	dm = ucm * 0.02			# maximum 2% deviation
	dc = 5 * 0.02
	if abs(m1 - ucm) > dm or abs(c1 - ucc) > dc:
		msg(_('Too much error in A1: m = %f  c=%f')%(m1,c1),_('red'))
		return

	iv = 10						# Calibrate A2
	for k in range(np):
		p.write_dac(iv)
		time.sleep(0.01)
		x[k] = p.read_adc(2)				# binary from A2, after level shifting
		y[k] = p.read_adc(12)*5.0/4095	# voltage at PVS (connected to A2)			
		iv += 400
	xbar = mean(x)							# Calculate m & c for A1  , 12 bit
	ybar = mean(y)
	m2 = sum(y*(x-xbar)) / sum(x*(x-xbar))
	m2 = float(m2)
	c2 = ybar - xbar * m2
	c2 = float(c2)
	if abs(m2 - ucm) > dm or abs(c2 - ucc) > dc:	# Error check
		msg(_('Too much error in A2: m = %f  c=%f')%(m2,c2),_('red'))
		return
	print m1,c1,m2,c2
	if p.storeCF_a1a2(m1, c1, m2, c2) == None:	# Store to EEPROM
		msg(_('EEPROM write failed. Old Firmware ?'),_('red'))
		return	
	ss =_('m1 = %f   c1 = %6.3f\nm2 = %f   c2 = %6.3f')%(m1, c1, m2, c2)
	msg(_('A1&A2 Calibration Saved to EEPROM\n')+ss)
	print ss

#------------------------------------------------------------------------------
def save_calibsen():	# Saves scale factors of A1 & A2 to file 'eyesj.cal'
	v = p.get_voltage(5)
	try:
		r = float(Rsen.get())
		R = r * (5.0 - v) / v
	except:
		msg(_('Enter the R connected to SEN'), _('red'))
		return
	print R
	if (R < 4950) or (R > 5250):
		msg(_('Wrong Resistor ??. Calculated Rp =%5.1f Ohm')%R, _('red'))
		return
	if p.storeCF_sen(R) == None:					# Store to EEPROM
		msg(_('EEPROM write failed. Old Firmware ?'),_('red'))
		return
	else:
		msg(_('Calibrted SEN. Rp =%5.0f')%R )

#------------------------- Capacitance calibration ------------------------
socket_cap = 0

def measure_socketcap():
	global socket_cap
	sc = p.measure_cap_raw()
	if 20 < sc < 50:
		socket_cap = sc
		msg(_('Empty Socket is %5.1f pF')%socket_cap)
	else:
		msg(_('IN1 not empty'), _('red'))

def save_calibcap():
	global socket_cap
	if socket_cap == 0:
		msg(_('Measure Socket capacitance first'), _('red'))
		return
	try:
		creal = float(Cin.get())
	except:
		msg(_('Enter the C connected to IN1'), _('red'))
		return
	try:
		cm = p.measure_cap_raw() - socket_cap
		error = creal/cm
	except:
		msg(_('Mesuring capacitor failed'),_('red'))
		return

	print creal, cm, error, cm*error
	if error < 0.85 or error > 1.15 or socket_cap > 50:	# Error check
		msg(_('Too much error: Socket C= %f CF=%f')%(socket_cap, error),_('red'))
		return
	if p.storeCF_cap(socket_cap, error) == None:		# Store to EEPROM
		msg(_('Write to EEPROM failed'),_('red'))
	else:
		msg(_('Saved: Socket C = %5.1f pF. CF = %5f %%')%(socket_cap, error))

#---------------------------------------------------------------------------------
root = Tk()
Label(root, text = _('Calibration of Inputs A1 & A2'), fg=_('blue'),\
			font=(_('Helvetica'), 14)).pack(side=TOP)
Label(root, text = _('Connect PVS to both A1 and A2')).pack(side=TOP)
Button(root, text = _("Calibrate A1 & A2"), command = save_calib).pack(side = TOP)
separator = Frame(height=2, bd=1, relief=SUNKEN)
separator.pack(fill=X, padx=5, pady=5)

Label(root, text = _('Calibration of Resistor on SEN'),font=(_('Helvetica'), 14),\
		fg=_('blue')).pack(side=TOP)
f = Frame(root, relief = SUNKEN)
f.pack(side=TOP)
Label(f, text = _('Enter the Resistance connected from SEN to GND=')).pack(side=LEFT)
Rval = StringVar()
Rsen = Entry(f, width=6, textvariable=Rval)
Rsen.pack(side=LEFT)
Rval.set('4984')
Label(f, text = _('Ohm')).pack(side=LEFT)
Button(root,text = _("and Click here to Calibrate SEN"), \
	command = save_calibsen).pack(side = TOP)
separator = Frame(height=2, bd=1, relief=SUNKEN)
separator.pack(fill=X, padx=5, pady=5)

Label(root, text = _('Calibration of IN1 for Capacitance'),font=(_('Helvetica'), 14),\
		fg=_('blue')).pack(side=TOP)
Button(root,text = _("First, Click Here without Capacitor on IN1"), \
	command = measure_socketcap).pack(side = TOP)
f = Frame(root)
f.pack(side=TOP)
Label(f, text = _('Enter the Capacitance connected to IN1')).pack(side=LEFT)
Cval = StringVar()
Cin = Entry(f, width=6, textvariable = Cval)
Cin.pack(side=LEFT)
Cval.set('980')
Label(f, text = _('pF')).pack(side=LEFT)
Button(root,text = _("and Click Here to Calibrate IN1"), command = save_calibcap).pack(side = TOP)
separator = Frame(height=2, bd=1, relief=SUNKEN)
separator.pack(fill=X, padx=5, pady=5)

msgwin = Label(root, text = 'calibration program')
msgwin.pack(side=TOP)
separator = Frame(height=2, bd=1, relief=SUNKEN)
separator.pack(fill=X, padx=5, pady=5)

Button(text = _("Exit"), command = sys.exit).pack(side = TOP)

p = expeyes.eyesj.open()
if p == None:
	root.title(_('EYES Junior Hardware not found'))
eyeplot.pop_image('pics/calibrate.png', _('Calibrate A1 & A2'))
root.title(_('EYES Junior Calibration'))
root.mainloop()

