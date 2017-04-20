import gettext
gettext.bindtextdomain("expeyes")
gettext.textdomain('expeyes')
_ = gettext.gettext

import expeyes.eyes17, expeyes.eyeplot17 as eyeplot,sys
VER = sys.version[0]
if VER == '3':
	from tkinter import *
else:
	from Tkinter import *


def update():
	v = p.get_voltage('A1')
	if v == v:   #is it NaN
		A1.config(text=_('%5.3f'%(v)))
	
	v = p.get_voltage('A2')
	if v == v:   #is it NaN
		A2.config(text=_('%5.3f'%(v)))
	
	v = p.get_voltage('A3')
	if v == v:   #is it NaN
		A3.config(text=_('%5.3f'%(v)))
		
	cap = p.get_capacitance()
	print cap
	if cap <= 1000e-12:
		print cap * 1e12, 'pF'
	elif cap <= 1000e-9:
		print cap * 1e9, 'nF'
	elif cap <= 1000e-6:
		print cap * 1e6, 'uF'
		
	w.after(500,update)
	
p=expeyes.eyes17.open()
p.set_pv1(-3.)
w = Tk()
f = Frame(w)
f.pack(side=TOP)
f.columnconfigure(2, minsize=100)
Label(f,text=_('A1 = '), font=("Helvetica", 26)).grid(row=1, column=1,sticky=E+W)
Label(f,text=_('A2 = '), font=("Helvetica", 26)).grid(row=2, column=1,sticky=E+W)
Label(f,text=_('A3 = '), font=("Helvetica", 26)).grid(row=3, column=1,sticky=E+W)

A1 = Label(f,text=_('      '), font=("Helvetica", 26))
A1.grid(row=1, column=2,sticky=E+W)
A2 = Label(f,text='', font=("Helvetica", 26))
A2.grid(row=2, column=2,sticky=E+W)
A3 = Label(f,text='', font=("Helvetica", 26))
A3.grid(row=3, column=2,sticky=E+W)

Label(f,text=_(' volts'), font=("Helvetica", 26)).grid(row=1, column=3,sticky=E+W)
Label(f,text=_(' volts'), font=("Helvetica", 26)).grid(row=2, column=3,sticky=E+W)
Label(f,text=_(' volts'), font=("Helvetica", 26)).grid(row=3, column=3,sticky=E+W)

Button(text=_('QUIT'), command=sys.exit).pack(side=TOP)
w.title(_('EYES-17: Measuring voltage'))
w.after(500,update)
w.mainloop()

