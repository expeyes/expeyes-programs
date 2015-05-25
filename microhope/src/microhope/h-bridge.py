import time
from pymicro import *
p=atm32()
#time.sleep(1)
p.outb(DDRA,255)
p.outb(PORTA,0)  

