from __future__ import print_function
import numpy as np
gains=[1,2,4,5,8,10,16,32,1/11.]

#-----------------------Classes for input sources----------------------
# Variables , and functions
# allAnalogChannels : A list of available input channels that are used to populate drop down menus in apps like the oscilloscope
#                     Its use can be avoided if the inputRanges dict is migrated to OrderedDict
# bipolars : bipolar input channels. Accept both positive and negative input voltages
# inputRanges : a dictionary with channel_name as key , and a tuple as value. The tuple's first part is the voltage for a raw ADC
#               reading of 0 , and second value is for a raw ADC reading of 4095 in 12-bit mode. These are used for scaling in the
#               absence of calibration data. Since A1, A2 are fed through an inverting op-amp in the hardware, raw ADC 0 = 16.5V

allAnalogChannels = ['A1','A2','A3','MIC','IN1','SEN','AN8','CCS']

bipolars = ['A1','A2','A3','MIC']
inputRanges={'A1':[16.5,-16.5],	#Specify inverted channels explicitly by reversing range!!
'A2':[16.5,-16.5],
'A3':[-3.3,3.3],					#external gain control analog input
'MIC':[-3.3,3.3],					#connected to MIC amplifier
'IN1':[0,3.3],
'SEN':[0,3.3],
'AN8':[0,3.3],
'CCS':[0,3.3],
}


picADCMultiplex={'A1':3,'A2':0,'A3':1,'MIC':2,'IN1':5,'CCS':6,'SEN':7,'AN8':8}
gainPGAs = {'A1':1,'A2':2}


class analogInputSource:
	gain_values=gains
	gainEnabled=False
	gain=None
	gainPGA=None
	inverted=False
	inversion=1.
	calPoly10 = np.poly1d([0,3.3/1023,0.])
	calPoly12 = np.poly1d([0,3.3/4095,0.])
	calibrationReady=False
	defaultOffsetCode=0
	def __init__(self,name,**args):
		self.name = name			#The generic name of the input. like 'A1', 'IN1' etc
		self.CHOSA = picADCMultiplex[self.name]
		self.polynomials={}
		self.calibrationCorrection={}  #Percentage error of calibration coefficient at extremum
		self.calibrationError=False  # Will be set to True if any channel exceeds 30% error

		self.R=inputRanges[name]
		
		if self.R[1]-self.R[0] < 0:
			self.inverted=True
			self.inversion=-1

		self.scaling=1.
		if name in gainPGAs:
			self.gainEnabled=True
			self.gainPGA = gainPGAs[name]
			self.gain=0		#This is not the gain factor. use self.gain_values[self.gain] to find that.

		self.gain=0
		self.regenerateCalibration()



	def setGain(self,g):
		'''
		specify gain 1,2,4,5,8,10,16,32
		used for correctly scaling ADC codes
		'''
		if not	self.gainEnabled:
			print ('Analog gain is not available on',self.name)
			return False
		self.gain=self.gain_values.index(g)
		self.regenerateCalibration()

	def __setGain__(self,g):
		'''
		specify gain index 0,1,2,3,4,5,6,7
		used for correctly scaling ADC codes
		'''
		if not	self.gainEnabled:
			print ('Analog gain is not available on',self.name)
			return False
		self.gain=g
		self.regenerateCalibration()

	def inRange(self,val):
		v = self.voltToCode12(val)
		return (v>=0 and v<=4095)

	def __conservativeInRange__(self,val,delta=100):
		v = self.voltToCode12(val)
		return (v>=0+delta and v<=4095-delta)

	def __conservativeInRangeRaw__(self,val,delta=100):
		return (val>=0+delta and val<=4095-delta)


	def __ignoreCalibration__(self):
		self.calibrationError = True
		self.calibrationReady = False

	def loadPolynomials(self,polys):
		B=self.R[1]
		A=self.R[0]
		intercept = self.R[0]
		
		for a in range(len(polys)):
			epoly = [float(b) for b in polys[a]]			
			newPoly = np.poly1d(epoly)
			
			gain = self.gain_values[a]
			slope = (B-A)/gain/4095.
			intercept = A/gain
			idealPoly = np.poly1d([0,slope,intercept])
			#print (self.name,a,newPoly(4095),idealPoly(4095))
			err = 100*abs((newPoly(4095)-idealPoly(4095))/idealPoly(4095))
			self.calibrationCorrection[a] = err
			if (err > 30.):   #Greater than 30% deviation from ideal
				self.calibrationError = True
				self.polynomials[a] = idealPoly
				print ('Calibration invalid for %s at Gain %dx | %.2f'%(self.name,gain,err))
			else:
				self.polynomials[a] = newPoly


	def regenerateCalibration(self):
		B=self.R[1]
		A=self.R[0]
		intercept = self.R[0]
		
		if self.gain!=None:
				gain = self.gain_values[self.gain]
				B = B/gain
				A = A/gain


		slope = B-A
		intercept = A
		if self.calibrationReady and self.gain!=8 :  #special case for 1/11. gain
			self.calPoly10 = self.__cal10__
			self.calPoly12 = self.__cal12__

			#self.voltToCode10 = np.poly1d([0,1023./slope,-1023*intercept/slope])
			#self.voltToCode12 = np.poly1d([0,4095./slope,-4095*intercept/slope])			
			#Inverse of the calibration polynomials .
			self.voltToCode12 = lambda x:np.clip( (self.polynomials[self.gain]-x).roots[1] , 0 , 4090)
			self.voltToCode10 = lambda x:np.clip( ((self.polynomials[self.gain]-x).roots[1])*1023./4095 , 3 , 1020)
			
		else:
			self.calPoly10 = np.poly1d([0,slope/1023.,intercept])
			self.calPoly12 = np.poly1d([0,slope/4095.,intercept])

			self.voltToCode10 = np.poly1d([0,1023./slope,-1023*intercept/slope])
			self.voltToCode12 = np.poly1d([0,4095./slope,-4095*intercept/slope])


	def __cal12__(self,RAW):
		return self.polynomials[self.gain](RAW)

	def __cal10__(self,RAW):
		RAW*=4095/1023.
		return self.polynomials[self.gain](RAW)


