from layouts.advancedLoggerTools import inputs
import eyes17.eyes
import time
from matplotlib import pyplot as plt
dev = eyes17.eyes.open(ip='192.168.29.163', port=8080)
#dev = eyes17.eyes.open_android()
dev.set_sq1(2000)
plt.ion()
for a in range(1):
	st  = time.time()
	#v = dev.get_version()
	#print('Version',v, time.time()-st)
	x1,y1, x2, y2 = dev.capture2(2000, 5)
	plt.clf()
	plt.plot(x1,y1)
	plt.plot(x2,y2)
	plt.pause(0.05)

plt.ioff()
plt.show()