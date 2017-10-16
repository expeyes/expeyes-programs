'''                                                                              PA0
Connect LEDs from PB0..PB7 to Ground via 5k resistors.                            |
Change the voltage at PA0 using a potentiometer, using a connection like    5V__/\/\/\__GND
'''

import time
from kuttyPy import *

setReg(DDRB,255)

while 1:
	x  = readADC(0) >> 2
	setReg(PORTB, x)