'''
for a in ['CH1']:
	x=analogInputSource(a)
	print (x.name,x.calPoly10#,calfacs[x.name][0])
	print ('CAL:',x.calPoly10(0),x.calPoly10(1023))
	x.setOffset(1.65)
	x.setGain(32)
	print (x.name,x.calPoly10#,calfacs[x.name][0])
	print ('CAL:',x.calPoly10(0),x.calPoly10(1023))
'''
#---------------------------------------------------------------------



class analogAcquisitionChannel:
	'''
	This class takes care of oscilloscope data fetched from the device.
	Each instance may be linked to a particular input.
	Since only up to two channels may be captured at a time with the vLabtool, only two instances will be required
	
	Each instance will be linked to a particular inputSource instance by the capture routines.
	When data is requested , it will return after applying calibration and gain details
	stored in the selected inputSource
	'''
	def __init__(self,a):
		self.name=''
		self.gain=0
		self.channel=a
		self.channel_names=allAnalogChannels
		#REFERENCE VOLTAGE = 3.3 V
		self.calibration_ref196=1.#measured reference voltage/3.3
		self.resolution=10
		self.xaxis=np.zeros(10000)
		self.yaxis=np.zeros(10000)
		self.length=100
		self.timebase = 1.
		self.source = analogInputSource('A1') #use CH1 for initialization. It will be overwritten by set_params

	def fix_value(self,val):
		#val[val>1020]=np.NaN
		#val[val<2]=np.NaN
		if self.resolution==12:
			return self.calibration_ref196*self.source.calPoly12(val)
		else:return self.calibration_ref196*self.source.calPoly10(val)

	def set_yval(self,pos,val):
		self.yaxis[pos] = self.fix_value(val)

	def set_xval(self,pos,val):
		self.xaxis[pos] = val

	def set_params(self,**keys):
		self.gain = keys.get('gain',self.gain)	
		self.name = keys.get('channel',self.channel)	
		self.source = keys.get('source',self.source)
		self.resolution = keys.get('resolution',self.resolution)	
		l = keys.get('length',self.length)	
		t = keys.get('timebase',self.timebase)
		if t != self.timebase or l != self.length:
			self.timebase = t
			self.length = l
			self.regenerate_xaxis()

	def regenerate_xaxis(self):
		for a in range(int(self.length)): self.xaxis[a] = self.timebase*a

	def get_xaxis(self):
		return self.xaxis[:self.length]
	def get_yaxis(self):
		return self.yaxis[:self.length]

