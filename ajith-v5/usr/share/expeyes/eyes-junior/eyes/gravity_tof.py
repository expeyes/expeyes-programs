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
import expeyes.eyes as eyes, expeyes.eyeplot as eyeplot


def attach():
	p.write_outputs(1)

def get_tof1():
	global t1, h1
	h1 = float(H1.get())
	if (p.read_inputs() & 4) == 0:    # currently LOW
		t1 = p.clr2rtime(0,2)*1.0e-6
	else:
		t1 = p.clr2ftime(0,2)*1.0e-6
	if t1 > 0:
		msgwin.config(text = _('%8.6f sec')%t1)
	else:
		msgwin.config(text = _('Timeout Error..'))

def get_tof2():
	global t2, h2
	h2 = float(H2.get())
	t2 = p.clr2rtime(0,2)*1.0e-6
	if t2 > 0:
		res2.config(text = _('%8.6f sec')%t2)
	else:
		res2.config(text = _('Error..'))

def calc_g():
	global t1, t2, h1, h2
	try:
		print t1,t2,h1,h2
		g = 2 * (h2-h1) / (t2**2 - t1**2)
		msgwin.config(text='g = %5.1f'%g)
	except:
		msgwin.config(text = _(' Error'))

p = eyes.open()
p.disable_actions()

root = Tk()

cf = Frame(root)
cf.pack(side=TOP,  fill = BOTH, expand = 1)
b3 = Label(cf, text = _('Height='))
b3.pack(side = LEFT, anchor = SW)
H1 = StringVar()
h =Entry(cf, width=5, bg = 'white', textvariable = H1)
h.pack(side=LEFT)
H1.set('30')
b3 = Label(cf, text = _('cm'))
b3.pack(side = LEFT, anchor = SW)
b1 = Button(cf, text = _('Attach Ball'), command = attach)
b1.pack(side = LEFT, anchor = N)
b1 = Button(cf, text = _('Measure TOF'), command = get_tof1)
b1.pack(side = LEFT, anchor = N)
res1 = Label(cf, text = '')
res1.pack(side = LEFT, anchor = N)
'''
cf = Frame(root)
cf.pack(side=TOP,  fill = BOTH, expand = 1)
b3 = Label(cf, text = 'Height=')
b3.pack(side = LEFT, anchor = SW)
H2 = StringVar()
h =Entry(cf, width=5, bg = 'white', textvariable = H2)
h.pack(side=LEFT)
H2.set('20')
b3 = Label(cf, text = 'cm')
b3.pack(side = LEFT, anchor = SW)
b1 = Button(cf, text = 'Attach Ball', command = attach)
b1.pack(side = LEFT, anchor = N)
b1 = Button(cf, text = 'Measure TOF', command = get_tof2)
b1.pack(side = LEFT, anchor = N)
res2 = Label(cf, text = '')
res2.pack(side = LEFT, anchor = N)

cf = Frame(root)
cf.pack(side=TOP,  fill = BOTH, expand = 1)
b1 = Button(cf, text = 'Calculate "g"', command = calc_g)
b1.pack(side = LEFT, anchor = N)
'''

mf = Frame(root)
mf.pack(side=TOP,  fill = BOTH, expand = 1)
msgwin = Label(mf,text=_('Message'), fg = 'blue')
msgwin.pack(side=LEFT, anchor = S, fill=BOTH, expand=1)
b5 = Button(cf, text = _('QUIT'), command = sys.exit)
b5.pack(side = RIGHT, anchor = N)

eyeplot.pop_image('pics/g-tof.png', _('Gravity by TOF'))
root.title(_('Gravity by Time of Flight'))
root.mainloop()
