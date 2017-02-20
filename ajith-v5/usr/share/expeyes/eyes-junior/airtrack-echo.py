'''
expEYES airtrack program
Author  : Ajith Kumar B.P, bpajith@gmail.com
License : GNU GPL version 3
'''
import gettext
gettext.bindtextdomain("expeyes")
gettext.textdomain('expeyes')
_ = gettext.gettext

from Tkinter import *
import expeyes.eyesj as eyes, expeyes.eyeplot as eyeplot, expeyes.eyemath as eyemath, time, sys

TIMER = 10
WIDTH  = 650   		# width of drawing canvas
HEIGHT = 400   		# height    
MAXTIME = 10        # default is 10 seconds
MINX    = 0			
MINY    = 0
MAXY    = 60        # 60 cm at the max
history = []		# Data store
trial = 0			# trial number
data = [ [], [] ]	# Current & Voltage
index = 0
running = False
vs = 0.034000
stime = 0;
userStop = False

def dispmsg(s):
	msg.config(text=_(s))
	
def stop():
	global userStop
	userStop = True
		
def start():
	global stime, running, index, data, MINX, MAXTIME, MINY, MAXY, userStop
	try:
		MAXTIME = int(DURATION.get())
		MAXY = int(MAXDIST.get())
		g.setWorld(0, MINY, MAXTIME, MAXY,_('Time'),_('Dist'))
		#Dur.config(state=DISABLED)		
		dispmsg(_('Starting the Measurements'))
		stime = time.time()
		root.after(self.TIMER, self.update)
	except:
		dispmsg(_('Failed to Start'))
	running = True
	data = [ [], [] ]
	index = 0
	userStop = False
	root.after(TIMER,update)

def viewAll():
	g.delete_lines()
	for k in range(len(history)):
		g.line(history[k][0], history[k][1], k)

def update():					# Called periodically by the Tk toolkit
	global index, trial, running, data, history, userStop
	if running == False:
		return
	tt = p.srfechotime(9,0)
	dist = (tt-400) *vs/2
	elapsed = time.time() - stime
	data[0].append(elapsed)
	data[1].append(dist)

	if elapsed >= MAXTIME or userStop == True:
		running = False
		history.append(data)
		trial += 1
		return
	if index > 1:			# Draw the line
		g.delete_lines()
		g.line(data[0], data[1], trial)
	index += 1
	root.after(TIMER, update)
	msg.config(text=_('Starting to plot I-V'))

def xmgrace():		# Send the data to Xmgrace
	global history
	p.grace(history, _('Seconds'), _('cm'), _('Linear Motion'))

def save():
	global history, running
	if running == True:
		return
	s = e1.get()
	if s == '':
		return
	p.save(history, s)
	msg.config(text = _('Data saved to file ')+s)

def clear():
	global history, trial, running
	if running == True:
		return
	g.delete_lines()
	history = []
	trial = 0

p = eyes.open()
p.disable_actions()
p.set_state(10,1)
root = Tk()
Canvas(root, width = WIDTH, height = 5).pack(side=TOP)  # Some space at the top
g = eyeplot.graph(root, width=WIDTH, height=HEIGHT, bip=False)	# make plot objects using draw.disp
g.setWorld(MINX, MINY, MAXTIME, MAXY,_('Seconds'),_('cm'))

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)

b1 = Button(cf, text = _('START'), command = start)
b1.pack(side = LEFT, anchor = N)
b6 = Button(cf, text = _('STOP'), command = stop)
b6.pack(side = LEFT, anchor = N)
b6 = Button(cf, text = _('ViewAll'), command = viewAll)
b6.pack(side = LEFT, anchor = N)
b4 = Button(cf, text = _('CLEAR'), command = clear)
b4.pack(side = LEFT, anchor = N)
b5 = Button(cf, text = _('Grace'), command = xmgrace)
b5.pack(side = LEFT, anchor = N)

b5 = Button(cf, text = _('QUIT'), command = sys.exit)
b5.pack(side = RIGHT, anchor = N)

cf2 = Frame(root, width = WIDTH, height = 10)
cf2.pack(side=TOP,  fill = BOTH, expand = 1)

b3 = Label(cf2, text = _('Duration='))
b3.pack(side = LEFT, anchor = SW)
DURATION = StringVar()
Dur =Entry(cf2, width=5, bg = 'white', textvariable = DURATION)
DURATION.set('10')
Dur.pack(side = LEFT, anchor = SW)
b3 = Label(cf2, text = _('Sec'))
b3.pack(side = LEFT, anchor = SW)

b3 = Label(cf2, text = _('Max Dist='))
b3.pack(side = LEFT, anchor = SW)
MAXDIST = StringVar()
Dis =Entry(cf2, width=5, bg = 'white', textvariable = MAXDIST)
MAXDIST.set('60')
Dis.pack(side = LEFT, anchor = SW)
b3 = Label(cf2, text = _('cm'))
b3.pack(side = LEFT, anchor = SW)

b3 = Button(cf2, text = _('SAVE to'), command = save)
b3.pack(side = LEFT, anchor = N)
filename = StringVar()
e1 =Entry(cf2, width=15, bg = 'white', textvariable = filename)
filename.set('airtrack.dat')
e1.pack(side = LEFT)


mf = Frame(root, width = WIDTH, height = 10)
mf.pack(side=TOP,  fill = BOTH, expand = 1)
msg = Label(mf,text=_('Message'), fg = 'blue')
msg.pack(side=LEFT)

root.title(_('EYES: Air Track'))
root.mainloop()

