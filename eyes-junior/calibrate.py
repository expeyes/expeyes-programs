'''
expEYES Junior calibration program
Author  : Ajith Kumar B.P, bpajith@gmail.com
License : GNU GPL version 3
'''

import gettext, sys, os, os.path

gettext.bindtextdomain("expeyes")
gettext.textdomain('expeyes')
_ = gettext.gettext

#Path to the calibration file
if sys.platform.startswith('linux'):
	calibrationDir=os.path.expanduser('~/.local/share/data/expeyes')
else:
	calibrationDir="."
if not os.path.isdir(calibrationDir):
	os.makedirs(calibrationDir)
calibrationFile=os.path.abspath(os.path.join(calibrationDir,'eyesj.cal'))

from numpy import mean, zeros
from Tkinter import *
import expeyes.eyesj, time, expeyes.eyeplot as eyeplot

def msg(s, col='blue'):
	msgwin.config(text=s, fg=col)

def save_calib():	# Saves scale factors of A1 & A2 to calibrationFile
	v = p.set_voltage(2)
	v1 = p.get_voltage(1)
	if abs(v1-v) > 0.1:
		msg(_('PVS is NOT connected to A1%f %f') %(v, v1),'red')
		return
	v2 = p.get_voltage(2)
	if(abs(v2-v) > 0.1):
		msg(_('PVS is NOT connected to A2%f %f') %(v, v2),'red')
		return

	np = 10
	x = zeros(np)
	y  = zeros(np)
	iv = 10						# Calibrate A1 
	for k in range(np):
		p.write_dac(iv)
		time.sleep(0.01)
		x[k] = p.read_adc(1)				# binary from A1, after level shifting
		y[k] = p.read_adc(12)*5.0/4095	# voltage at PVS (connected to A2)
		iv += 400
	xbar = mean(x)							# Calculate m & c for A1  , 12 bit
	ybar = mean(y)
	m0 = sum(y*(x-xbar)) / sum(x*(x-xbar))
	c0 = ybar - xbar * m0
	p.m12[1] = float(m0)
	p.m8[1] = float(m0) * 4095./255
	p.c[1] = float(c0)
	iv = 10						# Calibrate A2
	for k in range(np):
		p.write_dac(iv)
		time.sleep(0.01)
		x[k] = p.read_adc(2)				# binary from A2, after level shifting
		y[k] = p.read_adc(12)*5.0/4095	# voltage at PVS (connected to A2)			
		iv += 400
	xbar = mean(x)							# Calculate m & c for A1  , 12 bit
	ybar = mean(y)
	m0 = sum(y*(x-xbar)) / sum(x*(x-xbar))
	c0 = ybar - xbar * m0
	p.m12[2] = float(m0)
	p.m8[2] = float(m0) * 4095./255
	p.c[2] = float(c0)
	f = open(calibrationFile , 'w')
	ss = '%f %f %f %f'%(p.m12[1],p.c[1],p.m12[2],p.c[2])
	print ss
	f.write(ss)
	f.close()
	msg(_('Calibrated: ')+ss)

root = Tk()
Label(text = _('Connect PVS to both A1 and A2')).pack(side=TOP)
Button(text = _("Calibrate"), command = save_calib).pack(side = TOP)
msgwin = Label(root, text = '')
msgwin.pack(side=TOP)
Button(text = _("Exit"), command = sys.exit).pack(side = TOP)
p = expeyes.eyesj.open()
if p == None:
	root.title(_('EYES Junior Hardware not found'))
eyeplot.pop_image('pics/calibrate.png', _('Calibrate A1 & A2'))
root.title(_('EYES Junior Calibration: PVS should be conected to A1 & A2'))
root.mainloop()

