import serial
fd = serial.Serial('/dev/ttyS0', 38400, stopbits=1, \
    timeout = 1.0, parity=serial.PARITY_EVEN)

while 1:
  c = raw_input('Enter a character : ')
  fd.write(c)	
  print ('Receiced ', fd.read())

