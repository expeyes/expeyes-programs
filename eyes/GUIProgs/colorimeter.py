from Tkinter import *
import phm, time, math, sys
p=phm.phm()

base = []
absvals = []
wavelen = [400., 430., 470., 505., 525., 570., 590., 610., 635., 660.]
NLED = 10
Calib = []
NUMCAL = 2


def measure(n):
	p.set_port(0,n<<4)
	time.sleep(0.1)
	res = p.get_voltage()[1]
	p.set_port(0, 10 << 4)   # Switch off all LEDs
	return res

def do_base():
	global base, wavelen, NLED
	base = []
	clear()
	for n in range(NLED):
		val = measure(n)
		base.append(val)
		ss = '%8.0f nm %8.3f V\n'%(wavelen[n],val*0.001)
		data.insert(END,ss)
	msg.config(text='Base Done', fg = 'black')


def do_sample():
	global base, wavelen, absvals, NLED
	if base == [] :
		msg.config(text='Do Base First', fg = 'red')
		return
	clear()
	absvals = []
	maxabs = 0.0
	index = 0			# Assume the first one
	data.insert(END,'Source # Wavelength         Base     Sample  Tran (%)  Absorbance\n')
	for n in range(NLED):
		val = measure(n)
		tr = val / base[n] * 100
		ab = 2.0 - math.log10(tr)
		absvals.append(ab)
		if ab > maxabs:
			maxabs = ab
			index = n
		ss = '%2d %8.0f nm  %8.3f V %8.3f V %8.1f %%  %8.3f\n'\
			%(n,wavelen[n], base[n]*0.001, val*0.001, tr, ab)
		data.insert(END,ss)
	msg.config(text='Sample Done. Maximum absorabnce at %5.0f nm'%wavelen[index], fg = 'black')
	Selected.set(str(index))

def clear():
	data.delete(1.0, END)  

def quit():
	sys.exit()

	
def doCalib(index):
	global base, selected, Calib
	print 'Index = ', index
	if base == [] :
		msg.config(text='Do Base First', fg = 'red')
		return
	s2 = Selected.get()
	try:
		selected = int(s2)
	except:
		msg.config(text='Enter the Wavelength Source(%d to %d)'%(0,NLED), fg = 'red')
		return
	val = measure(selected)
	tr = val / base[selected] * 100
	ab = 2.0 - math.log10(tr)
	Calib[index][2] = ab
	ss = '%8.3f'%(ab)
	Calib[index][1].config(text = ss)	

def uk_sample():
	s2 = Selected.get()
	try:
		selected = int(s2)
	except:
		msg.config(text='Enter the Wavelength Source(%d to %d)'%(0,NLED), fg = 'red')
		return
	xy = []
	for k in range(NUMCAL):
		s = Calib[k][0].get()
		print s
		try:
			nrm = float(s)
			xy.append( [Calib[k][2], nrm] )
		except:
			msg.config(text='Enter the Normality of sample %d'%(k+1), fg = 'red')
			return
	if abs(xy[1][0]-xy[0][0]) < 0.0001:
		msg.config(text='Standard solutions are identical', fg = 'red')
		return

	m = (xy[1][1] - xy[0][1]) / (xy[1][0] - xy[0][0])
	c = xy[0][1] - m * xy[0][0]
	print m, c
	val = measure(selected)
	tr = val / base[selected] * 100
	ab = 2.0 - math.log10(tr)
	unval = m * ab + c
	ss = 'Abs = %8.3f Normality = %5.2f'%(ab,unval)
	Result.config(text = ss)	


root = Tk()
f1 = Frame(root)
f1.pack()
data = Text(f1, width = 60, height = 12)
data.pack()

cf1 = Frame()
cf1.pack(side=TOP)
Selected = StringVar()    # Index of LED with maximum absorbance
Selected.set('nn')
s=Entry(cf1, width=3, bg = 'white', textvariable = Selected)
s.pack(side=LEFT)
print Selected.get()

Start = Button(cf1,text = 'Base Solution', command = do_base)
Start.pack(side=LEFT)
Start = Button(cf1,text = 'Sample Solution', command = do_sample)
Start.pack(side=LEFT)
Start = Button(cf1,text = 'Clear', command = clear)
Start.pack(side=LEFT)
Start = Button(cf1,text = 'Quit', command = quit)
Start.pack(side=RIGHT)

for k in range(NUMCAL):
	cf = Frame(root)
	cf.pack(side=TOP)
	cl = Label(cf,text = 'Standard Solution %d'%(k+1))
	cl.pack(side=LEFT)
	cb = Button(cf,text = 'Absorbance =', command = (lambda k = k: doCalib(k)))
	cb.pack(side=LEFT)
	reslabel = Label(cf, width = 10, text = 'Not Measured')
	reslabel.pack(side=LEFT)
	lab = Label(cf, width = 10, text = 'Normality=')
	lab.pack(side=LEFT)
	UDN = StringVar()    # User Defined Normality
	e=Entry(cf, width=7, bg = 'white',textvariable = UDN)
	e.pack(side=LEFT)
	calsam = []
	calsam.append(UDN)	# User Defined Normality
	calsam.append(reslabel)	# Absorbance label Widget
	calsam.append(0.0)	# Place for Absorbance value. Obtained during doCalib()
	Calib.append(calsam)

f2 = Frame(root)
f2.pack(side=TOP)
us = Button(f2,text = 'Measure Unknown Sample', command = uk_sample)
us.pack(side=LEFT)
Result = Label(f2,text = 'Result = NA')
Result.pack(side=LEFT)

msg = Label(root,text = '')
msg.pack(side=LEFT)


root.title('Phoenix Based Colorimeter')
root.mainloop()

