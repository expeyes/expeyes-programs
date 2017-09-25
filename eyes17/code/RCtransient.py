#import eyes17.eyes          # uncomment these two lines while running stand-alone
#p = eyes17.eyes.open()

from pylab import *
import time

p.set_state(OD1=0)			# OD1 to LOW
time.sleep(.5)
t,v = p.capture_action('A1', 100, 5, 'SET_HIGH')
plot(t,v,linewidth = 2, color = 'blue')

p.set_state(OD1=1)			# OD1 to LOW
time.sleep(.5)
t,v = p.capture_action('A1', 100, 5, 'SET_LOW')

plot(t,v,linewidth = 2, color = 'red')
show()
