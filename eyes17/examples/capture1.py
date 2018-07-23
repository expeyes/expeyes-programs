import eyes17.eyes
p = eyes17.eyes.open()

from pylab import *
x,y = p.capture1('A1',10,10)
plot(x,y)
show()
