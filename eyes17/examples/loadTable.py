import eyes17.eyes
p = eyes17.eyes.open()

# Connect WG to A1

from pylab import *

x = arange(-256, 256)
x = abs(x)
p.load_table(x)
p.set_wave(400)

x,y = p.capture1('A1', 500,10)
plot(x,y)
show()
