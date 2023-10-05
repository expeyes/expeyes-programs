import eyes17.eyes
p = eyes17.eyes.open()

from matplotlib import pyplot as plt

p.set_sine(200)
p.set_pv1(1.35)       # will clip at 1.35 + diode drop

t,v, tt,vv = p.capture2(500, 20)   # captures A1 and A2

xlabel('Time(mS)')
ylabel('Voltage(V)')
plot([0,10], [0,0], 'black')
ylim([-4,4])

plot(t,v,linewidth = 2, color = 'blue')
plot(tt, vv, linewidth = 2, color = 'red')

show()
