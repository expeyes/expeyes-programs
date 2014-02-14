import serial, struct, time
import numpy as np
import matplotlib.pyplot as plt

READBLOCK = 1         # 1 represents readblock command for the uC
fd = serial.Serial('/dev/ttyACM0', 38400, stopbits=1, timeout = 1.0)
fd.flush()

def readblock(np,tg):		# Sends the command, NP, TG, receives data and returns it in 2 lists
	fd.write(chr(READBLOCK))
	fd.write(chr(np&255))	
	fd.write(chr(np>>8))	
	fd.write(chr(tg&255))	
	fd.write(chr(tg>>8))	
	fd.read()
	data = fd.read(np)
	raw = struct.unpack('B'* np, data)  # 8 bit data in byte array
	ta = []
	va = []
	for i in range(np):
		ta.append(0.001 * i * tg)	# convert time from microseconds to milliseconds
		va.append(raw[i] * 5.0 / 255)
	return ta, va

NP = 1000
TG = 50

fig=plt.figure()
plt.axis([0, NP*TG/1000, 0, 5])

plt.ion()
plt.show()

ta,va = readblock(NP,TG)
line, = plt.plot(ta,va)
print ta[-1]
while 1:
	ta,va = readblock(NP,TG)
	line.set_xdata(ta)
	line.set_ydata(va)
	plt.draw()
	time.sleep(0.05)
    
    
    
