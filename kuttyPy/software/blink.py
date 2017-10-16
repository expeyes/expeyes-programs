
#Connect LEDs from PB0..PB7 to Ground via 5k resistors.

import time
from kuttyPy import *

setReg(DDRB,255)

while 1:
	setReg(PORTB, 255)
	time.sleep(1)
	setReg(PORTB, 0)
	time.sleep(1)

