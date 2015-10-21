from __future__ import print_function

import expeyes.eyes, time
p=expeyes.eyes.open()

p.set_upv(2.5)
p.set_sqr1(100)
p.clear_hist()
p.start_hist()
time.sleep(5)
p.stop_hist()
a = p.read_hist()
for k in a:
	if k[1] != 0:
		print (k)

