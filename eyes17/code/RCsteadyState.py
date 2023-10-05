from matplotlib import pyplot as plt

set_sine(200)
set_pv1(1.35)       # will clip at 1.35 + diode drop

t,v, tt,vv = capture2(500, 20)   # captures A1 and A2

plt.xlabel('Time(mS)')
plt.ylabel('Voltage(V)')
plt.plot([0,10], [0,0], 'black')
plt.ylim([-4,4])

plt.plot(t,v,linewidth = 2, color = 'blue')
plt.plot(tt, vv, linewidth = 2, color = 'red')

plt.show()
