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
from expeyes.SENSORS import ADS1115

VER = sys.version[0]
if VER == '3':
	from tkinter import *
else:
	from Tkinter import *

NCHAN  = 4
WIDTH  = 600   # width of drawing canvas
HEIGHT = 400   # height    
chansrc = [0, 1, 2, 3]
offset = [0, 1, 2, 3]

class ADS1115_Logger:
	chan = [1,2,3,4,5]
	tv = [ [], [] ]						# Lists for Time & Voltage
	MAXTIME = 10  	    # Maximum time, user can set
	TIMER = 500
	MINY = 0			# could be 0
	MAXY = 100 #100degrees
	start_time = None
	running = False

	def __init__(self):
		self.chinfo = []
		for ch in range(NCHAN):
			self.chinfo.append([False, [[],[]], 0])  # Active, Data, Start Time

	def start(self):
		self.running = False					# Assume no channel is selected
		for ch in range(NCHAN):
			self.chinfo[ch][1] = [ [], [] ]		# Clear old data
			if CH[ch].get() == 1:
				self.chinfo[ch][0] = True
				self.running = True
			else:
				self.chinfo[ch][0] = False
		try:
			self.MAXTIME = int(DURATION.get())
			g.setWorld(0, self.MINY, self.MAXTIME, self.MAXY,_('Time'),_('Temperature(C)'))
			self.TIMER = int(TGAP.get())
			for k in range(4): CB[k].config(state = DISABLED)
			Total.config(state=DISABLED)
			Dur.config(state=DISABLED)
			self.msg(_('Starting the Measurement'))
			root.after(self.TIMER, self.update)
		except:
			self.msg(_('Failed to Start Measurement'))
			pass

	def stop(self):
		for k in range(NCHAN): CB[k].config(state = NORMAL)
		Total.config(state=NORMAL)
		Dur.config(state=NORMAL)
		self.running = False

	def fixOffset(self):
		tmp = [0]*NCHAN
		for ch in range(NCHAN):
				tmp[ch] = ADC.readADC_SingleEnded(chansrc[ch])*1e-1
		avg = sum(tmp)/float(NCHAN)
		valLabel['text']='average :%.2f'%avg
		for ch in range(NCHAN):
			offset[ch] = tmp[ch]-avg
		

	def update(self):
		if self.running == False:
			return
		g.delete_lines()
		msg=''
		for ch in range(NCHAN):
			if self.chinfo[ch][0] == True:
				t=time.time()
				v = ADC.readADC_SingleEnded(chansrc[ch])*1e-1 - offset[ch]
				msg+='%d: %.2f, '%(ch,v)
				#t,v = p.get_voltage_time(chansrc[ch])
				if len(self.chinfo[ch][1][0]) == 0:
					self.chinfo[ch][2] = t
					elapsed = 0
				else:
					elapsed = t - self.chinfo[ch][2]
				self.chinfo[ch][1][0].append(elapsed)
				self.chinfo[ch][1][1].append(v)
				if len(self.chinfo[ch][1][0]) >= 2:
					g.line(self.chinfo[ch][1][0], self.chinfo[ch][1][1],ch, smooth=True)
		#print [self.chinfo[a][1][1][-1] for a in range(NCHAN)]
		valLabel['text']=msg

		try:
			self.MAXTIME = int(DURATION.get())
			self.TIMER = int(TGAP.get())
		except:
			pass
		if elapsed > self.MAXTIME:
			for k in range(NCHAN): CB[k].config(state = NORMAL)
			Total.config(state=NORMAL)
			Dur.config(state=NORMAL)
			self.running = False
			return 
		root.after(self.TIMER, self.update)

	def save(self):
		try:
			fn = filename.get()
		except:
			fn = 'logger.dat'
		f = open(fn, 'w')
		for ch in range(NCHAN):
			if self.chinfo[ch][0] == True:
				size = len(self.chinfo[ch][1][0])
				for k in range(size):
					s = '%5.3f  %5.3f\n'%(self.chinfo[ch][1][0][k], self.chinfo[ch][1][1][k])
					f.write(s)
				f.write('\n')
		msg.config(text = _('Data Saved'))

	def clear(self):
		if self.running == True:
			return
		for ch in range(NCHAN):
			self.chinfo[ch][1] = [ [], [] ]
		g.delete_lines()
	
	def msg(self,s):
		msgwin.config(text=s)


p = eyes.open()
ADC = ADS1115.connect(p.I2C)

root = Tk()
Canvas(root, width = WIDTH, height = 5).pack(side=TOP)  # Some space at the top
g = eyeplot.graph(root, width=WIDTH, height=HEIGHT, bip=False)	# make plot objects using draw.disp
log = ADS1115_Logger()

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)

CB = [0]*NCHAN
CH = [IntVar(), IntVar(), IntVar(), IntVar(), IntVar()]
for k in range(NCHAN):
	CB[k] = Checkbutton(cf,text ='%s'%chansrc[k], variable=CH[k], fg = 'black')
	CB[k].pack(side=LEFT, anchor = SW)
	CH[k].set(0)
CH[0].set(1)

b3 = Label(cf, text = _('Read Every'))
b3.pack(side = LEFT, anchor = SW)
TGAP = StringVar()
Dur =Entry(cf, width=5, bg = 'white', textvariable = TGAP)
TGAP.set('500')
Dur.pack(side = LEFT, anchor = SW)
b3 = Label(cf, text = _('mS,'))
b3.pack(side = LEFT, anchor = SW)
b3 = Label(cf, text = _('for total'))
b3.pack(side = LEFT, anchor = SW)
DURATION = StringVar()
Total =Entry(cf, width=5, bg = 'white', textvariable = DURATION)
DURATION.set('100')
Total.pack(side = LEFT, anchor = SW)
b3 = Label(cf, text = _('Seconds'))
b3.pack(side = LEFT, anchor = SW)
b1 = Button(cf, text = _('START'), command = log.start)
b1.pack(side = LEFT, anchor = N)
b1 = Button(cf, text = _('STOP'), command = log.stop)
b1.pack(side = LEFT, anchor = N)
b4 = Button(cf, text = _('CLEAR'), command = log.clear)
b4.pack(side = LEFT, anchor = N)

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)
b3 = Button(cf, text = _('SAVE to'), command = log.save)
b3.pack(side = LEFT, anchor = N)
filename = StringVar()
e1 =Entry(cf, width=15, bg = 'white', textvariable = filename)
filename.set('logger.dat')
e1.pack(side = LEFT)

bL = Button(cf, text = _('Fix Offset'), command = log.fixOffset)
bL.pack(side = LEFT, anchor = N)
valLabel = Label(cf, text = _('Res:'))
valLabel.pack(side = LEFT, anchor = S)


b5 = Button(cf, text = _('QUIT'), command = sys.exit)
b5.pack(side = RIGHT, anchor = N)

mf = Frame(root, width = WIDTH, height = 10)
mf.pack(side=TOP,  fill = BOTH, expand = 1)
msgwin = Label(mf,text=_('Message'), fg = 'blue')
msgwin.pack(side=LEFT)

root.title(_('EYES-Junior: Four Channel Data Logger for ADS1115 16-bit ADC'))
root.mainloop()

