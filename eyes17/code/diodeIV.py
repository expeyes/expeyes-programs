from matplotlib import pyplot as plt


voltage = []
current = []

v = 0.0
while v <= 5.0:
  va = set_pv1(v)
  vd = get_voltage('A1')
  i = (va-vd)/1.0         # current in milli Amps
  voltage.append(vd)
  current.append(i)
  v = v + 0.050    # 50 mV step

plt.xlabel('Voltage')
plt.ylabel('Current')
plt.plot(voltage, current, linewidth = 2)
plt.show()
