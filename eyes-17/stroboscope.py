import expeyes.eyes17, expeyes.eyeplot17 as eyeplot,sys
VER = sys.version[0]
if VER == '3':
	from tkinter import *
else:
	from Tkinter import *

p=expeyes.eyes17.open()

import gettext
gettext.bindtextdomain("expeyes")
gettext.textdomain('expeyes')
_ = gettext.gettext

def set_freq(w):
	state = int(Sqr1.get())
	fr = float(Sqr1.get())
	res = p.set_sqr1(fr)

w = Tk()
Label(text=_('Use Slider to change SQ1 from 1 to 100 Hz')).pack(side=TOP)
Sqr1 = Scale(w,command = set_freq, orient=HORIZONTAL, length=220, showvalue=True, from_ = 1, to=50, resolution=.1)
Sqr1.pack(side=TOP)
Button(text=_('QUIT'), command=sys.exit).pack(side=TOP)
t=_('Stroboscope')
eyeplot.pop_help('stroboscope', t)
w.title(t)
w.mainloop()

