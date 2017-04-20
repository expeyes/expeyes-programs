import serial, struct, time
import numpy as np
import matplotlib.pyplot as plt

import expeyes.eyes17
dev=expeyes.eyes17.open()

NP = 1000
TG = 10

dev.set_gain('A1', 1)
dev.set_sine(1000)
dev.set_sqr1(1000)

fig=plt.figure()
plt.axis([0, NP*TG*0.001, -5, 5])
plt.ion()
plt.show()

t,v = dev.capture1('A1', NP, TG)   
#print t[-1]
line, = plt.plot(t,v)

t,v,tt,vv = dev.capture2( NP, TG)   
print tt[-1]

while 1:
	t,v = dev.capture1('A1', NP, TG)    
	line.set_xdata(t)
	line.set_ydata(v)
	plt.draw()
	time.sleep(0.1)
    
    
    
