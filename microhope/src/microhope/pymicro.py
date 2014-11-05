''' 
Program : pymicro.py
author  : Ajith Kumar (ajith@iuac.res.in)
License : GNU GPL version 3 or above
A program to read/write the microcontroller registers 
'''

READB  = 1   # Codes for the uC end
WRITEB = 2        

ADCL   = 0X24       # ADC data
ADCH   = 0X25
ADCSRA = 0X26		# ADC status/control
ADMUX  = 0X27       # ADC channel, reference
PIND   = 0x30       # Port D input
DDRD   = 0x31		# Port D direction
PORTD  = 0x32		# Port D output
PINC   = 0x33
DDRC   = 0x34
PORTC  = 0x35
PINB   = 0x36
DDRB   = 0x37
PORTB  = 0x38
PINA   = 0x39
DDRA   = 0x3A
PORTA  = 0x3B
OCR2   = 0X43		# Timer/Counter 2  Output Compare  Reg
TCNT2  = 0X44		# Counter2 
TCCR2  = 0x45		# Timer/Counter 2 control reg
TCNT0  = 0x52		# Timer/ Counter 0
TCCR0  = 0x53
OCR0   = 0x5C

import serial, time

class atm32:
	fd = None
	def __init__(self):   # Establish connection to ATmega32 connected to USB port
		self.fd = serial.Serial('/dev/ttyACM0', 38400, stopbits=1, timeout = 1.0)
		time.sleep(2)   # even if user forgets to remove PCRST jumper
		if self.fd == None:
			print 'Error opening ATmega32 connection'
	
	def outb(self,port, data):			#Output a byte to the specified port 
		self.fd.write(chr(WRITEB))
		self.fd.write(chr(port))
		self.fd.write(chr(data))

	def inb(self,port):					#Read a byte from the specified port 
		self.fd.write(chr(READB))
		self.fd.write(chr(port))
		val = self.fd.read()
		return ord(val)
	

