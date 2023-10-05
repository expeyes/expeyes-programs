#import eyes17.eyes          # uncomment these two lines while running stand-alone
#p = eyes17.eyes.open()

from matplotlib import pyplot as plt

p.set_sine(200)

t,v, tt,vv = p.capture2(500, 20)   # captures A1 and A2

plt.xlabel('Time(mS)')
plt.ylabel('Voltage(V)')
plt.plot([0,10], [0,0], 'black')
plt.ylim([-4,4])

plt.plot(t,v,linewidth = 2, color = 'blue')
plt.plot(tt, vv, linewidth = 2, color = 'red')

plt.show()
