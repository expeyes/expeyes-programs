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
	calibrationDir=os.path.expanduser('~/.expeyes')
else:
	calibrationDir="."
if not os.path.isdir(calibrationDir):
	os.makedirs(calibrationDir)
calibrationFile=os.path.abspath(os.path.join(calibrationDir,'eyesj.cal'))
calibrationFileSEN=os.path.abspath(os.path.join(calibrationDir,'eyesj-sen.cal'))
calibrationFileCAP=os.path.abspath(os.path.join(calibrationDir,'eyesj-cap.cal'))

from numpy import mean, zeros
from Tkinter import *
import expeyes.eyesj, time, expeyes.eyeplot as eyeplot

def msg(s, col='blue'):
	msgwin.config(text=s, fg=col)

def save_calib():	# Saves scale factors of A1 & A2 to calibrationFile
	v = p.set_voltage(2)
	v1 = p.get_voltage(1)
	if abs(v1-v) > 0.1:
		msg(_('PVS is NOT connected to A1'),'red')
		return
	v2 = p.get_voltage(2)
	if(abs(v2-v) > 0.1):
		msg(_('PVS is NOT connected to A2'), 'red')
		return

	vs = 0.0
	while vs < 5.1:
		v = p.set_voltage(vs)
		v1 = p.get_voltage(1)
		v2 = p.get_voltage(2)
		e1 = (v - v1)*1000
		e2 = (v - v2)*1000
		ss = _('PVS:%6.3f   Er1 = %3.0f  Er2= %3.0f mV\n')%(v,e1,e2)
		Out.insert(END, ss)
		vs += .5

root = Tk()
Label(root, text = _('Verification of Inputs A1 & A2'), fg=_('blue')).pack(side=TOP)
Label(root, text = _('Connect PVS to both A1 and A2')).pack(side=TOP)
Button(root, text = _("Verify A1 & A2"), command = save_calib).pack(side = TOP)
separator = Frame(height=2, bd=1, relief=SUNKEN)
Out = Text(bg= 'white', width = 40, height = 12)
Out.pack(side = TOP)
separator.pack(fill=X, padx=5, pady=5)

Button(text = _("Exit"), command = sys.exit).pack(side = TOP)

p = expeyes.eyesj.open()
if p == None:
	root.title(_('EYES Junior Hardware not found'))
eyeplot.pop_image('pics/calibrate.png', _('Calibrate A1 & A2'))
root.title(_('EYES Junior: Connect PVS to A1 & A2'))
print p.measure_cap()
root.mainloop()

