'''
expEYES program
Author  : Ajith Kumar B.P, bpajith@gmail.com
License : GNU GPL version 3
'''
import gettext
gettext.bindtextdomain("expeyes")
gettext.textdomain('expeyes')
_ = gettext.gettext

from Tkinter import *
import expeyes.eyes as eyes, expeyes.eyeplot as eyeplot, expeyes.eyemath as eyemath, time, sys, math

WIDTH  = 600   # width of drawing canvas
HEIGHT = 400   # height    

class Pend:
	nt = [ [], [] ]		# Lists for Trial number  & T
	ng = [ [], [] ]		# Lists for Trial number  & g
	TIMER = 5
	MINY = 0			# could be 0
	MAXY = 1500
	running = False
	index = 0
	nmax = 10
	length = 10.0

	def xmgrace(self):
		if self.running == True:
			return
		p.grace([self.nt, self.ng])

	def hist(self):					# Need to be written
		if self.running == True:
			return
		try:
			nbin = int(NBIN.get())
			if nbin > self.nmax / 2:
				return
		except:
			return
		self.h = [0]*nbin
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
		print tmin, tmax, span, step
		for k in range(self.nmax):
			for j in range(nbin):
				#print tmin+j*step, self.nt[1][k], tmin+(j+1)*step
				if tmin+j*step < data[k] <= tmin+(j+1)*step:
					self.h[j] += 1
		print self.h


	def start(self):
		self.running = True
		self.index = 0
		self.nt = [ [], [] ]
		self.ng = [ [], [] ]
		p.set_sqr2(0)			# Switch on the LED
		p.adc2cmp(5)			# Route Sensor to CMP input
		self.nmax = int(NMAX.get())
		g.setWorld(0, 0, self.nmax, self.MAXY,_('Trials'),_('T & g'))
		self.msg(_('Starting the Measurements'))
		self.length = float(LEN.get())
		root.after(self.TIMER, self.update)

	def stop(self):
		p.set_sqr2(-1)
		self.running = False
		self.msg(_('User Stopped the measurements'))

	def update(self):
		if self.running == False:
			return
		t = p.multi_r2rtime(4,1)
		if t > 0:
			self.nt[0].append(self.index)
			self.nt[1].append(t*1.0e-3)
			self.ng[0].append(self.index)
			accn = 4.0 * math.pi**2 * 2.0 * self.length / (3.0 *  (t*1.0e-6)**2)
			print accn
			self.ng[1].append(accn)
			self.index += 1
			if self.index >= 2:
				g.delete_lines()
				g.line(self.nt[0], self.nt[1])
				g.line(self.nt[0], self.ng[1],1)
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
		p.save([self.nt,self.ng],fn)
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
p.disable_actions()
root = Tk()
Canvas(root, width = WIDTH, height = 5).pack(side=TOP)  # Some space at the top
g = eyeplot.graph(root, width=WIDTH, height=HEIGHT)	# make plot objects using draw.disp
pen = Pend()

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)

l1 = Label(cf, text = _('Length='))
l1.pack(side = LEFT, anchor = SW)
LEN = StringVar()
e1 =Entry(cf, width=5, bg = 'white', textvariable = LEN)
LEN.set('10')
e1.pack(side = LEFT, anchor = SW)
l2 = Label(cf, text = _('cm. '))
l2.pack(side = LEFT, anchor = SW)

b3 = Label(cf, text = _('Measure'))
b3.pack(side = LEFT, anchor = SW)
NMAX = StringVar()
e1 =Entry(cf, width=5, bg = 'white', textvariable = NMAX)
NMAX.set('10')
e1.pack(side = LEFT, anchor = SW)
b3 = Label(cf, text = _('times.'))
b3.pack(side = LEFT, anchor = SW)

b1 = Button(cf, text = _('START'), command = pen.start)
b1.pack(side = LEFT, anchor = N)
b1 = Button(cf, text = _('STOP'), command = pen.stop)
b1.pack(side = LEFT, anchor = N)
b4 = Button(cf, text = _('CLEAR'), command = pen.clear)
b4.pack(side = LEFT, anchor = N)
b3 = Button(cf, text = _('SAVE to'), command = pen.save)
b3.pack(side = LEFT, anchor = N)
filename = StringVar()
e1 =Entry(cf, width=15, bg = 'white', textvariable = filename)
filename.set('rodpend.dat')
e1.pack(side = LEFT)

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)
b1 = Button(cf, text = _('Xmgrace'), command = pen.xmgrace)
b1.pack(side = LEFT, anchor = N)

'''
b1 = Button(cf, text = _('Histogram'), command = pen.hist)
b1.pack(side = LEFT, anchor = N)
NBIN = StringVar()
e1 =Entry(cf, width=3, bg = 'white', textvariable = NBIN)
NBIN.set('2')
e1.pack(side = LEFT)
b3 = Label(cf, text = _('bins.'))
b3.pack(side = LEFT, anchor = SW)
'''

b5 = Button(cf, text = _('QUIT'), command = sys.exit)
b5.pack(side = RIGHT, anchor = N)

mf = Frame(root, width = WIDTH, height = 10)
mf.pack(side=TOP)
msgwin = Label(mf,text=_('Message'), fg = 'blue')
msgwin.pack(side=LEFT, anchor = S, fill=BOTH, expand=1)

eyeplot.pop_image('pics/rodpend.png', _('Period of Rod Pendulum'))
root.title(_('EYES: Value of Accn. due to gravity using Pendulum'))
root.mainloop()

