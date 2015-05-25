'''
expEYES program
Author  : Ajith Kumar B.P, bpajith@gmail.com
License : GNU GPL version 3
'''
import gettext
gettext.bindtextdomain("expeyes")
gettext.textdomain('expeyes')
_ = gettext.gettext

import time, math, sys
if sys.version_info.major==3:
        from tkinter import *
else:
        from Tkinter import *

sys.path=[".."] + sys.path

import expeyes.eyesj as eyes
import expeyes.eyeplot as eyeplot
import expeyes.eyemath as eyemath

WIDTH  = 600   # width of drawing canvas
HEIGHT = 400   # height    

class Pend:
	tv = [ [], [] ]			# Lists for Readings
	TIMER = 5			# Time interval between reads
	IDLE_TIMER = 100                # time interval between idle reads
	idle_threshold = 3              # 3V are necessary to autostart
	MINY = -5			# Voltage range
	MAXY = 5
	running = False
	MAXTIME = 10

	def __init__(self):
		"""
		The constructor
		"""
		self.reset_idle()
		root.after(self.IDLE_TIMER, self.idle)

	def fit_curve(self):
		fa = eyemath.fit_dsine(self.tv[0], self.tv[1], mode="Hz")
		if fa != None:
			pa = fa[1]
			g.line(self.tv[0], fa[0],1)
			self.msg(_('Angular velocity = %5.2f rad/sec. Damping Factor = %5.3f')%(pa[1], pa[4]))
		else:
			self.msg(_('Failed to fit data'))

	def xmgrace(self):
		if self.running == True:
			return
		p.grace([self.tv])

	def reset_idle(self):
		"""
		resets an internal list of 20 samples
		"""
		self.idle_values=[0.0]*20
		return

	def idle(self):
		"""
		callback used when no other method is in action.
		stores internally 20 previous samples of voltage measured
		recently, every tenth of second.
		When this list contains values with an amplitude greater
		than a given threshold, creates an "autolaunch".
		"""
		if self.running:
			return
		t,v = p.get_voltage_time(1)
		del self.idle_values[0]
		self.idle_values.append(v)
		amplitude=max(self.idle_values) - min(self.idle_values)
		if amplitude > self.idle_threshold:
			self.start()
		root.after(self.IDLE_TIMER, self.idle)
		return
		
	def start(self):
		self.running = True
		self.reset_idle()
		self.index = 0
		self.tv = [ [], [] ]
		try:
			self.MAXTIME = int(DURATION.get())
			g.setWorld(0, self.MINY, self.MAXTIME, self.MAXY,_('Time'),_('Volt'))
			Dur.config(state=DISABLED)
			self.msg(_('Starting the Measurements'))
			root.after(self.TIMER, self.update)
		except:
			self.msg(_('Failed to Start'))

	def stop(self):
		self.running = False
		Dur.config(state=NORMAL)
		self.msg(_('User Stopped the measurements'))
		root.after(self.IDLE_TIMER, self.idle)

	def update(self):
		if self.running == False:
			return
		t,v = p.get_voltage_time(1)  # Read A2
		if len(self.tv[0]) == 0:
			self.start_time = t
			elapsed = 0
		else:
			elapsed = t - self.start_time
		self.tv[0].append(elapsed)
		self.tv[1].append(v)
		if len(self.tv[0]) >= 2:
			g.delete_lines()
			g.line(self.tv[0], self.tv[1])
		if elapsed > self.MAXTIME:
			self.running = False
			Dur.config(state=NORMAL)
			self.msg(_('Completed the Measurements'))
			root.after(self.IDLE_TIMER, self.idle)
			return 
		root.after(self.TIMER, self.update)

	def save(self):
		try:
			fn = filename.get()
		except:
			fn = 'pendulum.dat'
		p.save([self.tv],fn)
		self.msg(_('Data saved to %s')%fn)

	def clear(self):
		if self.running == True:
			return
		self.tv = [ [], [] ]
		g.delete_lines()
		self.msg(_('Cleared Data and Trace'))

	def msg(self,s, col = 'blue'):
		msgwin.config(text=s, fg=col)

p = eyes.open()
p.disable_actions()
root = Tk()
Canvas(root, width = WIDTH, height = 5).pack(side=TOP)  # Some space at the top
g = eyeplot.graph(root, width=WIDTH, height=HEIGHT, bip=False)	# make plot objects using draw.disp
pen = Pend()

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)


b3 = Label(cf, text = _('Digitize for'))
b3.pack(side = LEFT, anchor = SW)
DURATION = StringVar()
Dur =Entry(cf, width=5, bg = 'white', textvariable = DURATION)
DURATION.set('15')
Dur.pack(side = LEFT, anchor = SW)
b3 = Label(cf, text = _('Seconds.'))
b3.pack(side = LEFT, anchor = SW)

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)
b1 = Button(cf, text = _('START'), command = pen.start)
b1.pack(side = LEFT, anchor = N)
b1 = Button(cf, text = _('STOP'), command = pen.stop)
b1.pack(side = LEFT, anchor = N)
b1 = Button(cf, text = _('FIT'), command = pen.fit_curve)
b1.pack(side = LEFT, anchor = N)
b4 = Button(cf, text = _('CLEAR'), command = pen.clear)
b4.pack(side = LEFT, anchor = N)
b1 = Button(cf, text = _('Xmgrace'), command = pen.xmgrace)
b1.pack(side = LEFT, anchor = N)
b3 = Button(cf, text = _('SAVE to'), command = pen.save)
b3.pack(side = LEFT, anchor = N)
filename = StringVar()
e1 =Entry(cf, width=15, bg = 'white', textvariable = filename)
filename.set('pendulum.dat')
e1.pack(side = LEFT)
b5 = Button(cf, text = _('QUIT'), command = sys.exit)
b5.pack(side = RIGHT, anchor = N)

mf = Frame(root, width = WIDTH, height = 10)
mf.pack(side=TOP)
msgwin = Label(mf,text=_('Message'), fg = 'blue')
msgwin.pack(side=LEFT, anchor = S, fill=BOTH, expand=1)


eyeplot.pop_image('pics/pend-wave.png', _('Pendulum Oscillations'))
root.title(_('Oscillations of Pendulum'))
root.mainloop()

