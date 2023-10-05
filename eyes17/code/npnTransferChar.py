#import eyes17.eyes          # uncomment these two lines while running stand-alone
#p = eyes17.eyes.open()
from __future__ import print_function
from matplotlib import pyplot as plt
vcc = p.set_pv1(4.8)

iba = []
ica = []

pv2 = 0.8
while pv2 <= 3: 
	p.set_pv2(pv2)     
	a2 = p.get_voltage('A2')
	ib = (pv2-a2)/100e3

	a1 =  p.get_voltage('A1')
	ic = (vcc - a1)/1000
	iba.append(ib)
	ica.append(ic)
	print (ib, ic)
	pv2 += 1
plt.plot(iba,ica)
plt.show()
