#import eyes17.eyes          # uncomment these two lines while running stand-alone
#p = eyes17.eyes.open()

from pylab import *

p.set_wave(50,'tria')
p.select_range('A1',4)
p.select_range('A2',4)

t,v, tt,vv = p.capture2(500, 100)   # captures A1 and A2

xlabel('Time(mS)')
ylabel('Voltage(V)')
plot([0,1], [0,0], 'black')
ylim([-4,4])

plot(t,v,linewidth = 2, color = 'blue')
plot(tt, vv, linewidth = 2, color = 'red')

show()
