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
	nt = [ [], [] ]		# Lists for Trial number  & T
	TIMER = 5
	MINY = 0			# could be 0
	MAXY = 1500
	running = False
	index = 0
	nmax = 10

	def xmgrace(self):
		if self.running == True:
			return
		p.grace([self.nt])

	def hist(self):					# Need to be written
		if self.running == True:
			return
		nbin = self.nmax/5          # average binsize is 5
		self.hist = [0]*nbin
		data = []
		for t in self.nt[1]:
			data.append(4.0 * math.pi**2 * 2.0 * self.length / (3.0 *  t * t))
		if len(data) < 3:
			return
		tmin = p.minimum(data)
		tmax = p.maximum(data)	
		tmean = (tmin+tmax)/2
		span = tmax - tmin
		step = span / nbin
		#print tmin, tmax, span, step
		for k in range(self.nmax):
			for j in range(nbin):
				#print tmin+j*step, self.nt[1][k], tmin+(j+1)*step
				if tmin+j*step < data[k] <= tmin+(j+1)*step:
					self.h[j] += 1
		#print self.h


	def start(self):
		self.running = True
		self.index = 0
		self.nt = [ [], [] ]
		p.set_sqr1(0)					# Switch on the LED
		self.nmax = int(NMAX.get())
		self.msg(_('Starting the Measurements'))
		Result.delete(1.0, END)
		root.after(self.TIMER, self.update)

	def stop(self):
		p.set_sqr1(-1)
		self.running = False
		self.msg(_('User Stopped the measurements'))

	def update(self):
		if self.running == False:
			return
		t = p.multi_r2rtime(0,3)
		if t > 0:
			s = _('%5.1f mS\n') %(t*1.0e-3)
			#print s
			Result.insert(END, s)	
			self.nt[0].append(self.index)
			self.nt[1].append(t*1.0e-3)
			self.index += 1
			if self.index > self.nmax:
				self.running = False
				p.set_sqr2(-1)
				self.msg(_('Completed the Measurements'))
				return 
		else:
			self.running = False
			p.set_sqr2(-1)
			self.msg(_('Timeout Error. Check Connections'),'red')
			return 
		root.after(self.TIMER, self.update)

	def save(self):
		try:
			fn = filename.get()
		except:
			fn = 'rodpend.dat'
		p.save([self.nt],fn)
		self.msg(_('Data saved to %s')%fn)

	def clear(self):
		if self.running == True:
			return
		self.nt = [ [], [] ]
		Result.delete(1.0,END)
		self.msg(_('Cleared Data and Trace'))

	def msg(self,s, col = 'blue'):
		msgwin.config(text=s, fg=col)

p = eyes.open()
p.disable_actions()
root = Tk()
pen = Pend()
top = Frame()
top.pack(side=TOP)
cf = Frame(top, width = WIDTH, height = 10)
cf.pack(side=LEFT,  fill = BOTH, expand = 1)

b3 = Label(cf, text = _('Trials'))
b3.pack(side = TOP, anchor = W)
NMAX = StringVar()
e1 =Entry(cf, width=5, bg = 'white', textvariable = NMAX)
e1.pack(side = TOP, anchor = W)
NMAX.set('10')
b1 = Button(cf, text = _('START'), command = pen.start)
b1.pack(side = TOP, anchor = W)
b1 = Button(cf, text = _('STOP'), command = pen.stop)
b1.pack(side = TOP, anchor = W)
b4 = Button(cf, text = _('CLEAR'), command = pen.clear)
b4.pack(side = TOP, anchor = W)
b3 = Button(cf, text = _('SAVE to'), command = pen.save)
b3.pack(side = TOP, anchor = W)
filename = StringVar()
e1 =Entry(cf, width=10, bg = 'white', textvariable = filename)
filename.set('rodpend.dat')
e1.pack(side = TOP)
b1 = Button(cf, text = _('Xmgrace'), command = pen.xmgrace)
b1.pack(side = TOP, anchor = W)
b5 = Button(cf, text = _('QUIT'), command = sys.exit)
b5.pack(side = TOP, anchor = W)

Result = Text(top, width=15, height=16)	# make plot objects using draw.disp
Result.pack(side=LEFT)

mf = Frame(root, width = WIDTH, height = 10)
mf.pack(side=TOP)
msgwin = Label(mf,text=_('Message'), fg = 'blue')
msgwin.pack(side=LEFT, anchor = S, fill=BOTH, expand=1)

eyeplot.pop_image('pics/light-barrier.png', _('Period of a Pendulum'))
root.title(_('EYES Junior: Pendulum'))
root.mainloop()

