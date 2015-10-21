'''
expEYES program
Author  : Ajith Kumar B.P, bpajith@gmail.com
License : GNU GPL version 3
'''
from __future__ import print_function

import gettext
gettext.bindtextdomain("expeyes")
gettext.textdomain('expeyes')
_ = gettext.gettext

from Tkinter import *
import expeyes.eyes as eyes, expeyes.eyeplot as eyeplot, expeyes.eyemath as eyemath, time, sys, math

WIDTH  = 600   # width of drawing canvas
HEIGHT = 400   # height    

class PT100:
	tv = [ [], [] ]			# Lists for Readings
	TIMER = 500				# Time interval between reads
	MINY = 0				# Temperature range
	MAXY = 100
	running = False
	ccs_current = 1.0		# .5 mA
	Rg = 300.0				# 300 Ohm resistor
	calibrated = False
	bpdone = False
	fpdone = False

	def get_freezing(self):
		v = p.get_voltage(2)
		temp = self.v2t(v)
		print (temp)
		if -10 < temp < 10:
			self.BPvoltage = v
			self.fpdone = True
			self.msg(_('Voltage at Freezing Point is %5.3f V')%v)
		else:
			self.msg(_('Something wrong. Check the connection & Rg'))

	def get_boiling(self):
		v = p.get_voltage(2)
		temp = self.v2t(v)
		print (temp)
		if 90 < temp < 110:
			self.BPvoltage = v
			self.bpdone = True
			self.msg(_('Voltage at Boiling Point is %5.3f V')%v)
		else:
			self.msg(_('Something wrong. Check the connection & Rg'))

	def calibrate(self):
		if self.bpdone == True and self.fpdone == True:
			self.m = (100.0 - 0.0) / (self.BPvoltage - self.FPvoltage)
			self.c = self.FPvoltage
			self.calibrated = True
			self.msg(_('Calibration Done m = %5.3f, c = 5.3f')%(self.m, self.c))
		else:
			self.msg(_('Boiling & Freezing points to be measured first'))

	def v2t(self, v):			# Convert Voltage to Temperature for PT100
		gain = 1.0 + 10000./self.Rg
		r = v / gain / (self.ccs_current * 1.0e-3)  # mA to Ampere
		r0 = 100.0
		A = 3.9083e-3
		B = -5.7750e-7
		c = 1 - r/r0
		b4ac = math.sqrt( A*A - 4 * B * c)
		t = (-A + b4ac) / (2.0 * B)
		#print (r,t)
		return t

	def xmgrace(self):
		if self.running == True:
			return
		p.grace([self.tv])

	def start(self):
		self.running = True
		self.index = 0
		self.tv = [ [], [] ]
		try:
			p.set_current(self.ccs_current)
			self.MAXTIME = int(DURATION.get())
			self.MINY = int(TMIN.get())
			self.MAXY = int(TMAX.get())
			self.Rg = float(RG.get())
			g.setWorld(0, self.MINY, self.MAXTIME, self.MAXY,_('Time'),_('Volt'))
			self.TIMER = int(TGAP.get())
			Total.config(state=DISABLED)
			Dur.config(state=DISABLED)
			self.msg(_('Starting the Measurements'))
			root.after(self.TIMER, self.update)
		except:
			self.msg(_('Failed to Start'))

	def stop(self):
		self.running = False
		Total.config(state=NORMAL)
		Dur.config(state=NORMAL)
		self.msg(_('User Stopped the measurements'))

	def update(self):
		if self.running == False:
			return
		t,v = p.get_voltage_time(2)  # Read A2
		if len(self.tv[0]) == 0:
			self.start_time = t
			elapsed = 0
		else:
			elapsed = t - self.start_time
		self.tv[0].append(elapsed)
		if self.calibrated:
			temp = self.m * v + self.c		# Use the calibration 
		else:
			temp = self.v2t(v)
		print (v,temp)
		self.tv[1].append(temp)
		if len(self.tv[0]) >= 2:
			g.delete_lines()
			g.line(self.tv[0], self.tv[1])
		if elapsed > self.MAXTIME:
			self.running = False
			Total.config(state=NORMAL)
			Dur.config(state=NORMAL)
			self.msg(_('Completed the Measurements'))
			return 
		root.after(self.TIMER, self.update)

	def save(self):
		try:
			fn = filename.get()
		except:
			fn = 'pt100.dat'
		p.save([self.tv],fn)
		self.msg(_('Data saved to %s')%fn)

	def clear(self):
		if self.running == True:
			return
		self.nt = [ [], [] ]
		g.delete_lines()
		self.msg(_('Cleared Data and Trace'))

	def msg(self,s, col = 'blue'):
		msgwin.config(text=s, fg=col)

