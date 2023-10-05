#import eyes17.eyes          # uncomment these two lines while running stand-alone
#p = eyes17.eyes.open()

from matplotlib import pyplot as plt

p.set_sine(200)
p.set_pv1(1.7)       # will clamp at 2.0 + diode drop

maxV = 8

p.select_range('A1', maxV)
p.select_range('A2', maxV)

t,v, tt,vv = p.capture2(500, 20)   # captures A1 and A2

plt.xlabel('Time(mS)')
plt.ylabel('Voltage(V)')
plt.plot([0,10], [0,0], 'black')
plt.ylim([-maxV, maxV])

plt.plot(t,v,linewidth = 2, color = 'blue', label='Input')
plt.plot(tt, vv, linewidth = 2, color = 'red', label='Clamped')

plt.legend(framealpha=0.5)

plt.show()
