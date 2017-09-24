
from pylab import *

set_sine(1000)
res = capture4(300, 10)  # returns four sets of data
plot(res[0], res[1])   # A1
plot(res[2], res[3])   # A2
plot(res[4], res[5])   # A3
plot(res[6], res[7])   # MIC
show()
