#PB3 is OC0, connected to the RED of RGB LED

import time
from kuttyPy import *

setReg(DDRB,255)
csb = 1 		# Clock select bits uint8_t
WGM01=3
WGM00=6
COM01=5
setReg( TCCR0 , (1 << WGM01) | (1 << WGM00) | (1 << COM01) | csb )

while 1:
	setReg(OCR0 , 50)
	time.sleep(0.5)
	setReg(OCR0 , 200)
	time.sleep(0.5)
