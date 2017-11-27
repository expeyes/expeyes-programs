
#Connect LEDs from PD0..PD7 to Ground via 5k resistors.

import time
from kuttyPy import *

setReg(DDRD,255)

while 1:
	setReg(PORTD, 255)
	time.sleep(1)
	setReg(PORTD, 0)
	time.sleep(1)

