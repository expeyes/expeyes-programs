'''
expEYES program
Author  : Ajith Kumar B.P, bpajith@gmail.com
License : GNU GPL version 3
'''

import gettext
gettext.bindtextdomain("expeyes")
gettext.textdomain('expeyes')
_ = gettext.gettext

from tkinter import *
import expeyes.eyes as eyes, expeyes.eyeplot as eyeplot, expeyes.eyemath as eyemath, time

WIDTH  = 600   # width of drawing canvas
HEIGHT = 400   # height 

class amfm:
	delay = 20			# Time interval between samples
	NP = 1000			# Number of samples
	NC = 1				# Number of channels

	def do_fft(self):
		if self.trace == None: return
		transform = []
		for xy in self.trace:
			fr,tr = eyemath.fft(xy[1], self.delay * self.NC * 0.001)
			transform.append([fr,tr])
		p.grace(transform, _('freq'), _('power'))
		#eyeplot.plot(fr,tr)
		#p.save(transform, 'power-spec.dat')
		#msgwin.config(text=_('Fourier Power Spectrum Saved to power-spec.dat.'))

	def capture(self):
		self.chanmask = A0.get() | (A1.get() << 1)
		if self.chanmask == 3:
			self.NC = 2
		else:
			self.NC = 1
		self.trace = []
		v = float(UPV.get())
		p.set_upv(v)
		s = '%5.3f'%v
		UPV.set(s)
		self.NP = int(Npoints.get())
		self.delay = int(Delay.get())
		g.setWorld(0,-5, self.NC*self.NP * self.delay * 0.001, 5, _('mS'),_('V'))
		s = ''
		if self.chanmask == 1 or self.chanmask == 2:
			t,v = p.capture(self.chanmask-1, self.NP, self.delay)
			g.delete_lines()
			g.line(t,v,self.chanmask-1)
			self.trace.append([t,v])
		elif self.chanmask == 3:
			t,v,tt,vv = p.capture01(self.NP, self.delay)
			g.delete_lines()
			g.line(t,v)
			g.line(tt,vv,1)
			self.trace.append([t,v])
			self.trace.append([tt,vv])

p = eyes.open()
p.loadall_calib()
a = amfm()
root = Tk()
Canvas(root, width = WIDTH, height = 5).pack(side=TOP)  # Some space at the top
g = eyeplot.graph(root, width=WIDTH, height=HEIGHT)		# make plot objects using draw.disp
g.setWorld(0, -5, 20, 5,_('mS'),_('V'))
g.setWorld(0,-5, a.NP * a.delay * 0.001, 5, _('mS'),_('V'))

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)

A0 = IntVar()
b=Checkbutton(cf,text='A0', variable=A0, fg= 'black')
b.pack(side=LEFT, anchor = SW)
A0.set(1)
A1 = IntVar()
b=Checkbutton(cf,text='A1', variable=A1, fg= 'black')
b.pack(side=LEFT, anchor = SW)


b=Button(cf,text=_('Capture'), command = a.capture, fg= 'black')
b.pack(side=LEFT, anchor = SW)

b=Button(cf,text=_('Power Spectrum'), command = a.do_fft, fg= 'black')
b.pack(side=LEFT, anchor = SW)

b5 = Button(cf, text = _('QUIT'), command = sys.exit)
b5.pack(side = RIGHT, anchor = N)

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)
l = Label(cf, text = _('Number of Samples ='))
l.pack(side=LEFT)
Npoints = StringVar()
t=Entry(cf, width=5, bg = 'white', textvariable = Npoints)
t.pack(side=LEFT, anchor = S)
Npoints.set('1000')

l = Label(cf, text = _('Delay between samples='))
l.pack(side=LEFT)
Delay = StringVar()
t=Entry(cf, width=3, bg = 'white', textvariable = Delay)
t.pack(side=LEFT, anchor = S)
Delay.set('20')
l = Label(cf, text = _('uS.'))
l.pack(side=LEFT)

l = Label(cf, text = _('UPV ='))
l.pack(side=LEFT)
UPV = StringVar()
t=Entry(cf, width=5, bg = 'white', textvariable = UPV)
t.pack(side=LEFT, anchor = S)
UPV.set('3')
l = Label(cf, text = _('V'))
l.pack(side=LEFT)

mf = Frame(root)				# Message Frame below command frame.
mf.pack(side=TOP, anchor = SW)
msgwin = Label(mf,text = _('Messages'), fg = 'blue')
msgwin.pack(side=LEFT, anchor = SW)

root.title(_('Amplitude Modulation'))
root.mainloop()

