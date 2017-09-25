from pylab import *

p.set_sine(200)

res = p.capture4(500, 20)   # captures A1 and A2

xlabel('Time(mS)')
ylabel('Voltage(V)')
plot([0,10], [0,0], 'black')
ylim([-4,4])

plot(res[0], res[1], linewidth = 2, color = 'blue')
plot(res[2], res[3], linewidth = 2, color = 'red')
plot(res[4], res[5], linewidth = 2, color = 'magenta')

show()
