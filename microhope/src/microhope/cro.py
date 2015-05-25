import serial, struct, time
import numpy as np
import matplotlib.pyplot as plt

NP = 500
TG = 100

fd = serial.Serial('/dev/ttyACM0', 38400, stopbits=1, timeout = 1.0)
fd.flush()

fig=plt.figure()
plt.axis([0, NP*TG/1000, 0, 5])
plt.ion()
plt.show()

va =ta = range(NP)
line, = plt.plot(ta,va)
while 1:
	fd.write(chr(1))		# 1 is the readblock command for uC end
	print fd.read()		    # This must be a 'D'
	data = fd.read(NP)
	raw = struct.unpack('B'* NP, data)  # 8 bit data in byte array
	ta = []
	va = []
	for i in range(NP):
		ta.append(0.001 * i * TG)	# convert time from microseconds to milliseconds
		va.append(raw[i] * 5.0 / 255)
	line.set_xdata(ta)
	line.set_ydata(va)
	plt.draw()
	time.sleep(0.05)
    
    
    
