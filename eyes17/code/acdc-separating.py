from matplotlib import pyplot as plt

set_sqr1(200)
select_range('A1',8)
select_range('A2',8)

t,v, tt,vv = capture2(500, 20)   # captures A1 and A2

plt.xlabel('Time(mS)')
plt.ylabel('Voltage(V)')
plt.plot([0,10], [0,0], 'black')
plt.ylim([-6,6])

plt.plot(t,v,linewidth = 2, color = 'blue')
plt.plot(tt, vv, linewidth = 2, color = 'red')

plt.show()
