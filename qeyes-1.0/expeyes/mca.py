'''
EYES MCA
Python library to communicate to the AtMega32 uC running 'eyes.c'
Author  : Ajith Kumar B.P, bpajith@gmail.com
License : GNU GPL version 3
Last Edit : 20-Nov-2011
'''

import serial, struct, math, time, commands, sys, os

#Commands with One byte argument (41 to 80) 
GETVERSION  =   1
READCH0     =   2
STARTHIST	=  10	# Start histogramming
READHIST	=  11	# Send the histogram to PC, 2 x 256 bytes data
CLEARHIST	=  12	# Send the histogram to PC, 2 x 256 bytes data
STOPHIST	=  13	# Stop histogramming

NUMCHANS    = 512   # 512 channels, of 2 bytes
WORDSIZE	= 2

#Serial devices to search for EYES hardware.  
linux_list = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2', '/dev/ttyUSB3', '/dev/tts/USB0','/dev/tts/USB1']
BAUDRATE = 38400

def open(dev = None):
	'''
	If EYES hardware in found, returns an instance of 'Eyes', else returns None.
	'''
	obj = Eyes()
	if obj.fd != None:
		return obj
	print 'Could not find Phoenix-EYES hardware'
	print 'Check the connections.'

class Eyes:
	#buf = array.array('B',BUFSIZE * [0])    # unsigned character array, Global
	fd = None								# init should fill this
	adcsize = 1

	def __init__(self, dev = None):
		"""
		Searches for MCA hardware on the USB-to-Serial adapters.Presence of the
		device is done by reading the version string.
		"""
	
		if os.name == 'nt':	
			device_list = []
			for k in range(1,100):
				s = 'COM%1d'%k
				device_list.append(s)
			for k in range(1,11):
				device_list.append(k)
		else:
			device_list = linux_list
		

		for dev in device_list:
			print dev
			try:
				handle = serial.Serial(dev, BAUDRATE, stopbits=1, timeout = 0.3, \
					parity=serial.PARITY_EVEN)
			except:
				continue
			print 'Port %s is existing '%dev,
			if handle.isOpen() != True:
				print 'but could not open'				
				continue
			print 'and opened. ',
			handle.flush()
			while handle.inWaiting() > 0 :
				print 'inWaiting'
				handle.flushInput()
			handle.write(chr(GETVERSION))
			res = handle.read(1)
			print res
			ver = handle.read(5)		# 5 character version number
			print ver
			if ver[:2] == 'mc':
				self.device = dev
				self.fd = handle
				self.version = ver
				handle.timeout = 3.0	# 
				print 'Found MCA version ',ver
				return 
			else:
				print 'No MCA hardware detected'
				self.fd = None

#------------------------------------------Histogram-----------------------------------
	def start_hist(self):
		'''
		Enables the Interrupt that handles the
		Pulse processing plug-in.
		'''
		self.fd.write(chr(STARTHIST))
		self.fd.read(1)

	def stop_hist(self):
		'''
		Disables the Analog Comparator Interrupt
		'''
		self.fd.write(chr(STOPHIST))
		self.fd.read(1)

	def clear_hist(self):
		'''
		Clear the Histogram memory at ATmega32
		'''
		self.fd.write(chr(CLEARHIST))
		self.fd.read(1)

	def read_hist(self):
		'''
		Reads the Histogram memory to PC. 
		1 byte status + 1 byte header + 256 x 2 bytes of data
		'''
		self.fd.write(chr(READHIST))
		res = self.fd.read(1)
		if res != 'D':
			return None
		self.fd.read(1)           # The pad byte
		data = self.fd.read(NUMCHANS*WORDSIZE)
		dl = len(data)
		#for k in data: print ord(k),
		if dl != NUMCHANS*WORDSIZE:
			print 'HIST read data error'
			return None
		raw = struct.unpack('H'* (NUMCHANS), data)  	# 16 bit data in uint16 array
		ch = []
		nn = []
		for i in range(NUMCHANS):
			ch.append(i)
			nn.append(raw[i])
		return ch,nn

	def read_adc(self, ch):
		'''
		Reads the specified ADC channel, returns a number from 0 to 4095. Low level routine.
		'''
		if (ch > 7):
			print 'Argument error'
			return
		self.fd.write(chr(READADC))
		self.fd.write(chr(ch))
		res = self.fd.read(1)
		if res != 'D':
			print 'READADC error ', res
			return
		res = self.fd.read(2)
		iv = ord(res[0]) | (ord(res[1]) << 8)
		return iv

#----------------------------------analysis------------------------------------
	def maximum(self,va):
		vmax = 1.0e-10		# need to change
		for v in va:
			if v > vmax:
				vmax = v
		return vmax

	def save(self, data, filename = 'plot.dat'):
		'''
		Input data is of the form, [ [x1,y1], [x2,y2],....] where x and y are vectors
		'''
		if data == None: return
		import __builtin__					# Need to do this since 'eyes.py' redefines 'open'
		f = __builtin__.open(filename,'w')
		for xy in data:
			for k in range(len(xy[0])):
				f.write('%5.3f  %5.3f\n'%(xy[0][k], xy[1][k]))
			f.write('\n')
		f.close()

	def grace(self, data, xlab = '', ylab = '', title = ''):
		'''
		Input data is of the form, [ [x1,y1], [x2,y2],....] where x and y are vectors
		'''
		try:
			import pygrace
			pg = pygrace.grace()
			for xy in data:
				pg.plot(xy[0],xy[1])
				pg.hold(1)				# Do not erase the old data
			pg.xlabel(xlab)
			pg.ylabel(ylab)
			pg.title(title)
			return True
		except:
			return False


