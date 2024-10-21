r'''                                                                              PA0
Connect LEDs from PB0..PB7 to Ground via 5k resistors.                            |
Change the voltage at PA0 using a potentiometer, using a connection like    5V__/\/\/\__GND
'''

import time
from kuttyPy import *

ADSP2 = 2
REFS1 = 7
REFS0 = 6
ADC_SPEED = 7		# ADCClk = (8 MHz/ 128) = 62.5 KHz =>208 usec
ADEN   = 7
ADIF   = 4
ADSC   = 6

setReg(DDRA,0)

def readADC(ch):        # Read the ADC channel
	setReg(ADMUX, (1 << REFS1) | (1 << REFS0) | ch)         # REference source and channel number
	setReg(ADCSRA, 1 << ADEN | (1 << ADSC) | 1 << ADSP2)	# Enable, start and clock setting
	low = getReg(ADCL);
	hi = getReg(ADCH);
	return (hi << 8) | low

while 1:
	print (readADC(0))
	time.sleep(1)
