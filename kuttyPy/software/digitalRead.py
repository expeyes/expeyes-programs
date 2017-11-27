#Connect switches from PC0..PC7 to Ground via 5k resistors

import time
from kuttyPy import *

setReg(DDRB,255)
setReg(DDRC,0)
setReg(PORTC,255)

while 1:
	val = getReg(PINC)
	print val
	setReg(PORTB, val)
	time.sleep(.1)
