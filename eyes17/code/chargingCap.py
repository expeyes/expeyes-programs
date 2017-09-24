# Connect 1k from OD1 to A1, Capacitor from A1 o Gnd

from pylab import *
import time

set_state(OD1=0)			# OD1 to LOW
time.sleep(.2)
t,v = capture_action('A1', 300, 10, 'SET_HIGH')

plot(t,v)
show()
