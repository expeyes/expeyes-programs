import time
from pymicro import *
u=atm32()

while 1:
	u.outb(PORTB, 1)
	time.sleep(0.5)
	u.outb(PORTB, 0)
	time.sleep(0.5)

