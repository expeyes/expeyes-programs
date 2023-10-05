from matplotlib import pyplot as plt

p.set_sine(200)

res = p.capture4(500, 20)   # captures A1 and A2

plt.xlabel('Time(mS)')
plt.ylabel('Voltage(V)')
plt.plot([0,10], [0,0], 'black')
plt.ylim([-4,4])

plt.plot(res[0], res[1], linewidth = 2, color = 'blue')
plt.plot(res[2], res[3], linewidth = 2, color = 'red')
plt.plot(res[4], res[5], linewidth = 2, color = 'magenta')

plt.show()
