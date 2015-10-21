from __future__ import print_function

import serial, time
fd = serial.Serial('/dev/ttyUSB0', 38400, stopbits=1, timeout = 1.0)
fd.flush()	
time.sleep(1)

while 1:
  ch = input('Enter Channel Number to read ADC ')
  if ch < 0 or ch > 7:
     print ('Enter from 0 to 7 only')
     continue       	
  fd.write(chr(ch))	
  try:
    low = fd.read()
    hi = fd.read()
    adcval = (ord(hi) <<  8) | ord(low)   # make 16 bit word from the two bytes
    print ('adc out = %d , %5.3f volts'%(adcval,5.0 * adcval/1023))
  except:
    print ('No data')
