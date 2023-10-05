import eyes17.eyes
p = eyes17.eyes.open()

from matplotlib import pyplot as plt

p.set_sine(200)
p.set_pv1(1.7)       # will clamp at 2.0 + diode drop

maxV = 8

p.select_range('A1', maxV)
p.select_range('A2', maxV)

t,v, tt,vv = p.capture2(500, 20)   # captures A1 and A2

xlabel('Time(mS)')
ylabel('Voltage(V)')
plot([0,10], [0,0], 'black')
ylim([-maxV, maxV])

plot(t,v,linewidth = 2, color = 'blue', label='Input')
plot(tt, vv, linewidth = 2, color = 'red', label='Clamped')

legend(framealpha=0.5)

show()
