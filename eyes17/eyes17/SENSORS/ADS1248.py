from __future__ import print_function
import time,sys

class ADS1248:
	MUX0 = 0x00
	VBIAS = 0x01
	MUX1 = 0x02
	SYS0 = 0x03
	OFC0 = 0x04
	OFC1 = 0x05
	OFC2 = 0x06
	FSC0 = 0x07
	FSC1 = 0x08
	FSC2 = 0x09
	IDAC0 = 0x0A
	IDAC1 = 0x0B
	GPIOCFG = 0x0C
	GPIODIR = 0x0D
	GPIODAT = 0x0E
	
	RDATAC=0x14
	SDATAC=0x16
	RDATA=0x12
	NOP=0xFF
	def __init__(self,I):
		self.cs='CS1'
		self.I = I
		self.I.SPI.set_parameters(0,1,1,0)
		#init source : https://github.com/donfuge/ADS1248/blob/master/ADS1248_minimal.py
		self.writeRegister(self.MUX0, 0b00000001);	# MUX0:  Pos. input: AIN0, Neg. input: AIN1 (Burnout current source off) 
		self.writeRegister(self.MUX1, 0b00100000);	# MUX1:  REF0, normal operation
		self.writeRegister(self.SYS0, 0b00000000);	# SYS0:  PGA Gain = 1, 5 SPS
		self.writeRegister(self.IDAC0,0b00000000);	# IDAC0: off
		self.writeRegister(self.IDAC1,0b11001100);	# IDAC1: n.c.
		self.writeRegister(self.VBIAS,0b00000000);	# VBIAS: BIAS voltage disabled
		self.writeRegister(self.OFC0, 0b00000000);	# OFC0:  0 => reset offset calibration
		self.writeRegister(self.OFC1, 0b00000000);	# OFC1:  0 => reset offset calibration
		self.writeRegister(self.OFC2, 0b00000000);	# OFC2:  0 => reset offset calibration
		self.writeRegister(self.GPIOCFG, 0b00000000);	# GPIOCFG: all used as analog inputs
		self.writeRegister(self.GPIODIR, 0b00000000);	# GPIODIR: -
		self.writeRegister(self.GPIODAT, 0b00000000);	# GPIODAT: -

	def start(self):
		self.I.SPI.start(self.cs)

	def stop(self):
		self.I.SPI.stop(self.cs)

	def send8(self,val):
		x = self.I.SPI.send8(val)
		#print val,x
		return x

	def send16(self,val):
		x=self.I.SPI.send16(val)
		#print val,x
		return x
	def write(self,regname,value):
		pass
		
	def readRegister(self,regname,numbytes):
		reply = self.I.SPI.xfer(self.cs,[0x20|regname,numbytes-1]+[0]*numbytes)
		return reply[2:]

	def writeRegister(self,regname,dat):
		print ([0x40|regname,0,dat])
		reply = self.I.SPI.xfer(self.cs,[0x40|regname,0,dat])
		return reply[2:]

	def readData(self):
		self.I.set_state(SQR1=1)
		reply = self.I.SPI.xfer(self.cs,[self.RDATA,0,0,0])
		self.I.SPI.xfer(self.cs,[self.NOP]) # sending NOP
		self.I.set_state(SQR1=0)
		return reply

	def printstat(self):
		time.sleep(0.016)
		self.start()
		self.send8(0x23) #issue RDATA
		val = self.send16(0xFFFF) #
		val<<=8
		val |= self.send8(0xFF)
		self.stop()
		print (val)
		time.sleep(0.1)




if __name__ == "__main__":
	from expeyes import eyes17
	I= eyes17.open()
	a=ADS1248(I)
	I.set_pv3(.7)
	while 1:
		time.sleep(0.5)
		print ('data ',a.readData())




