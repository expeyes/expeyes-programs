import struct, time
import numpy as np
import matplotlib.pyplot as plt

import expeyes.eyes17, time
p = expeyes.eyes17.open()
va = [] #list to fill voltage values
ia = [] # list to fill current values


fig=plt.figure()
plt.axis([0, 5, 0, 5])
plt.ion()
plt.show()

NP = 50
va =ia = [0,0,0,0]		
line, = plt.plot(va,ia)
v = 0;
while v < 5.0:
	p.set_pv1(v)
	time.sleep(0.05)
	vd = p.get_voltage('A1')
	i = (v-vd)		# in milliAmps
	va.append(vd)
	ia.append(i)
	line.set_xdata(va)
	line.set_ydata(ia)
	plt.draw()
	time.sleep(0.05)
	v += 0.1

raw_input('press Enter key to quit')


