'''
expEYES program
Author  : Ajith Kumar B.P, bpajith@gmail.com
License : GNU GPL version 3
'''

import gettext
gettext.bindtextdomain("expeyes")
gettext.textdomain('expeyes')
_ = gettext.gettext

from numpy import *
from Tkinter import *
import expeyes.eyes as eyes, time


cpoints = [4.0, 3.0, 2.0, 1.0, -1.0, -2.0, -3.0, -4.0] # between -5 and +5 only
NP = len(cpoints)
setVar  = []
mesVar  = []
ADlab0  = []
ADlab1  = []
DAlab   = []
Measured= [False]*NP
ERRMAX  = 5.0   # maximum error expected without calibration
BPV = 0			# bipolar DAC

def msg(s, col = 'black'):
	msgwin.config(text=s, fg=col)

def setvoltage(n):
	Measured[n] = False
	v = cpoints[n]
	da = p.set_voltage(BPV,v)
	dabin[n] = da				#set voltage returns the binary number set
	ss = '(%4.0f)'%da
	DAlab[n].config(text = ss, fg='blue')
	time.sleep(0.1)

	asum = 0
	for k in range(10):
		asum += p.read_adc(0)
	ad0 = float(asum)/10
	error = abs(ad0-da)/da*100
	if error < ERRMAX:
		adbin0[n] = ad0
		ADlab0[n].config(text = '(%4.0f)'%ad0, fg='blue')
		ss =_('Point %5.3fV. Deviation A0 %5.2f%%') %(v,error)
	else:
		msg(_('ERROR: Check BPV to A0 connection'), 'red')
		return

	asum = 0
	for k in range(10):
		asum += p.read_adc(1)
	ad1 = float(asum)/10	
	error = abs(ad1-da)/da*100
	if error < ERRMAX:
		adbin1[n] = ad1
		ADlab1[n].config(text = '(%4.0f)'%ad1, fg='blue')
		ss +=' A1 %5.2f%%'%(error)
	else:
		msg(_('ERROR: Check BPV to A1 connection'))
		return
	Measured[n] = True
	msg(ss,'blue')

def calib():
	for k in range(NP):
		if Measured[k] == False:
			msg(_('ERROR : Point %5.3f Volts NOT done') %cpoints[k], 'red')
			return
		mv = float(mesVar[k].get())
		sv = cpoints[k]
		print sv, abs(sv-mv)
		if abs(sv-mv) > 0.1:
			msg(_('Readback for %5.3f V point = %5.3f V NOT GOOD') %(sv,mv), 'red')
			return
		advolts[k] = mv
		print cpoints[k], dabin[k], mv, adbin0[k], adbin1[k]

	x = adbin0				# Calculate m & c for CH0
	y = advolts
	xbar = mean(x)
	ybar = mean(y)
	m0 = sum(y*(x-xbar)) / sum(x*(x-xbar))
	c0 = ybar - xbar * m0

	x = adbin1				# Calculate m & c for CH1
	y = advolts
	xbar = mean(x)
	ybar = mean(y)
	m1 = sum(y*(x-xbar)) / sum(x*(x-xbar))
	c1 = ybar - xbar * m1

	x = advolts				# m & c for -5V to +5V DAC
	y = dabin
	xbar = mean(x)
	ybar = mean(y)
	m8 = sum(y*(x-xbar)) / sum(x*(x-xbar))
	c8 = ybar - xbar * m8
	print _('ADC0 m & c '), m0,c0
	print _('ADC1 m & c '), m1,c1
	print _('DAC0 m & c '), m8,c8

	p.save_calib(0,m0,c0)		# Save it on EEPROM
	p.save_calib(1,m1,c1)		# Save it on EEPROM
	p.save_calib(8,m8,c8)		# Save it on EEPROM
	msg(_('DONE: (%7.6f,%5.3f)(%7.6f,%5.3f)(%5.1f,%5.1f)') %(m0,c0,m1,c1,m8,c8) ,'blue')

def verify(ch):
	p.load_calib(8)
	p.load_calib(ch)
	f = open('calib%d.dat'%ch,'w')
	v = -4.5
	while v <= 4.5:
		p.set_voltage(0,v)
		time.sleep(0.01)	
		rv = p.get_voltage(ch)		
		ss = '%10.3f %10.4f'%(v,v-rv)
		f.write(ss+'\n')
		print ss
		v = v + 0.1
	f.close()

p = eyes.open()
if p == None:
	sys.exit()

adbin0 	= zeros(NP,dtype=float)
adbin1 	= zeros(NP,dtype=float)
advolts = zeros(NP,dtype=float)
dabin   = zeros(NP,dtype=float)
davolts = zeros(NP,dtype=float)

root = Tk()


for k in range(NP):
	lv = Frame(root, padx = 5, pady = 5)
	lv.pack(side=TOP, fill = X)
	l = Label(lv, text = '(0000)', fg = 'black')
	l.pack(side = LEFT, fill = Y)
	DAlab.append(l)
	Set = Button(lv,text=_('Set %3.0f Volts')%cpoints[k], command = lambda arg=k : setvoltage(arg))
	Set.pack(side=LEFT)
	l = Label(lv, text = '(0000)', fg = 'black')
	l.pack(side = LEFT, fill = Y)
	ADlab0.append(l)
	l = Label(lv, text = '(0000)', fg = 'black')
	l.pack(side = LEFT, fill = Y)
	ADlab1.append(l)
	l = Label(lv, text = _('Measured ='),)
	l.pack(side = LEFT, fill = Y)
	mv = StringVar()
	mesVar.append(mv)
	e = Entry(lv, width = 8, textvariable = mv, fg = 'blue', bg = 'white')
	e.pack(side = LEFT, fill = Y)
	mesVar[k].set('%5.0f'%cpoints[k])

f = Frame(root, padx = 5, pady = 5)
f.pack(side=TOP, fill = X)
l = Label(f, text = _('First you MUST Connect BPV to A0 & A1.\nThen click on each "Set Volts Button",')+\
		_('Measure BPV with a 4.5 DMM and\n enter it in the "Measured=" Field.\n')+\
		_('IMPROPER USE MAY SPOIL THE CALIBRATION'), fg = 'blue')
l.pack(side = LEFT, fill = Y)


cmd = Frame(root, padx = 5, pady = 5)
cmd.pack(side=TOP, fill = X)
Cal = Button(cmd,text=_('Calibrate'), fg='red', command = calib)
Cal.pack(side=LEFT)

b = Button(cmd,text=_('Verify CH0'), command = lambda arg=0 : verify(arg))
b.pack(side=LEFT)
b = Button(cmd,text=_('Verify CH1'), command = lambda arg=1 : verify(arg))
b.pack(side=LEFT)
b = Button(cmd,text=_('QUIT'), command = sys.exit)
b.pack(side=LEFT)
f = Frame(root, padx = 5, pady = 5)
f.pack(side=TOP, fill = BOTH)
msgwin = Label(f, text = _('msg'))
msgwin.pack(side=LEFT)

root.title(_('AD/DA CALIBRATION. NOT FOR EVERYONE!!'))
root.mainloop()

