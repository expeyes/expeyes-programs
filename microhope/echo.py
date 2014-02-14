import serial
try:
	fd = serial.Serial('/dev/ttyUSB0', 38400, stopbits=1, timeout = 1.0)
except:
	fd = serial.Serial('/dev/ttyACM0', 38400, stopbits=1, timeout = 1.0)


while 1:
  c = raw_input('Enter a character : ')
  fd.write(c)	
  print 'Receiced ', fd.read()
