# Reads and plots data from three channels of Phoenix, for 'maxtime' seconds.
# Uses draw.py
from __future__ import print_function

from tkinter import *
import phm, draw, time, sys

NUMCHANS = 1		# Change number of channels if you like

WIDTH  = 600   # width of drawing canvas
HEIGHT = 150   # height    
datahistory = []       # store data      
data  = [ [],[],[] ]
dispobjects = [] 	# Objects of class display
running = False
starts  = [0,0,0]      # starting times for three channels
maxvolts = 5000.0
timegap = 5           # minimum msecs between reads
maxtime = 10.0	       # Total duration of the run in seconds

def update():	# Called periodically by the Tk toolkit
	global data, running, timegap, ph, NUMCHANS
	if running == False:
		return
	for ch in range(NUMCHANS):
		if NUMCHANS > 1 :	  # save some time
			ph.select_adc(ch)
		res = ph.get_voltage()
		x = res[0] - starts[ch]
		y = res[1]
		data[ch].append((x,y))
		if len(data[ch]) > 1:
			dispobjects[ch].delete_lines()
			dispobjects[ch].line(data[ch], 'black')
	if x <= maxtime:	# remove this condition to stop only by the STOP Button
		root.after(timegap, update)

def save():
	global data, running, filename
	s = e1.get()
	print (s)
	if s == '':
		s = filename
	f = open(s, 'w')
	for ch in range(NUMCHANS):
		for item in data[ch]:
			f.write('%5.3f  %5.0f\n'%(item[0], item[1]))
		f.write('\n')
	f.close()
	print ('Data saved to file ', s)

def clear():
	global data, dispobjects, running
	if running == True:
		return
	for ch in range(NUMCHANS):
		data[ch] = []
		dispobjects[ch].delete_lines()

def start():
	global data, running, starts, timegap
	running = True
	s = time.time()  # time stamp
	starts[0] = starts[1] = starts[2] = s
	data  = [ [],[],[] ]
	root.after(timegap, update)

def stop():
	global running
	running = False

def setduration(self):
	global maxtime
	maxtime = Scale.get()
	for ch in range(NUMCHANS):
		dispobjects[ch].delete_lines()
		dispobjects[ch].setWorld(0, 0, maxtime, maxvolts)
		dispobjects[ch].mark_axes('Seconds','mV')
		if len(data[ch]) > 1:
			#dispobjects[ch].delete_lines()
			dispobjects[ch].line(data[ch], 'black')
def quit():
	sys.exit()

ph = phm.phm()
ph.set_adc_size(2)
ph.select_adc(0)    # Use this is NUMCHANS = 1

root = Tk()
Canvas(root, width = WIDTH, height = 5).pack(side=TOP)  # Some space at the top
for k in range(NUMCHANS):					
	w = draw.disp(root, width=WIDTH, height=HEIGHT)	# make plot objects using draw.disp
	w.setWorld(0, 0, maxtime, maxvolts)
	w.mark_axes('Seconds','mV')
	dispobjects.append(w)

dispobjects[0].mark_axes('milli Seconds','mV')

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)
b1 = Button(cf, text = 'START', command = start)
b1.pack(side = LEFT, anchor = N)
b2 = Button(cf, text = 'STOP', command = stop)
b2.pack(side = LEFT, anchor = N)
b3 = Button(cf, text = 'SAVE to', command = save)
b3.pack(side = LEFT, anchor = N)
filename = StringVar()
e1 =Entry(cf, width=15, bg = 'white', textvariable = filename)
filename.set('logger.dat')
e1.pack(side = LEFT)

Scale = Scale(cf,command = setduration, orient=HORIZONTAL, length=200,\
		from_ = 10,to=1000, resolution=10)
Scale.pack(side=LEFT)

b4 = Button(cf, text = 'CLEAR', command = clear)
b4.pack(side = LEFT, anchor = N)
b5 = Button(cf, text = 'QUIT', command = quit)
b5.pack(side = RIGHT, anchor = N)

root.title('Phoenix Based Data Logger')
root.mainloop()

