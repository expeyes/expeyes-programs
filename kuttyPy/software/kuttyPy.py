import serial, time, platform, sys,struct

VERSION = 99        # uC return this when GETVER is send

GETVER = 1			# Codes for the uC communication
READB  = 2   		
WRITEB = 3        

# Register addresses of ATmega32 micro-controller
TWAR	= 0X22
TWDR	= 0X23
ADCL	= 0X24       # ADC data
ADCH	= 0X25
ADCSRA	= 0X26		# ADC status/control
ADMUX	= 0X27       # ADC channel, reference
ACSR	= 0X28
UBRRL	= 0X29
UCSRB	= 0X2A
UCSRA	= 0X2B
UDR		= 0X2C
SPCR	= 0X2D
SPSR	= 0X2E
SPDR	= 0X2F
PIND	= 0x30       # Port D input
DDRD	= 0x31		# Port D direction
PORTD	= 0x32		# Port D output
PINC	= 0x33
DDRC	= 0x34
PORTC	= 0x35
PINB	= 0x36
DDRB	= 0x37
PORTB	= 0x38
PINA	= 0x39
DDRA	= 0x3A
PORTA	= 0x3B
EECR	= 0X3C
EEDR	= 0X3D
EEARL	= 0X3E
EEARH	= 0X3F

OCR2	= 0X43		# Timer/Counter 2  Output Compare  Reg
TCNT2	= 0X44		# Counter2 
TCCR2	= 0x45		# Timer/Counter 2 control reg
ICR1L	= 0X46
ICR1H	= 0X47
OCR1BL	= 0X48
OCR1BH	= 0X49
OCR1AL	= 0X4A
OCR1AH	= 0X4B
TCNT1L	= 0X4C
TCNT1H	= 0X4D
TCCR1B	= 0X4E
TCCR1A	= 0x4F
SFIOR	= 0X50

TCNT0	= 0x52		# Timer/ Counter 0
TCCR0	= 0x53
MCUCSR	= 0X54
MCUCR	= 0X55
TWCR	= 0X56
SPMCR	= 0X57
TIFR	= 0X58
TIMSK	= 0X59
GIFR	= 0X5A
GICR	= 0X5B
OCR0	= 0x5C
SPL		= 0X5D
SPH		= 0x5E
SREG	= 0X5F

# Register bit definitions
REF_EXT	= 0			# Feed reference voltage externally
REF_INT	= (3<<6)	# use the 2.56 V internal reference
REF_AVCC = (1<<6)	# Connect AVCC internally to reference
ADMAX = 7			# channels 0 to 7 
ADC_SPEED = 7		# ADCClk = (8 MHz/ 128) = 62.5 KHz =>208 usec
ADEN   = 7
ADIF   = 4
ADSC   = 6


#--------------------Function that communicate to ATmega32 -------------------
fd = None
def connectKP(s):  	 # Establish connection to ATmega32 connected to USB port
	global fd
	try:
		fd = serial.Serial(s, 9600, stopbits=1, timeout = 0.1)    #to overcome a possible bug in pyserial
		fd.flush();fd.read(1)									  # not required for all versions
		fd.close()
		
		fd = serial.Serial(s, 38400, stopbits=1, timeout = 1.0)
		if fd == None: 
			return None
		fd.setRTS(level=0)				# Set the RTS LED ON
		fd.flush()
		fd.write(chr(GETVER))			# Look for kuttyPy signature
		res = fd.read()
		ver = ord(res)
		if ver == VERSION:
			return fd
		else:
			print 'Found port %s, but no kuttyPy on it',s
			return None
	except:
		pass
	#Exception as e:
	#print str(e)
		
def findKP():
	device_list = []
	pf = platform.platform()
	if 'Windows' in pf:	
		for k in range(1,255):
			s = 'COM%d'%k
			device_list.append(s)
		for k in range(1,11):
			device_list.append(k)
	elif 'inux' in pf:	
		device_list = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyACM0','/dev/ttyACM1']
	#print device_list
	for dev in device_list:
		res = connectKP(dev)
		if res != None:
			print 'KuttyPy found on port ',dev
			return res
	

def setReg(reg, data):
	fd.write(chr(WRITEB))
	time.sleep(0.01)
	fd.write(chr(reg))
	time.sleep(0.01)
	fd.write(chr(data))

def getReg(port):
	fd.write(chr(READB))
	time.sleep(0.01)
	fd.write(chr(port))
	val = fd.read()
	return ord(val)

#-----------------------------------------------------------------

def readADC(ch):        # Read the ADC channel
	setReg(ADMUX, REF_INT | ch)
	setReg(ADCSRA, 1 << ADEN | (1 << ADSC) | ADC_SPEED)		# Enable the ADC
	low = getReg(ADCL);
	hi = getReg(ADCH);
	return (hi << 8) | low

#---------------------------------------------------------------------------------------------------

KP = findKP()
if KP == None:
	print 'Hardware NOT detected. Exiting'
	sys.exit(0)
	