p = eyes.open()
p.loadall_calib()
p.disable_actions()
root = Tk()
Canvas(root, width = WIDTH, height = 5).pack(side=TOP)  # Some space at the top
g = eyeplot.graph(root, width=WIDTH, height=HEIGHT, bip=False)	# make plot objects using draw.disp
pt = PT100()

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)

b3 = Label(cf, text = _('Read Every'))
b3.pack(side = LEFT, anchor = SW)
TGAP = StringVar()
Dur =Entry(cf, width=5, bg = 'white', textvariable = TGAP)
TGAP.set('500')
Dur.pack(side = LEFT, anchor = SW)
b3 = Label(cf, text = _('mS,'))
b3.pack(side = LEFT, anchor = SW)
b3 = Label(cf, text = _('for total'))
b3.pack(side = LEFT, anchor = SW)
DURATION = StringVar()
Total =Entry(cf, width=5, bg = 'white', textvariable = DURATION)
DURATION.set('100')
Total.pack(side = LEFT, anchor = SW)
b3 = Label(cf, text = _('Seconds.'))
b3.pack(side = LEFT, anchor = SW)

b3 = Label(cf, text = _('Temp From'))
b3.pack(side = LEFT, anchor = SW)
TMIN = StringVar()
TMIN.set('0')
Tmin =Entry(cf, width=5, bg = 'white', textvariable = TMIN)
Tmin.pack(side = LEFT, anchor = SW)
b3 = Label(cf, text = _('to,'))
b3.pack(side = LEFT, anchor = SW)
TMAX = StringVar()
TMAX.set('200')
Tmax =Entry(cf, width=5, bg = 'white', textvariable = TMAX)
Tmax.pack(side = LEFT, anchor = SW)
b3 = Label(cf, text = _('Deg C. '))
b3.pack(side = LEFT, anchor = SW)

b3 = Label(cf, text = _('Rg='))
b3.pack(side = LEFT, anchor = SW)
RG = StringVar()
RG.set('300')
Rg =Entry(cf, width=4, bg = 'white', textvariable = RG)
Rg.pack(side = LEFT, anchor = SW)
b3 = Label(cf, text = _('Ohm'))
b3.pack(side = LEFT, anchor = SW)


#help = Balloon(root, bg ='green')
#help.config( statusbar = msgwin)


cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)
b1 = Button(cf, text = _('START'), command = pt.start)
b1.pack(side = LEFT, anchor = N)
b1 = Button(cf, text = _('STOP'), command = pt.stop)
b1.pack(side = LEFT, anchor = N)
b4 = Button(cf, text = _('CLEAR'), command = pt.clear)
b4.pack(side = LEFT, anchor = N)
b1 = Button(cf, text = _('Xmgrace'), command = pt.xmgrace)
b1.pack(side = LEFT, anchor = N)
b3 = Button(cf, text = _('SAVE to'), command = pt.save)
b3.pack(side = LEFT, anchor = N)
filename = StringVar()
e1 =Entry(cf, width=15, bg = 'white', textvariable = filename)
filename.set('pt100.dat')
e1.pack(side = LEFT)
b5 = Button(cf, text = _('QUIT'), command = sys.exit)
b5.pack(side = RIGHT, anchor = N)

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)
b1 = Button(cf, text = _('Freezing Point'), command = pt.get_freezing)
b1.pack(side = LEFT, anchor = N)
b1 = Button(cf, text = _('Boiling Point'), command = pt.get_boiling)
b1.pack(side = LEFT, anchor = N)
b1 = Button(cf, text = _('Calibrate'), command = pt.calibrate)
b1.pack(side = LEFT, anchor = N)

mf = Frame(root, width = WIDTH, height = 10)
mf.pack(side=TOP)
msgwin = Label(mf,text=_('Message'), fg = 'blue')
msgwin.pack(side=LEFT, anchor = S, fill=BOTH, expand=1)


eyeplot.pop_image('pics/pt100.png', _('Temperatue bt PT100'))
root.title(_('Temperature measuements using PT100'))
root.mainloop()

