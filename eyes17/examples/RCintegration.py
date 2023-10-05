import eyes17.eyes
p = eyes17.eyes.open()

from matplotlib import pyplot as plt

p.set_wave(500,'tria')
p.select_range('A1',4)
p.select_range('A2',4)

t,v, tt,vv = p.capture2(500, 20)   # captures A1 and A2

xlabel('Time(mS)')
ylabel('Voltage(V)')
plot([0,10], [0,0], 'black')
ylim([-4,4])

plot(t,v,linewidth = 2, color = 'blue')
plot(tt, vv, linewidth = 2, color = 'red')

show()
