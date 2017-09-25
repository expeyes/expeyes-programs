from pylab import *

set_sqr1(200)
select_range('A1',8)
select_range('A2',8)

t,v, tt,vv = capture2(500, 20)   # captures A1 and A2

xlabel('Time(mS)')
ylabel('Voltage(V)')
plot([0,10], [0,0], 'black')
ylim([-6,6])

plot(t,v,linewidth = 2, color = 'blue')
plot(tt, vv, linewidth = 2, color = 'red')

show()
