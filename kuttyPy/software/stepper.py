#Connect unipolar Stepper Motor coils to PA0, PA1, PA2 and PA3. Power from 5V

import time
from kuttyPy import *

seq = [12,6,3,9]
pos = 0

def rotateMotor (nsteps, direction):
	global seq, pos
	for k in range(nsteps):
		if direction == 1:
			pos = (pos + 1) & 3
		else:
			if pos == 0:
				pos = 3
			else:
				pos -= 1
		setReg(PORTA,seq[pos])         # set the uC register 
		print 'PORTA set to ',seq[pos]
		time.sleep(.05)


setReg(DDRA,15)    # make PA0 to PA3 as outputs

while 1:
	rotateMotor(100, 1)
	rotateMotor(100, 0)
	

