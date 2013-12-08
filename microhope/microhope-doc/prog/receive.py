import serial
ser = serial.Serial('/dev/ttyS0', 38400, stopbits=1)

count = 0
val = ''
while(1):
	while ser.inWaiting() == 0:
		pass
	x=ser.read()
	if ord(x) == 0:     #Print when end of string 
		print val
		val = ''
	else:
		val = val + x
