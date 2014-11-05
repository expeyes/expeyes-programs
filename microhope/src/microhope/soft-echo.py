import serial
fd = serial.Serial('/dev/ttyACM1', 9600, stopbits=1, timeout = 1.0)


while 1:
  c = raw_input('Enter a character : ')
  fd.write(c)	
  print 'Receiced ', fd.read()
