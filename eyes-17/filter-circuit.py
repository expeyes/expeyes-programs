'''
expEYES program
Author  : Ajith Kumar B.P, bpajith@gmail.com
License : GNU GPL version 3
'''

import gettext
gettext.bindtextdomain("expeyes")
gettext.textdomain('expeyes')
_ = gettext.gettext

import expeyes.eyes17 as eyes, expeyes.eyeplot17 as eyeplot, expeyes.eyemath17 as eyemath, time, sys
VER = sys.version[0]
if VER == '3':
	from tkinter import *
else:
	from Tkinter import *

TIMER = 10
WIDTH  = 600   # width of drawing canvas
HEIGHT = 400   # height    

FMIN 	= 100		# starting freqency
FMAX 	= 4000
FREQ    = FMIN		# this will change in the loop
STEP    = 10		# in Hertz
MINY    = 0			 
MAXY    = 1.1		# Amplitude ratio is plotted
trial = 0			# trial number
data = [ [], [], [] ]	# amp1, phase1, amp2, phase2
index = 0
running = False

def stop():
	global running
	running = False
	msg.config(text=_('Plotting Interrupted'))

def start():
	global FREQ, running, index, data
	if running == True: return
	p.select_range('A1',4)
	FMIN = float(fmin.get())
	if FMIN < 10: FMIN =10
	FMAX = float(fmax.get())
	if FMAX > 5000: FMAX = 5000
	g.setWorld(FMIN, MINY, FMAX, MAXY,'Freq',_('Gain'))
	running = True
	data = [ [], [], [] ]
	FREQ = FMIN
	index = 0
	msg.config(text=_('Starting to plot Freq vs Gain'))
	root.after(TIMER,update)

def verify_fit(y,y1):
	sum = 0.0
	for k in range(len(y)):
		sum += abs((y[k] - y1[k])/y[k])
	err = sum/len(y)
	if err > .5:
		return False
	else:
		return True
	
def update():				# Called periodically by the Tk toolkit
	global FREQ, FMAX, STEP, index, trial, running, data, history
	if running == False:
		return
	fr = p.set_wave(FREQ)	
	time.sleep(0.02)
	TG = 1.e6/FREQ/50   # 50 points per wave
	TG = int(TG)//2 * 2
	NP = 400
	MAXTIME = 200000.  # .2 seconds
	if NP * TG > MAXTIME:
		NP = int(MAXTIME/TG)
	if NP % 2: NP += 1  # make it an even number
	
	goodFit = False
	for k in range(3):                  # try 3 times
		t,v, tt,vv = p.capture2(NP, int(TG))	
		fa = eyemath.fit_sine(t,v)
		if fa != None:
			if verify_fit(v,fa[0]) == False:        # compare the trace and the fitted curve
				continue
			fb = eyemath.fit_sine(tt,vv)
			if fb != None:
				if verify_fit(vv,fb[0]) == False:        # compare the trace and the fitted curve
					continue
				data[0].append(fr)
				data[1].append(abs(fb[1][0]/fa[1][0]))
				#data[2].append(.5+(fa[1][2]-fb[1][2])/6.28)
				goodFit = True
				break
				
	FREQ += STEP
	if goodFit == False:		# Failed at this data point
		root.after(TIMER, update)
		return

	if index > 1:							# Draw the line
		g.delete_lines()
		g.line(data[0], data[1], 0)		
		#g.line(data[0], data[2], 1)		
	index += 1

	if FREQ > FMAX:
		running = False
		return
	root.after(TIMER, update)

def xmgrace():		# Send the data to Xmgrace
	global data
	eyeplot.grace([data], _('Freq'), _('Gain'), _('Frequency Response of Filter.'))

def save():
	global history, running
	if running == True:
		return
	s = e1.get()
	if s == '':
		return
	p.save([data], s)
	msg.config(text = _('Data saved to file ')+s)


def clear():
	global history, trial, running
	if running == True:
		return
	g.delete_lines()
	history = []
	trial = 0

p = eyes.open()
root = Tk()
Canvas(root, width = WIDTH, height = 5).pack(side=TOP)  # Some space at the top
g = eyeplot.graph(root, width=WIDTH, height=HEIGHT, bip=False)	# make plot objects using draw.disp
g.setWorld(FMIN, MINY, FMAX, MAXY,_('Freq'),_('Gain'))

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)

Label(cf, text = _('Scan from')).pack(side = LEFT, anchor = S)
fmin = Entry(cf,width = 6, bg = 'white')
fmin.pack(side=LEFT, anchor = SW)
fmin.insert(END,'100')
Label(cf, text = _('Hz to')).pack(side = LEFT, anchor = S)
fmax = Entry(cf,width = 6, bg = 'white')
fmax.pack(side=LEFT, anchor = SW)
fmax.insert(END,'4000')
Label(cf, text = _('Hz')).pack(side = LEFT, anchor = S)


b1 = Button(cf, text = _('START'), command = start)
b1.pack(side = LEFT, anchor = N)
b1 = Button(cf, text = _('STOP'), command = stop)
b1.pack(side = LEFT, anchor = N)
b3 = Button(cf, text = _('SAVE to'), command = save)
b3.pack(side = LEFT, anchor = N)
filename = StringVar()
e1 =Entry(cf, width=15, bg = 'white', textvariable = filename)
filename.set('LCfilter.dat')
e1.pack(side = LEFT)

b5 = Button(cf, text = _('QUIT'), command = sys.exit)
b5.pack(side = RIGHT, anchor = N)
b4 = Button(cf, text = _('CLEAR'), command = clear)
b4.pack(side = RIGHT, anchor = N)
b5 = Button(cf, text = _('Grace'), command = xmgrace)
b5.pack(side = RIGHT, anchor = N)

mf = Frame(root, width = WIDTH, height = 10)
mf.pack(side=TOP,  fill = BOTH, expand = 1)
msg = Label(mf,text=_('Message'), fg = 'blue')
msg.pack(side=LEFT)

t=_('Filter frequency response')
eyeplot.pop_help('filter-circuit', t)
root.title(t)
root.mainloop()

