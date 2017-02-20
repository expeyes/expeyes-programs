from Tkinter import *
import expeyes.eyes17, expeyes.eyeplot17 as eyeplot
p=expeyes.eyes17.open()

import gettext
gettext.bindtextdomain("expeyes")
gettext.textdomain('expeyes')
_ = gettext.gettext

def set_pvs(w):
	iv = int(Pvs.get())
	v = (iv - 5000) * 0.001
	p.set_pv1(v)
	Res.config(text=_('PV1 = %5.3f volts')%v)
	
w = Tk()
Label(text=_('To change PV1 drag the slider. For fine adjustment, click on its left or right')).pack(side=TOP)
Pvs = Scale(w,command = set_pvs, orient=HORIZONTAL, length=500, showvalue=False, from_ = 0, to=10000, resolution=1)
Pvs.pack(side=TOP)
Res = Label(text = _(''), fg = _('blue'))
Res.pack(side=TOP)
Button(text=_('QUIT'), command=sys.exit).pack(side=TOP)
w.title(_('EYES Junior: Adjust PVS'))
w.mainloop()

