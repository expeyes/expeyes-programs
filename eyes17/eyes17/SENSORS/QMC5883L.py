from numpy import int16
def connect(route,**args):
	return QMC5883L(route,**args)


class QMC5883L():			
	#--------------Parameters--------------------
	#This must be defined in order to let GUIs automatically create menus
	#for changing various options of this sensor
	#It's a dictionary of the string representations of functions matched with an array
	#of options that each one can accept
	params={	'init':['Now'],
	'QMC_RANGE':['2G','8G'],
	}
	ADDRESS = 13
	name = 'Magnetometer'
	NUMPLOTS=3	
	PLOTNAMES = ['Bx','By','Bz']
	QMC_scaling = 3000
	def __init__(self,I2C,**args):
		self.I2C=I2C
		self.ADDRESS = args.get('address',self.ADDRESS)
		self.name = '3 axis Magnetometer'
		self.init('')

	def init(self,dummy_variable_to_circumvent_framework_limitation):  # I know how to fix this now. remind me.
		self.I2C.writeBulk(self.ADDRESS,[0x0A,0x80]) #0x80=reset. 0x40= rollover
		self.I2C.writeBulk(self.ADDRESS,[0x0B,0x01]) #init , set/reset period
		self.QMC_RANGE('2G')

	def QMC_RANGE(self,r):
		if r=='2G':
			self.I2C.writeBulk(self.ADDRESS,[0x09,0b001|0b000 | 0b100 | 0b10000]) #Mode. continuous|oversampling(512) | rate 50Hz | range(8g)
			self.QMC_scaling = 3000
		elif r=='8G':
			self.I2C.writeBulk(self.ADDRESS,[0x09,0b001|0b000 | 0b100 | 0b00000]) #Mode. continuous|oversampling(512) | rate 50Hz | range(2g)
			self.QMC_scaling = 12000	

	def getVals(self,addr,numbytes):
		vals = self.I2C.readBulk(self.ADDRESS,addr,numbytes) 
		return vals
	
	def getRaw(self):
		vals=self.getVals(0x00,6)
		if vals:
			if len(vals)==6:
				return [int16((vals[a*2+1]<<8)|vals[a*2])/self.QMC_scaling for a in range(3)]
			else:
				return False
		else:
			return False		

if __name__ == "__main__":
	print('hello')
