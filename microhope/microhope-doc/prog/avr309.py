# Class implementing communication to the USB to the Serial Adapter
# Require python-usb module installed

import usb, array, time, sys

VENDOR_ID	= 0x03eb	# Vendor ID of Atmel
PRODUCT_ID	= 0x21ff	# Atmega based usb interface
VDR  		= 0xC0		# USB Vendor device request
RS_WRITE 	= 10	
RS_READ  	= 14
RS_SETBAUD	= 12

USBMAXTRY	= 100
USBTIMEOUT	= 0
PHOENIX_ERR	= -1
MAXDATA = 802				# 800 + 2
buf = array.array('B',MAXDATA * [0])	# unsigned character array, Global

class avrusb:
  def __init__(self):
    busses = usb.busses()
    self.fd = None		# Device file handle
    for bus in busses:		
      devices = bus.devices
      for dev in devices:	# Search for AVRUSB
        if dev.idVendor == VENDOR_ID and dev.idProduct==PRODUCT_ID:
          self.dev = dev
          self.conf = self.dev.configurations[0]
          self.intf = self.conf.interfaces[0][0]
          self.fd = self.dev.open()
          self.fd.setConfiguration(self.conf)
          self.fd.claimInterface(self.intf)
          self.setbaud(38)	# 38400 baud
          self.clearbuf()
          
  def setbaud(self, val):
    self.fd.controlMsg(VDR, RS_SETBAUD, 1, value = val, index = 0)
              
  def write(self, val):
    self.fd.controlMsg(VDR, RS_WRITE, 1, value = val)
#    time.sleep(.01)
    
  def read_one(self):	 # Read one byte, no wait
      res = self.fd.controlMsg(VDR, RS_READ, 1+2)
      if len(res) > 2:
        return res[2]

  def clearbuf(self):
    while 1:
      res = self.fd.controlMsg(VDR, RS_READ, 802)
      if len(res) < 3:
        break
      else:
        print ('Cleared ', res[0] + res[1]*256, 'bytes')
  
  def read(self, nb):	 # loop until getting 'nb' bytes
    index = 0
    remaining = nb
    timer = 0
    while remaining:
      if remaining <= 200:
          bsize = remaining
      else:
          bsize = 200
      part = self.fd.controlMsg(VDR, RS_READ, bsize + 2)
      if len(part) < 3:
          timer = timer + 1
          if timer > USBMAXTRY:
              return USBTIMEOUT
          continue;
      pl = len(part) - 2
      for k in range(2,len(part)):
          buf[index] = part[k]
          index = index + 1
      remaining = remaining - pl
    return index

