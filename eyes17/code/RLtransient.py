#import eyes17.eyes          # uncomment these two lines while running stand-alone
#p = eyes17.eyes.open()

from matplotlib import pyplot as plt
import time


plt.plot([0,.5], [0,0], color='black')
plt.ylim([-5,5])


p.set_state(OD1=1)			# OD1 to LOW
time.sleep(.5)
t,v = p.capture_action('A1', 100, 5, 'SET_LOW')

plt.plot(t,v,linewidth = 2, color = 'red')
plt.show()
