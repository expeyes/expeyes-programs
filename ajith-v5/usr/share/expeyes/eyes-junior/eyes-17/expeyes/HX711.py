import struct,time
Byte =     struct.Struct("B") # size 1
ShortInt = struct.Struct("H") # size 2
Integer=   struct.Struct("I") # size 4

from numpy import int32,int16

class HX711():
	MAIN_COMMAND = 11 #common section
	SUB_COMMAND = 29 #HX711
	def __init__(self,H):
		self.H = H
		self.scale = 64

	def enable(self):
		"""
		Enables the sensor by pulling SCK low		
		
		"""
		self.H.__sendByte__(self.MAIN_COMMAND)
		self.H.__sendByte__(self.SUB_COMMAND)
		self.H.__sendByte__(1)
		self.H.__get_ack__()

	def disable(self):
		"""
		Disables the sensor by pulling SCK high
		
		"""
		self.H.__sendByte__(self.MAIN_COMMAND)
		self.H.__sendByte__(self.SUB_COMMAND)
		self.H.__sendByte__(0)
		self.H.__get_ack__()

	def read(self,channel):
		"""
		Reads values from the sensor
		
		================	============================================================================================
		**Arguments** 
		================	============================================================================================
		channel				options
						* 'A128'     reads channel A with 128x gain
						* 'B32'     reads channel B with 32x gain
						* 'A64'     reads channel A with 64x gain
		================	============================================================================================

		:return: value returned by slave device
		"""
		index = ['A128','B32','A64'].index(channel)
		self.H.__sendByte__(self.MAIN_COMMAND)
		self.H.__sendByte__(self.SUB_COMMAND)
		self.H.__sendByte__(25+index)
		msb = self.H.__getInt__()
		lsb = self.H.__getInt__()
		self.H.__get_ack__()
		if lsb&0x100:
			print 'sensor busy'
		val = (msb<<8)|(lsb&0xFF)
		val = float(int32((val<<8)&0xFFFFFFFF)>>8)/self.scale
		self.scale = [128,32,64][index]
		return val

if __name__ == "__main__":
	import eyes17
	I=eyes17.open()
	while 1:
		time.sleep(0.1)
		print I.HX711.read('A64')
