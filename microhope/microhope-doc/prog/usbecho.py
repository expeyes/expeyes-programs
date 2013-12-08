import avr309, sys

con = avr309.avrusb()
if con.fd == None:
  print 'AVR309 USB to Serial Adapter not found. Exiting'
  sys.exit()

con.setbaud(38) 	# 38 for 38400 and 12 for 115200

while 1:
    c = raw_input('Enter a character : ')
    con.write(ord(c))
    print chr(con.read_one())
