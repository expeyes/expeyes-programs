# Connect WG to A1

from pylab import *

def f1(x):                         #
	return sin(x) + sin(3*x)/3
	
load_equation(f1, [-pi,pi])
set_wave(400)

x,y = capture1('A1', 500,10)
plot(x,y)
show()
