# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
# eyes17 - software stack to support the eyesj2.
#
# Copyright (C) 2016 by Jithin B.P. <jithinbp@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
import os,time

from . import commands_proto as CP
from . import packet_handler as packet_handler
from collections import OrderedDict

from .achan import *
import serial,string,inspect
import time
import sys
import numpy as np
from . import eyemath17

def open(**kwargs):
    '''
    If hardware is found, returns an instance of 'Interface', else returns None.
    '''
    obj = Interface(**kwargs)
    if obj.H.fd != None:
        return obj
    else:
        print('Device opening Error')
        return None
        #raise RuntimeError('Could Not Connect')
    

class Interface():
	"""
	**Communications library.**

	This class contains methods that can be used to interact with ExpEYES-17

	Initialization does the following

	* connects to tty device
	* loads calibration values.

	.. tabularcolumns:: |p{3cm}|p{11cm}|

	+----------+-----------------------------------------------------------------+
	|Arguments |Description                                                      |
	+==========+=================================================================+
	|timeout   | serial port read timeout. default = 1s                          |
	+----------+-----------------------------------------------------------------+

	>>> import expeyes.eyes17
	>>> I = expeyes.eyes17.open()
	>>> self.__print__(I)
	<eyes17.Interface instance at 0xb6c0cac>

	Once you have instantiated this class,  its various methods will allow access to all the features built
	into the device.
	"""

	CAP_AND_PCS=0
	ADC_SHIFTS_LOCATION1=1
	ADC_SHIFTS_LOCATION2=2
	ADC_POLYNOMIALS_LOCATION=3

	BAUD = 500000
	W1Type = 'sine'
	def __init__(self,timeout=1.0,**kwargs):
		self.verbose=kwargs.get('verbose',False)
		self.initialArgs = kwargs
		self.generic_name = 'ExpEYES17'
		self.timebase = 40
		self.MAX_SAMPLES = CP.MAX_SAMPLES
		self.samples=self.MAX_SAMPLES
		self.triggerLevel=550
		self.triggerChannel = 0
		self.error_count=0
		self.channels_in_buffer=0
		self.digital_channels_in_buffer=0
		self.currents=[0.55e-3,0.55e-6,0.55e-5,0.55e-4]
		self.currentScalers=[1.0,1.0,1.0,1.0]

		'''
		PGA settings
		0 - 16.5/1x [16V]; 1 - 16.5/2x [8V]; 2 - 16.5/4x [4V]; 3 - 16.5/5x [3.3V]; 4 - 16.5/8x [2.04V]; 5 - 16.5/10x [1.6V]; 6 - 16.5/16x [1V]; 7 - 16.5/32x [.5V]
		Since devices may have offsets up to 150mV , the ideal voltage ranges won't work.
		So, if a user selects 0.5V range , a 1V range will be more appropriate to prevent unexpected out-of-range situations
		'''
		self.analogRanges = OrderedDict([(16,0),		(8,1),		(4,2),		(2.5,3),		(1.5,4),		(1,5),		(.5,6),		(.25,7)		])
		
		self.data_splitting = kwargs.get('data_splitting',CP.DATA_SPLITTING)
		self.allAnalogChannels=allAnalogChannels
		self.analogInputSources={}
		for a in allAnalogChannels:self.analogInputSources[a]=analogInputSource(a)

		self.sinefreq = None;self.WaveType = 'none';self.WaveMode = 'sine'
		self.sqrfreq = None
		self.currentSourceValue = 1.1e-3
		self.aboutArray=[]
		self.errmsg = ''
		self.version = 'not connected'

		#--------------------------Initialize communication handler, and subclasses-----------------
		self.timestamp = None
		self.H = packet_handler.Handler(**kwargs)
		self.version_number = 1.0
		try:
			#self.H = packet_handler.Handler(**kwargs)
			self.version = self.H.version_string
			try:self.version_number = float(self.version[-3:])
			except:pass
			status = self.H.status 
			self.__print__(self.version,len(self.version))
		except Exception as ex:
			self.errmsg = "failed to Connect. Please check connections/arguments\n"
			self.connected = False
			print(self.errmsg)#raise RuntimeError(msg)
		
		try:
			self.__runInitSequence__(**kwargs)

		except Exception as ex:
			self.errmsg = "failed to run init sequence. Check device connections\n"+str(ex)
			self.connected = False
			print(self.errmsg)#raise RuntimeError(msg)

	def __runInitSequence__(self,**kwargs):
		self.aboutArray=[]
		from .Peripherals import I2C,PWMDAC
		self.connected = self.H.connected
		if not self.H.connected:
			self.__print__('Check hardware connections. Not connected')

		self.streaming=False
		self.achans=[analogAcquisitionChannel(a) for a in bipolars]        
		self.gain_values=gains
		self.buff=np.zeros(10000)
		self.SOCKET_CAPACITANCE = 0 
		self.resistanceScaling  = 1.
		self.CAP_RC_SCALING  = 1.
		self.rtime = lambda t: t/64e6

		self.digital_inputs=['IN2','SQR1_READ','OD1_READ','SEN','SQR1','OD1','SQ2','SQ3']
		self.digital_outputs=['OD1','CCS','SQR1','SQR2']
		self.allDigitalChannels = self.digital_inputs
		self.gains = {}
		if self.version_number<=2.0 and self.connected:
			self.__write_data_address__(0x0E1C,4) #Enable pull down resistor on IN2 
		for a in gainPGAs:
			self.gains[a] = 0

		#This array of four instances of digital_channel is used to store data retrieved from the
		#logic analyzer section of the device.  It also contains methods to generate plottable data
		#from the original timestamp arrays.
		self.I2C = I2C(self.H)
		#self.I2C.pullSCLLow(5000)        
		self.hexid=''    
		if self.H.connected:
			for a in self.gains: self.set_gain(a,self.gains[a],True) #Force load gain
			self.load_equation('sine')
			self.hexid=hex(self.device_id())
		
		self.DAC = PWMDAC(self.H,3.3,0)
		self.calibrated = False
		#-------Check for calibration data if connected. And process them if found---------------
		if kwargs.get('load_calibration',True) and self.H.connected:
			import struct
			cap_and_pcs=self.read_bulk_flash(self.CAP_AND_PCS,5+8*4)  #READY+calibration_string
			try:
				if cap_and_pcs[:5]=='READY':
					self.__print__(cap_and_pcs,'...') 
					scalers = list(struct.unpack('8f',cap_and_pcs[5:])) # #socket cap , C0,C1,C2,C3,PCS,SEN
					self.SOCKET_CAPACITANCE = scalers[0]
					#self.DAC.CHANS['PCS'].load_calibration_twopoint(scalers[1],scalers[2]) #
					self.__calibrate_ctmu__(scalers[1:5])
					self.currentSourceValue *= scalers[5]   #CCS
					self.__print__( '\nCCS Value : ',self.currentSourceValue)
					self.aboutArray.append(['Current Source Value']+[scalers[5]])
					self.resistanceScaling = scalers[6]   #SEN
					self.CAP_RC_SCALING = scalers[7]   #cap via RC
					self.aboutArray.append(['Capacitance[sock,550uA,55uA,5.5uA,.55uA]']+scalers[1:5])
					self.aboutArray.append(['SEN']+[scalers[6]])
				else:
					self.__print__('Cap and PCS calibration invalid') 
					#self.displayDialog('Cap and PCS calibration invalid')
					self.SOCKET_CAPACITANCE = 41e-12  #approx 41pF
					self.resistanceScaling = 1.
					self.CAP_RC_SCALING = 1.
			except:
					self.__print__('Cap and PCS calibration invalid. Unable to parse') 
				

			#Load constants for ADC and DAC
			polynomials = self.read_bulk_flash(self.ADC_POLYNOMIALS_LOCATION,2048)
			polyDict={}
			if polynomials[:7]=='ExpEYES':
				intro = polynomials.partition("\n")[0]
				parts = intro.partition('``')
				if len(parts[1]):self.timestamp = parts[2]
				self.__print__('ADC calibration found: %s'%(self.timestamp))
				
				self.aboutArray.append(['Calibration Found'])
				self.aboutArray.append([])
				self.calibrated = True
				poly_sections = polynomials.split('STOP')  #The 2K array is split into sections containing data for ADC_INL fit, ADC_CHANNEL fit, DAC_CHANNEL fit, PCS, CAP ...

				adc_slopes_offsets	= poly_sections[0]
				dac_slope_intercept = poly_sections[1]

				for a in adc_slopes_offsets.split('>|')[1:]:
					name,cals = a.split('|<')
					self.__print__( '\n','>'*20,name,'<'*20)
					self.aboutArray.append([])
					self.aboutArray.append(['ADC Channel',name])
					self.aboutArray.append(['Gain','X^2','X','C'])
					polyDict[name]=[]
					for b in range(len(cals)//12):
						try:
							poly=struct.unpack('3f',cals[b*12:(b+1)*12])
						except:
							self.__print__(name, ' not calibrated')
						self.__print__( b,poly)
						self.aboutArray.append([b]+['%.3e'%v for v in poly])
						polyDict[name].append(poly)
				
				#Load calibration data (slopes and offsets) for ADC channels . X^2+X+C
				for a in self.analogInputSources:
					if a in polyDict:
						self.__print__ ('loading polynomials for ',a,polyDict[a])
						self.analogInputSources[a].loadPolynomials(polyDict[a])
						self.analogInputSources[a].calibrationReady=True
					self.analogInputSources[a].regenerateCalibration()
				
				#Load calibration data for DAC channels. X^2+X+C
				for a in dac_slope_intercept.split('>|')[1:]:
					NAME = a[:3]			#Name of the DAC channel . PV1, PV2 ...
					self.aboutArray.append([]);	self.aboutArray.append(['Calibrated :',NAME])
					try:
						fits = struct.unpack('3f',a[5:])
						self.__print__(NAME, ' calibrated' , fits)
					except:
						self.__print__(NAME, ' not calibrated' , a[5:], len(a[5:]),a)
						continue
					self.DAC.CHANS[NAME].load_calibration_polynomial(fits)

	def get_resistance(self):
		V = self.get_average_voltage('SEN')
		if V>3.295:return np.Inf
		I = (3.3-V)/5.1e3
		res = V/I
		return res*self.resistanceScaling

	def __ignoreCalibration__(self):
			print ('CALIBRATION DISABLED')
			for a in self.analogInputSources:
				self.analogInputSources[a].__ignoreCalibration__()
				self.analogInputSources[a].regenerateCalibration()

			for a in ['PV1','PV2']: self.DAC.__ignoreCalibration__(a)

	def __print__(self,*args):
		if self.verbose:
			for a in args:
				print(a, end="")
			print()

	def __del__(self):
		self.__print__('closing port')
		try:
			self.H.fd.close()
		except:
			pass

	def get_version(self):
		"""
		Returns the version string of the device
		format: LTS-......
		"""
		try:
			return self.H.get_version(self.H.fd)
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)


	#-------------------------------------------------------------------------------------------------------------------#

	#|================================================ANALOG SECTION====================================================|
	#|This section has commands related to analog measurement and control. These include the oscilloscope routines,     |
	#|voltmeters, ammeters, and Programmable voltage sources.                                                           |
	#-------------------------------------------------------------------------------------------------------------------#

	def reconnect(self,**kwargs):
		'''
		Attempts to reconnect to the device in case of a commmunication error or accidental disconnect.
		'''
		try:
			self.H.reconnect(**kwargs)
			self.__runInitSequence__(**kwargs)
		except Exception as ex:
			self.errmsg = str(ex)
			self.H.disconnect()
			print(self.errmsg)
			raise RuntimeError(self.errmsg)
		
	def capture1(self,ch,ns,tg,**kwargs):
		"""
		Blocking call that fetches an oscilloscope trace from the specified input channel
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  ============================================================================================
		**Arguments** 
		==============  ============================================================================================
		ch              Channel to select as input. ['A1'..'A3','SEN']
		ns              Number of samples to fetch. Maximum 10000
		tg              Timegap between samples in microseconds
		==============  ============================================================================================

		.. figure:: images/capture1.png
			:width: 11cm
			:align: center
			:alt: alternate text
			:figclass: align-center
			
			A sine wave captured and plotted.
		
		Example
		
		>>> from pylab import *
		>>> import expeyes.eyes17
		>>> I=expeyes.eyes17.open()
		>>> x,y = I.capture1('A1',3200,1)
		>>> plot(x,y)
		>>> show()
				
		
		:return: Arrays X(timestamps),Y(Corresponding Voltage values)
		
		"""

		try:
			self.capture_traces(1,ns,tg,ch,**kwargs)
			time.sleep(1e-6*self.samples*self.timebase+.01)
			#while not self.oscilloscope_progress()[0]:
			#	pass
			while 1:
				x = self.oscilloscope_progress()
				time.sleep(0.01)
				#self.__print__('trigger:%d , conversion done : %d'%(x[1],x[0]))
				#print('trigger:%d , conversion done : %d'%(x[1],x[0]))
				if x[0]:break
				
			self.__fetch_channel__(1)
			#self.__fetch_channel__(2)

		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

		x=self.achans[0].get_xaxis()
		y=self.achans[0].get_yaxis()
		return x*1e-3,y


	def capture_action(self,ch,ns,tg,*args,**kwargs):
		"""
		Blocking call that records and returns an oscilloscope trace from the specified input channel after executing another command
		such as SET_LOW,SET_HIGH,FIRE_PULSE etc
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  ============================================================================================================================
		**Arguments** 
		==============  ============================================================================================================================
		ch              Channel to select as input. ['CH1'..'CH3','SEN']
		ns              Number of samples to fetch. Maximum 10000
		tg              Timegap between samples in microseconds
		\*args          SET_LOW    : set OD1 low before capture
		                SET_HIGH   : set OD1 high before capture
		                FIRE_PULSE : make a high pulse on OD1 before capture.
		                Use keyword argument pulse_width = x,where x = width of the pulse in uS. default width =10uS
		                Use keyword argument pulse_type = 'high_true' or 'low_true' to decide type of pulse
		                x,y = I.capture_action('A1',2000,1,'FIRE_PULSE',interval = 250) #Output 250uS pulse on OD1 before starting acquisition
		                SET_STATE  : change Digital output immediately after capture starts.						
		                Use keyword arguments that will be forwarded to the set_state command
		                e.g. x,y = I.capture_action('A1',2000,1,'SET_STATE',CCS=True,OD1=False) #Start capture. Set CCS high, OD1 low
		==============  ============================================================================================================================

		:return: Arrays X(timestamps),Y(Corresponding Voltage values)
		
		"""
		return self.__capture_fullspeed__(ch,ns,tg,*args,**kwargs)

	def capture2(self,ns,tg,TraceOneRemap='A1',**kwargs):
		"""
		Blocking call that fetches oscilloscope traces from A1 , A2 ...
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  =======================================================================================================
		**Arguments** 
		==============  =======================================================================================================
		ns              Number of samples to fetch. Maximum 5000
		tg              Timegap between samples in microseconds
		TraceOneRemap   Choose the analog input for channel 1. It is connected to A1 by default. Channel 2 always reads CH2.
		==============  =======================================================================================================

		.. figure:: images/capture2.png
			:width: 11cm
			:align: center
			:alt: alternate text
			:figclass: align-center
			
			Two sine waves captured and plotted.
		
		"""
		try:
			self.capture_traces(2,ns,tg,TraceOneRemap,**kwargs)
			time.sleep(1e-6*self.samples*self.timebase+.01)
			while not self.oscilloscope_progress()[0]:
				pass
				
			self.__fetch_channel__(1)
			self.__fetch_channel__(2)

		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

		x=self.achans[0].get_xaxis()
		y=self.achans[0].get_yaxis()
		y2=self.achans[1].get_yaxis()
		#x,y2=self.fetch_trace(2)
		return x*1e-3,y,x*1e-3,y2

	def capture4(self,ns,tg,TraceOneRemap='A1',**kwargs):
		"""
		Blocking call that fetches oscilloscope traces from A1,A2,A3,MIC . 
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  ======================================================================================================
		**Arguments** 
		==============  ======================================================================================================
		ns              Number of samples to fetch. Maximum 2500
		tg              Timegap between samples in microseconds. Minimum 1.75uS
		TraceOneRemap   Analog input for channel 1. It is connected to A1 by default.Channel 2-4 always reads CH2-MIC
		==============  ======================================================================================================

		.. figure:: images/capture4.png
			:width: 11cm
			:align: center
			:alt: alternate text
			:figclass: align-center
			
			Four traces captured and plotted.

		Example

		>>> from pylab import *
		>>> I=eyes17.Interface()
		>>> x,y1,y2,y3,y4 = I.capture4(800,1.75)
		>>> plot(x,y1)              
		>>> plot(x,y2)              
		>>> plot(x,y3)              
		>>> plot(x,y4)              
		>>> show()              
		
		:return: Arrays X(timestamps),Y1(Voltage at A1),Y2(Voltage at A2),Y3(Voltage at A3),Y4(Voltage at MIC)
		
		"""
		try:
			self.capture_traces(4,ns,tg,TraceOneRemap,**kwargs)
			time.sleep(1e-6*self.samples*self.timebase+.01)
			while not self.oscilloscope_progress()[0]:
				pass
			x,y=self.fetch_trace(1)
			x,y2=self.fetch_trace(2)
			x,y3=self.fetch_trace(3)
			x,y4=self.fetch_trace(4)
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)
		
		return x*1e-3,y,x*1e-3,y2,x*1e-3,y3,x*1e-3,y4     

	def __capture_fullspeed_init__(self,chan,samples,tg,*args, **kwargs):
		tg = int(tg*8)/8.  # Round off the timescale to 1/8uS units
		if(tg<0.5):tg=int(0.5*8)/8.
		if(samples>self.MAX_SAMPLES):
			self.__print__('Sample limit exceeded. 10,000 max')
			samples = self.MAX_SAMPLES

		self.timebase = int(tg*8)/8.
		self.samples = samples
		CHOSA=self.analogInputSources[chan].CHOSA

			
		try:
			self.H.__sendByte__(CP.ADC)
			if 'SET_LOW' in args:
				self.H.__sendByte__(CP.SET_LO_CAPTURE)
				#print ('set low capture')
			elif 'SET_HIGH' in args:
				self.H.__sendByte__(CP.SET_HI_CAPTURE)
				#print ('set high capture')
			elif 'FIRE_PULSE' in args:
				self.H.__sendByte__(CP.PULSE_CAPTURE)
				#print ('pulse capture')
			else:
				self.H.__sendByte__(CP.CAPTURE_DMASPEED)
			self.H.__sendByte__(CHOSA|0x80)     #|0x80 for 12-bit
			self.H.__sendInt__(samples)         #total number of samples to record
			self.H.__sendInt__(int(tg*8))       #Timegap between samples.  8MHz timer clock
			if 'FIRE_PULSE' in args:
				pwd = int(kwargs.get('pulse_width',10)) #width in uS
				if pwd>0x7FFF:pwd=0x7FFF
				if kwargs.get('pulse_type','high_true')=='high_true':self.H.__sendInt__(0x8000|pwd)
				else:self.H.__sendInt__(pwd)
				time.sleep(pwd*1e-6)

			if 'SET_STATE' in args:
				self.set_state(**kwargs)
			self.H.__get_ack__()



		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def __capture_fullspeed__(self,chan,samples,tg,*args,**kwargs):
		"""
		Blocking call that fetches oscilloscope traces from a single oscilloscope channel at a maximum speed of 2MSPS
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		===============  ============================================================================================
		**Arguments** 
		===============  ============================================================================================
		chan             channel name 'A1' / 'A2' ... 'SEN'
		samples          Number of samples to fetch. Maximum 10000/(total specified channels)
		tg               Timegap between samples in microseconds. minimum 0.5uS
		\*args           specify if SQR1 must be toggled right before capturing.
		 'SET_LOW' 		 will set OD1 to 0V
		 'SET_HIGH'		 will set it to 5V.  
		 'FIRE_PULSE' 	 will output a fixed width pulse on OD1 for a given interval (keyword arg 'interval' 
						 must be specified or it will default to 1000uS) before acquiring data.
						 if no arguments are specified, a regular capture will be executed.
		\*\*kwargs		 
		   interval      units:uS . Necessary if 'FIRE_PULSE' argument was supplied. default 1000uS
		===============  ============================================================================================

		.. code-block:: python

			from pylab import *
			I=eyes17.open()
			x,y = I.__capture_fullspeed__('A1',2000,1)
			plot(x,y)               
			show()
		

		.. code-block:: python

			x,y = I.__capture_fullspeed__('A1',2000,1,'SET_LOW')
			plot(x,y)               
			show()

		.. code-block:: python

			x,y = I.__capture_fullspeed__('A1',2000,1,'FIRE_PULSE',interval = 250) #Output 250uS pulse on OD1 before starting acquisition
			plot(x,y)               
			show()

		:return: timestamp array ,voltage_value array

		"""
		self.__capture_fullspeed_init__(chan,samples,tg,*args,**kwargs)
		time.sleep(1e-6*self.samples*self.timebase+kwargs.get('interval',0)*1e-6+0.1)
		y =  self.__retrieveBufferData__(0,self.samples)

		return np.linspace(0,1e-3*self.timebase*(self.samples-1),self.samples),self.analogInputSources[chan].calPoly12(y) #time in mS

	def __capture_fullspeed_hr__(self,chan,samples,tg,*args,**kwargs):
		tg = int(tg*8)/8.  # Round off the timescale to 1/8uS units
		if(tg<1):tg=1.
		if(samples>self.MAX_SAMPLES):
			self.__print__('Sample limit exceeded. 10,000 max')
			samples = self.MAX_SAMPLES

		self.timebase = int(tg*8)/8.
		self.samples = samples
		CHOSA=self.analogInputSources[chan].CHOSA
		try:
			self.H.__sendByte__(CP.ADC)
			if 'SET_LOW' in args:
				self.H.__sendByte__(CP.SET_LO_CAPTURE)     
			elif 'SET_HIGH' in args:
				self.H.__sendByte__(CP.SET_HI_CAPTURE)     
			elif 'READ_CAP' in args:
				self.H.__sendByte__(CP.MULTIPOINT_CAPACITANCE)     
			else:
				self.H.__sendByte__(CP.CAPTURE_DMASPEED)       
			self.H.__sendByte__(CHOSA|0x80)
			self.H.__sendInt__(samples)         #total number of samples to record
			self.H.__sendInt__(int(tg*8))       #Timegap between samples.  8MHz timer clock
			self.H.__get_ack__()
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def capture1_hr(self,chan,samples,tg,*args):
		try:
			self.__capture_fullspeed_hr__(chan,samples,tg,*args)
			time.sleep(1e-6*self.samples*self.timebase+.01)
			y =  self.__retrieveBufferData__(0,self.samples)
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

		return np.linspace(0,1e-3*self.timebase*(self.samples-1),self.samples),self.analogInputSources[chan].calPoly12(y)

	def __retrieveBufferData__(self,chan,samples):
		'''
		
		''' 
		data=b''
		try:
			for i in range(int(samples/self.data_splitting)):
				self.H.__sendByte__(CP.ADC)
				self.H.__sendByte__(CP.GET_CAPTURE_CHANNEL)
				self.H.__sendByte__(chan)  #channel number . starts with A0 on PIC 0,1,2,3!
				self.H.__sendInt__(self.data_splitting)
				self.H.__sendInt__(i*self.data_splitting)
				data+= self.H.fd.read(int(self.data_splitting*2))        #reading int by int sometimes causes a communication error. this works better.
				self.H.__get_ack__()

			if samples%self.data_splitting:
				self.H.__sendByte__(CP.ADC)
				self.H.__sendByte__(CP.GET_CAPTURE_CHANNEL)
				self.H.__sendByte__(chan)  #channel number starts with A0 on PIC
				self.H.__sendInt__(samples%self.data_splitting)
				self.H.__sendInt__(samples-samples%self.data_splitting)
				data += self.H.fd.read(int(2*(samples%self.data_splitting)))         #reading int by int may cause packets to be dropped. this works better.
				self.H.__get_ack__()

		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)
		try:
			for a in range(int(samples)): self.buff[a] = CP.ShortInt.unpack(data[a*2:a*2+2])[0]
		except Exception as ex:
			msg = "Incorrect Number of Bytes Received\n"
			raise RuntimeError(msg)

		return self.buff[:int(samples)]

	def capture_traces(self,num,samples,tg,channel_one_input='A1',CH123SA=0,**kwargs):
		"""
		Instruct the ADC to start sampling. use fetch_trace to retrieve the data

		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		=================== ============================================================================================
		**Arguments** 
		=================== ============================================================================================
		num                 Channels to acquire. 1/2/4
		samples             Total points to store per channel. Maximum 3200 total.
		tg                  Timegap between two successive samples (in uSec)
		channel_one_input   map channel 1 to 'A1' ... 'CH9'
		\*\*kwargs        
		
		\*trigger           Whether or not to trigger the oscilloscope based on the voltage level set by :func:`configure_trigger`
		=================== ============================================================================================


		see :ref:`capture_video`

		.. _adc_example:

			.. figure:: images/transient.png
				:width: 11cm
				:align: center
				:alt: alternate text
				:figclass: align-center
			
				Transient response of an Inductor and Capacitor in series

			The following example demonstrates how to use this function to record active events.

				* Connect a capacitor and an Inductor in series.
				* Connect A1 to the spare leg of the inductor. Also Connect OD1 to this point
				* Connect A2 to the junction between the capacitor and the inductor
				* connect the spare leg of the capacitor to GND( ground )
				* set OD1 initially high using set_state(SQR1=1)

			::

				>>> I.set_state(OD1=1)  #Turn on OD1
				#Arbitrary delay to wait for stabilization
				>>> time.sleep(0.5)                
				#Start acquiring data (2 channels,800 samples, 2microsecond intervals)
				>>> I.capture_traces(2,800,2,trigger=False)
				#Turn off OD1. This must occur immediately after the previous line was executed.
				>>> I.set_state(OD1=0)
				#Minimum interval to wait for completion of data acquisition.
				#samples*timegap*(convert to Seconds)
				>>> time.sleep(800*2*1e-6)
				>>> x,A1=I.fetch_trace(1)
				>>> x,A2=I.fetch_trace(2)
				>>> plot(x,A1-A2) #Voltage across the inductor                
				>>> plot(x,A2)     ##Voltage across the capacitor      
				>>> show()              

			The following events take place when the above snippet runs

			#. The oscilloscope starts storing voltages present at A1 and A2 every 2 microseconds
			#. The output OD1 was enabled, and this causes the voltage between the L and C to approach OD1 voltage.
			   (It may or may not oscillate)
			#. The data from A1 and A2 was read into x,A1,A2
			#. Both traces were plotted in order to visualize the Transient response of series LC
		
		:return: nothing
		
		.. seealso::            
			:func:`fetch_trace` , :func:`oscilloscope_progress` , :func:`capture1` , :func:`capture2` , :func:`capture4`

		"""
			
		triggerornot=0x80 if kwargs.get('trigger',True) else 0
		self.timebase=tg
		self.timebase = int(self.timebase*8)/8.  # Round off the timescale to 1/8uS units
		if channel_one_input not in self.analogInputSources:raise RuntimeError('Invalid input %s, not in %s'%(channel_one_input,str(self.analogInputSources.keys() )))
		CHOSA = self.analogInputSources[channel_one_input].CHOSA

		if self.version_number<=2.0 and (num==3 or num==4):  #Firmware bug in versions <= 2.0 for capture_four
			cmds = '\02\04%c\02\00\16\00'%(CHOSA)
			self.H.fd.write(cmds.encode())
			self.H.fd.read(1)

		try:
			self.H.__sendByte__(CP.ADC)
			if(num==1):
				if(self.timebase<1.5):self.timebase=int(1.5*8)/8.
				if(samples>self.MAX_SAMPLES):samples=self.MAX_SAMPLES

				self.achans[0].set_params(channel=channel_one_input,length=samples,timebase=self.timebase,resolution=10,source=self.analogInputSources[channel_one_input])
				self.H.__sendByte__(CP.CAPTURE_ONE)        #read 1 channel
				self.H.__sendByte__(CHOSA|triggerornot)     #channel number

			elif(num==2):
				if(self.timebase<1.75):self.timebase=int(1.75*8)/8.
				if(samples>self.MAX_SAMPLES/2):samples=self.MAX_SAMPLES/2

				self.achans[0].set_params(channel=channel_one_input,length=samples,timebase=self.timebase,resolution=10,source=self.analogInputSources[channel_one_input])
				self.achans[1].set_params(channel='A2',length=samples,timebase=self.timebase,resolution=10,source=self.analogInputSources['A2'])
				
				self.H.__sendByte__(CP.CAPTURE_TWO)            #capture 2 channels
				self.H.__sendByte__(CHOSA|triggerornot)             #channel 0 number

			elif(num==3 or num==4):
				if(self.timebase<1.75):self.timebase=int(1.75*8)/8.
				if(samples>self.MAX_SAMPLES/4):samples=self.MAX_SAMPLES/4

				self.achans[0].set_params(channel=channel_one_input,length=samples,timebase=self.timebase,\
				resolution=10,source=self.analogInputSources[channel_one_input])

				for a in range(1,4):
					chans=['NONE','A2','A3','MIC']
					self.achans[a].set_params(channel=chans[a],length=samples,timebase=self.timebase,\
					resolution=10,source=self.analogInputSources[chans[a]])
				
				self.H.__sendByte__(CP.CAPTURE_FOUR)           #read 4 channels
				self.H.__sendByte__(CHOSA|triggerornot)        #channel number


			self.samples=samples
			self.H.__sendInt__(samples)         #number of samples per channel to record
			self.H.__sendInt__(int(self.timebase*8))        #Timegap between samples.  8MHz timer clock
			self.H.__get_ack__()
			self.channels_in_buffer=num
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def capture_highres_traces(self,channel,samples,tg,**kwargs):
		"""
		Instruct the ADC to start sampling. use fetch_trace to retrieve the data

		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		=================== ============================================================================================
		**Arguments** 
		=================== ============================================================================================
		channel             channel to acquire data from 'A1' ... 'CH9'
		samples             Total points to store per channel. Maximum 3200 total.
		tg                  Timegap between two successive samples (in uSec)
		\*\*kwargs        
		
		\*trigger           Whether or not to trigger the oscilloscope based on the voltage level set by :func:`configure_trigger`
		=================== ============================================================================================

		
		:return: nothing
		
		.. seealso::
			
			:func:`fetch_trace` , :func:`oscilloscope_progress` , :func:`capture1` , :func:`capture2` , :func:`capture4`

		"""
		triggerornot=0x80 if kwargs.get('trigger',True) else 0
		self.timebase=tg
		try:
			self.H.__sendByte__(CP.ADC)
			CHOSA = self.analogInputSources[channel].CHOSA
			if(self.timebase<3):self.timebase=3
			if(samples>self.MAX_SAMPLES):samples=self.MAX_SAMPLES
			self.achans[0].set_params(channel=channel,length=samples,timebase=self.timebase,resolution=12,source=self.analogInputSources[channel])

			self.H.__sendByte__(CP.CAPTURE_12BIT)          #read 1 channel
			self.H.__sendByte__(CHOSA|triggerornot)     #channel number

			self.samples=samples
			self.H.__sendInt__(samples)         #number of samples to read
			self.H.__sendInt__(int(self.timebase*8))        #Timegap between samples.  8MHz timer clock
			self.H.__get_ack__()
			self.channels_in_buffer=1
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def capture_hr_multiple(self,samples,tg,*args):
		"""
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		=================== ============================================================================================
		**Arguments** 
		=================== ============================================================================================
		samples             Total points to store per channel. Maximum 10K total.
		tg                  Timegap between two successive samples (in uSec)
		\*\*args            channel names . 'A1','A2' ...'AN8'		
		=================== ============================================================================================

		
		:return: x1,y1,x2,y2... (where x1 is the time axis for the first channel, and y1 is its voltage , and so on...
		

		"""
		if len(args)==0:
			self.__print__('please specify channels to record')
			return
		tg = int(tg*8)/8.  # Round off the timescale to 1/8uS units
		if(tg<1.5):tg=int(1.5*8)/8.
		self.timebase=tg
		total_chans = len(args)

		total_samples = samples*total_chans
		if(total_samples>self.MAX_SAMPLES):
			self.__print__('Sample limit exceeded. 10,000 total')
			total_samples = self.MAX_SAMPLES
			samples = self.MAX_SAMPLES/total_chans
		self.samples=samples
		CHANNEL_SELECTION=0
		results = {}
		for chan in args:
			C=self.analogInputSources[chan].CHOSA
			CHANNEL_SELECTION|=(1<<C)
			results[C] = chan #make a CHOSA -> channel_name mapping.
		try:
			self.H.__sendByte__(CP.ADC)
			self.H.__sendByte__(CP.CAPTURE_12BIT_SCAN)  #read multiple channels sequentially
			self.H.__sendByte__(total_chans-1)  #channels to read . max 4
			self.H.__sendInt__(CHANNEL_SELECTION|((total_chans-1)<<12) )
			self.H.__sendInt__(samples)        		#number of samples to read
			self.H.__sendInt__(int(self.timebase*8))        #Timegap between samples.  8MHz timer clock
			self.H.__get_ack__()
			time.sleep(1e-6*total_samples*self.timebase*len(args)+.01)


			num = 0
			data = {}
			for C in np.sort(results.keys()):
				name = results[C]
				data[name] = [np.linspace(0,self.timebase*(self.samples-1),self.samples),self.analogInputSources[name].calPoly12(self.__retrieveBufferData__(num,self.samples))]
				num+=1
			for name in args:
				yield data[name][0]
				yield data[name][1]

		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def fetch_trace(self,channel_number):
		"""
		fetches a channel(1-4) captured by :func:`capture_traces` called prior to this, and returns xaxis,yaxis

		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  ============================================================================================
		**Arguments** 
		==============  ============================================================================================
		channel_number  Any of the maximum of four channels that the oscilloscope captured. 1/2/3/4
		==============  ============================================================================================

		:return: time array,voltage array

		.. seealso::
			
			:func:`capture_traces` , :func:`oscilloscope_progress`

		"""
		self.__fetch_channel__(channel_number)
		return self.achans[channel_number-1].get_xaxis(),self.achans[channel_number-1].get_yaxis()
		
	def oscilloscope_progress(self):
		"""
		returns the number of samples acquired by the capture routines, and the conversion_done status
		
		:return: conversion done(bool) , waiting_for_trigger(bool), samples acquired (number)

		>>> I.start_capture(1,3200,2)
		>>> self.__print__(I.oscilloscope_progress())
		(0,46)
		>>> time.sleep(3200*2e-6)
		>>> self.__print__(I.oscilloscope_progress())
		(1,3200)
		
		.. seealso::
			
			:func:`fetch_trace` , :func:`capture_traces`

		"""
		conversion_done=0
		samples=0
		try:
			self.H.__sendByte__(CP.ADC)
			self.H.__sendByte__(CP.GET_CAPTURE_STATUS)
			conversion_done = self.H.__getByte__()
			samples = self.H.__getInt__()
			self.H.__get_ack__()
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)
		return conversion_done&1,(conversion_done>>1)&1,samples

	def __fetch_channel__(self,channel_number):
		"""
		Fetches a section of data from any channel and stores it in the relevant instance of achan()
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  ============================================================================================
		**Arguments** 
		==============  ============================================================================================
		channel_number  channel number (1,2,3,4)
		==============  ============================================================================================
		
		:return: True if successful
		"""
		samples = self.achans[channel_number-1].length
		if(channel_number>self.channels_in_buffer):
			self.__print__('Channel unavailable')
			return False
		data=b''
		try:
			for i in range(int(samples/self.data_splitting)):
				self.H.__sendByte__(CP.ADC)
				self.H.__sendByte__(CP.GET_CAPTURE_CHANNEL)
				self.H.__sendByte__(channel_number-1)   #starts with A0 on PIC
				self.H.__sendInt__(self.data_splitting)
				self.H.__sendInt__(i*self.data_splitting)
				data+= self.H.fd.read(int(self.data_splitting*2))        #reading int by int sometimes causes a communication error. 
				self.H.__get_ack__()

			if samples%self.data_splitting:
				self.H.__sendByte__(CP.ADC)
				self.H.__sendByte__(CP.GET_CAPTURE_CHANNEL)
				self.H.__sendByte__(channel_number-1)   #starts with A0 on PIC
				self.H.__sendInt__(samples%self.data_splitting)
				self.H.__sendInt__(samples-samples%self.data_splitting)
				data += self.H.fd.read(int(2*(samples%self.data_splitting)))         #reading int by int may cause packets to be dropped.
				self.H.__get_ack__()
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

		try:
			for a in range(int(samples)): self.buff[a] = CP.ShortInt.unpack(data[a*2:a*2+2])[0]
			self.achans[channel_number-1].yaxis = self.achans[channel_number-1].fix_value(self.buff[:int(samples)])
		except Exception as ex:
			msg = "Incorrect Number of bytes received.\n"
			raise RuntimeError(msg)

		return True

	def __fetch_channel_oneshot__(self,channel_number):
		"""
		Fetches all data from given channel and stores it in the relevant instance of achan()
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  ============================================================================================
		**Arguments** 
		==============  ============================================================================================
		channel_number  channel number (1,2,3,4)
		==============  ============================================================================================
		
		"""
		offset=0 
		samples = self.achans[channel_number-1].length
		if(channel_number>self.channels_in_buffer):
			self.__print__('Channel unavailable')
			return False
		try:
			self.H.__sendByte__(CP.ADC)
			self.H.__sendByte__(CP.GET_CAPTURE_CHANNEL)
			self.H.__sendByte__(channel_number-1)   #starts with A0 on PIC
			self.H.__sendInt__(samples)
			self.H.__sendInt__(offset)
			data = self.H.fd.read(int(samples*2))        #reading int by int sometimes causes a communication error. this works better.
			self.H.__get_ack__()
			for a in range(int(samples)): self.buff[a] = CP.ShortInt.unpack(data[a*2:a*2+2])[0]
			self.achans[channel_number-1].yaxis = self.achans[channel_number-1].fix_value(self.buff[:int(samples)])
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

		return True
		
	def configure_trigger(self,chan,name,voltage,resolution=10,**kwargs):
		"""
		configure trigger parameters for 10-bit capture commands
		The capture routines will wait till a rising edge of the input signal crosses the specified level.
		The trigger will timeout within 8mS, and capture routines will start regardless.
		
		These settings will not be used if the trigger option in the capture routines are set to False
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  =====================================================================================================================
		**Arguments** 
		==============  =====================================================================================================================
		chan            channel . 0,1,2,3. corresponding to the channels being recorded by the capture routine(not the analog inputs)
		name            the name of the channel. 'A1'... 'V+'
		voltage         The voltage level that should trigger the capture sequence(in Volts)
		==============  =====================================================================================================================

		**Example**
		
		>>> I.configure_trigger(0,'A1',1.1)
		>>> I.capture_traces(4,800,2)
		#Unless a timeout occured, the first point of this channel will be close to 1.1Volts
		>>> I.fetch_trace(1)
		#This channel was acquired simultaneously with channel 1, 
		#so it's triggered along with the first
		>>> I.fetch_trace(2)
		
		.. seealso::
			
			:func:`capture_traces` , adc_example_

		"""
		prescaler = kwargs.get('prescaler',0)
		try:
			self.H.__sendByte__(CP.ADC)
			self.H.__sendByte__(CP.CONFIGURE_TRIGGER)
			self.H.__sendByte__((prescaler<<4)|(1<<chan))    #Trigger channel (4lsb) , trigger timeout prescaler (4msb)
			
			if resolution==12:
				level = self.analogInputSources[name].voltToCode12(voltage)
				level = np.clip(level,0,4095)
			else:
				level = self.analogInputSources[name].voltToCode10(voltage)
				#print('trigger level',level,voltage,self.analogInputSources[name].gain)
				level = np.clip(level,0,1023)

			if level>(2**resolution - 1):level=(2**resolution - 1)
			elif level<0:level=0

			self.H.__sendInt__(int(level))  #Trigger
			self.H.__get_ack__()
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def set_gain(self,channel,gain,Force=False):
		"""
		set the gain of the selected PGA
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  ============================================================================================
		**Arguments** 
		==============  ============================================================================================
		channel         'A1','A2'
		gain            (0-8) -> (1x,2x,4x,5x,8x,10x,16x,32x,1/11x)
		Force			If True, the amplifier gain will be set even if it was previously set to the same value.
		==============  ============================================================================================
		
		.. note::
			The gain value applied to a channel will result in better resolution for small amplitude signals.
			
			However, values read using functions like :func:`get_average_voltage` or    :func:`capture_traces` 
			will not be 2x, or 4x times the input signal. These are calibrated to return accurate values of the original input signal.
			
			in case the gain specified is 8 (1/11x) , an external 10MOhm resistor must be connected in series with the device. The input range will
			be +/-160 Volts
		
		>>> I.set_gain('A1',7)  #gain set to 32x on A1

		"""
		if gain<0 or gain>8:
			print('Invalid gain parameter. 0-7 only.')
			return
		if self.analogInputSources[channel].gainPGA==None:
			self.__print__('No amplifier exists on this channel :',channel)
			return False
		
		refresh = False
		if	self.gains[channel] != gain:
			self.gains[channel] = gain
			time.sleep(0.01)
			refresh = True
		if refresh or Force:
			try:
				self.analogInputSources[channel].__setGain__(gain)
				if gain>7: gain = 0   # external attenuator mode. set gain 1x
				self.H.__sendByte__(CP.ADC)
				self.H.__sendByte__(CP.SET_PGA_GAIN)
				self.H.__sendByte__(self.analogInputSources[channel].gainPGA) #send the channel. SPI, not multiplexer
				self.H.__sendByte__(gain) #send the gain
				self.H.__get_ack__()
				return self.gain_values[gain]
			except Exception as ex:
				self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

		return refresh

	def select_range(self,channel,voltage_range):
		"""
		set the gain of the selected PGA
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  ============================================================================================
		**Arguments** 
		==============  ============================================================================================
		channel         'A1','A2'
		voltage_range   choose from analogRanges.keys() [16,8,4,2.5,1.5,1,.5,.25]
		==============  ============================================================================================
		
		.. note::
			Setting the right voltage range will result in better resolution.			
			in case the range specified is 160 , an external 10MOhm resistor must be connected in series with the device. 
			
			Note : this function internally calls set_gain with the appropriate gain value
		
		>>> I.select_range('A1',8)  #gain set to 2x on A1. Voltage range +/-8V

		"""
		
		if voltage_range in self.analogRanges:
			g = self.analogRanges.get(voltage_range)
			return self.set_gain( channel, g)
		else:
			print ('not a valid range. try : ',self.analogRanges.keys())
			return None

	def __calcCHOSA__(self,name):
		name=name.upper()
		source = self.analogInputSources[name]

		if name not in self.allAnalogChannels:
			self.__print__('not a valid channel name. selecting A1')
			return self.__calcCHOSA__('A1')

		return source.CHOSA

	def get_voltage(self,channel_name,**kwargs):
		'''
		Reads voltage from specified channel , and returns the value.
		Autorange is enabled for this function, and it automatically selects the appropriate voltage range is either A1, or A2 are specified

		:return: V
		'''
		source = self.analogInputSources[channel_name]
		if source.gainEnabled: last_gain = source.gain
		self.voltmeter_autorange(channel_name)
		val = self.get_average_voltage(channel_name,**kwargs)
		if source.gainEnabled:self.set_gain(channel_name,last_gain)
		return val

	def get_voltage_time(self,channel_name,**kwargs):
		'''
		Reads voltage from specified channel , and returns the timestamp and measured value.

		:return: T,V
		'''
		source = self.analogInputSources[channel_name]
		if source.gainEnabled: last_gain = source.gain
		self.voltmeter_autorange(channel_name)
		val = self.get_average_voltage(channel_name,**kwargs)
		T = time.time()
		if source.gainEnabled:self.set_gain(channel_name,last_gain)
		return T,val

	def voltmeter_autorange(self,channel_name):
		if not self.analogInputSources[channel_name].gainEnabled:return None
		self.set_gain(channel_name,0)
		V = self.get_average_voltage(channel_name)
		return self.__autoSelectRange__(channel_name,V)

	def __autoSelectRange__(self,channel_name,V):
		keys =[16,7,3.5,2.8,1.6,1.1,.7,.3,0]
		cutoffs = {7:0,3.5:1,2.8:2,1.6:3,1.1:4,.7:5,.3:6,0:7}
		
		#keys = [8,4,3,1.8,1.2,.8,.3,0]
		#cutoffs = {8:0,4:1,3:2,1.8:3,1.2:4,.8:5,.3:6,0:7}
		g=0
		for a in keys:
			if abs(V)>a:
				g=cutoffs[a]
				break
		self.set_gain(channel_name,g)
		return g

	def __autoRangeScope__(self,tg):
		x,y1,y2 = self.capture2(1000,tg)
		self.__autoSelectRange__('A1',max(abs(y1)))
		self.__autoSelectRange__('A2',max(abs(y2)))


	def get_average_voltage(self,channel_name,**kwargs):
		""" 
		Return the voltage on the selected channel
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		+------------+-----------------------------------------------------------------------------------------+
		|Arguments   |Description                                                                              |
		+============+=========================================================================================+
		|channel_name| 'A1','A2','A3', 'MIC','IN1','SEN','V+'                                               |
		+------------+-----------------------------------------------------------------------------------------+
		|sleep       | read voltage in CPU sleep mode. not particularly useful. Also, Buggy.                   |
		+------------+-----------------------------------------------------------------------------------------+
		|\*\*kwargs  | Samples to average can be specified. eg. samples=100 will average a hundred readings    |
		+------------+-----------------------------------------------------------------------------------------+


		see :ref:`stream_video`

		Example:
		
		>>> self.__print__(I.get_average_voltage('CH4'))
		1.002
		
		"""
		try:
			source = self.analogInputSources[channel_name] #self.analogInputSources['A1'].polynomials[7](RAW)
		except Exception as ex:
			msg = "Invalid Channel"+str(ex)
			raise RuntimeError(msg)


		vals = [self.__get_raw_average_voltage__(channel_name,**kwargs) for a in range(int(kwargs.get('samples',1)))]
		val = np.average([source.calPoly12(a) for a in vals])
		rawval = np.average(vals)
		#print('get_average_voltage',rawval,val,source.gain,self.analogInputSources['A1'].polynomials[7](4095))
		if source.gainEnabled:
			if source.__conservativeInRangeRaw__(rawval,10):
				return  val
			else:
				print('Out of Range ',val,'Gain:',source.gainEnabled)
				return val#np.NaN
		else:
			return  val

	def __get_raw_average_voltage__(self,channel_name,**kwargs):
		""" 
		Return the average of 16 raw 12-bit ADC values of the voltage on the selected channel
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  ============================================================================================================
		**Arguments** 
		==============  ============================================================================================================
		channel_name    'A1', 'A2', 'A3', 'MIC', '5V', 'IN1','SEN'
		sleep           read voltage in CPU sleep mode
		==============  ============================================================================================================

		"""
		try:
			chosa = self.__calcCHOSA__(channel_name)
			self.H.__sendByte__(CP.ADC)
			self.H.__sendByte__(CP.GET_VOLTAGE_SUMMED)
			self.H.__sendByte__(chosa) 
			V_sum = self.H.__getInt__()
			self.H.__get_ack__()
			return  V_sum/16. #sum(V)/16.0  #
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def fetch_buffer(self,starting_position=0,total_points=100):
		"""
		fetches a section of the ADC hardware buffer
		"""
		try:
			self.H.__sendByte__(CP.COMMON)
			self.H.__sendByte__(CP.RETRIEVE_BUFFER)
			self.H.__sendInt__(starting_position)
			self.H.__sendInt__(total_points)
			for a in range(int(total_points)): self.buff[a]=self.H.__getInt__()
			self.H.__get_ack__()
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def clear_buffer(self,starting_position,total_points):
		"""
		clears a section of the ADC hardware buffer
		"""
		try:
			self.H.__sendByte__(CP.COMMON)
			self.H.__sendByte__(CP.CLEAR_BUFFER)
			self.H.__sendInt__(starting_position)
			self.H.__sendInt__(total_points)
			self.H.__get_ack__()
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def fill_buffer(self,starting_position,point_array):
		"""
		fill a section of the ADC hardware buffer with data
		"""
		try:
			self.H.__sendByte__(CP.COMMON)
			self.H.__sendByte__(CP.FILL_BUFFER)
			self.H.__sendInt__(starting_position)
			self.H.__sendInt__(len(point_array))
			for a in point_array:
				self.H.__sendInt__(int(a))
			self.H.__get_ack__()
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)


	#-------------------------------------------------------------------------------------------------------------------#

	#|===============================================DIGITAL SECTION====================================================|   
	#|This section has commands related to digital measurement and control. These include the Logic Analyzer, frequency |
	#|measurement calls, timing routines, digital outputs etc                               |
	#-------------------------------------------------------------------------------------------------------------------#
	
	def __calcDChan__(self,name):
		"""
		accepts a string represention of a digital input ['ID1','ID2','ID3','ID4','SEN','EXT','CNTR']
		and returns a corresponding number
		"""
		
		if name in self.digital_inputs:
			return self.digital_inputs.index(name)
		else:
			self.__print__(' invalid channel',name,' , selecting ID1 instead ')
			return 0
		
	def get_high_freq(self,pin):
		""" 
		retrieves the frequency of the signal connected to ID1. for frequencies > 1MHz
		also good for lower frequencies, but avoid using it since
		the oscilloscope cannot be used simultaneously due to hardware limitations.
		
		The input frequency is fed to a 32 bit counter for a period of 100mS.
		The value of the counter at the end of 100mS is used to calculate the frequency.
		
		.. seealso:: :func:`get_freq`
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		pin             The input pin to measure frequency from : ['ID1','ID2','ID3','ID4','SEN','EXT','CNTR']
		==============  ============================================================================================

		:return: frequency
		"""
		try:
			self.H.__sendByte__(CP.COMMON)
			self.H.__sendByte__(CP.GET_HIGH_FREQUENCY)
			self.H.__sendByte__(self.__calcDChan__(pin))
			val = self.H.__getLong__()
			if val:val+=1
			self.H.__get_ack__()
			return (val)/1.0e-1 #100mS sampling
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def get_freq(self,channel='CNTR',timeout=1.):
		"""
		Frequency measurement on IDx.
		Measures time taken for 4 rising edges of input signal.
		returns the frequency in Hertz

		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  ============================================================================================
		**Arguments** 
		==============  ============================================================================================
		channel         The input to measure frequency from. ['ID1','ID2','ID3','ID4','SEN','EXT','CNTR']
		timeout         This is a blocking call which will wait for one full wavelength before returning the
						calculated frequency.
						Use the timeout option if you're unsure of the input signal.
						returns 0 if timed out
		==============  ============================================================================================

		:return float: frequency
		
		
		.. _timing_example:
		
			* connect SQR1 to ID1
			
			>>> I.set_sqr1(4000,25)
			>>> self.__print__(I.get_freq('ID1'))
   
		
		"""
		try:
			self.H.__sendByte__(CP.COMMON)
			self.H.__sendByte__(CP.GET_FREQUENCY)
			timeout_msb = int((timeout*64e6))>>16
			self.H.__sendInt__(timeout_msb)
			self.H.__sendByte__(self.__calcDChan__(channel))

			#t=time.time()
			self.H.waitForData(timeout)
			#print('waited',time.time()-t,timeout_msb)

			tmt = self.H.__getByte__()
			x=[self.H.__getLong__() for a in range(2)]
			self.H.__get_ack__()
			freq = lambda t: 4*64e6/t if(t) else 0 #four rising edges counted against a 64MHz clock
			#self.__print__(x,tmt,timeout_msb)
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)
		if(tmt):return 0
		return freq(x[1]-x[0])

	def MeasureInterval(self,channel1,channel2,edge1,edge2,timeout=0.1):
		""" 
		Measures time intervals between two logic level changes on any two digital inputs(both can be the same)

		For example, one can measure the time interval between the occurence of a rising edge on ID1, and a falling edge on ID3.
		If the returned time is negative, it simply means that the event corresponding to channel2 occurred first.
		
		returns the calculated time
		
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  ============================================================================================
		**Arguments** 
		==============  ============================================================================================
		channel1        The input pin to measure first logic level change
		channel2        The input pin to measure second logic level change
						 -['ID1','ID2','ID3','ID4','SEN','EXT','CNTR']
		edge1           The type of level change to detect in order to start the timer
							* 'rising'
							* 'falling'
							* 'four rising edges'
		edge2           The type of level change to detect in order to stop the timer
							* 'rising'
							* 'falling'
							* 'four rising edges'
		timeout         Use the timeout option if you're unsure of the input signal time period.
						returns -1 if timed out
		==============  ============================================================================================

		:return : time

		.. seealso:: timing_example_
		
		
		"""
		try:
			self.H.__sendByte__(CP.TIMING)
			self.H.__sendByte__(CP.INTERVAL_MEASUREMENTS)
			timeout_msb = int((timeout*64e6))>>16
			self.H.__sendInt__(timeout_msb)

			self.H.__sendByte__(self.__calcDChan__(channel1)|(self.__calcDChan__(channel2)<<4))

			params =0
			if edge1  == 'rising': params |= 3 
			elif edge1=='falling': params |= 2
			else:              params |= 4

			if edge2  == 'rising': params |= 3<<3 
			elif edge2=='falling': params |= 2<<3
			else:              params |= 4<<3

			self.H.__sendByte__(params)
			A=self.H.__getLong__()
			B=self.H.__getLong__()
			tmt = self.H.__getInt__()
			self.H.__get_ack__()
			#self.__print__(A,B)
			if(tmt >= timeout_msb or B==0):return np.NaN
			rtime = lambda t: t/64e6
			return rtime(B-A+20)
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)


	#DEPRECATE SOON . REPLACE WITH DoublePinEdges , or SinglePinEdges as applicable
	def MeasureMultipleDigitalEdges(self,channel1,channel2,edgeType1,edgeType2,points1,points2,timeout=0.1,**kwargs):
		""" 
		Measures a set of timestamped logic level changes(Type can be selected) from two different digital inputs.

		Example
			Aim : Calculate value of gravity using time of flight.
			The setup involves a small metal nut attached to an electromagnet powered via SQ1.
			When SQ1 is turned off, the set up is designed to make the nut fall through two
			different light barriers( [LED,photodetector] pairs that show a logic change when an object gets in the middle)
			placed at known distances from the initial position. 
			
			one can measure the timestamps for rising edges on ID1 ,and ID2 to determine the speed, and then obtain value of g
		
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  ============================================================================================
		**Arguments** 
		==============  ============================================================================================
		channel1        The input pin to measure first logic level change
		channel2        The input pin to measure second logic level change
						 -['ID1','ID2','ID3','ID4','SEN','EXT','CNTR']
		edgeType1       The type of level change that should be recorded
							* 'rising'
							* 'falling'
							* 'four rising edges' [default]
		edgeType2       The type of level change that should be recorded
							* 'rising'
							* 'falling'
							* 'four rising edges'
		points1			Number of data points to obtain for input 1 (Max 4)
		points2			Number of data points to obtain for input 2 (Max 4)
		timeout         Use the timeout option if you're unsure of the input signal time period.
						returns -1 if timed out
		**kwargs
		  SQ1			set the state of SQR1 output(LOW or HIGH) and then start the timer.  eg. SQR1='LOW'
		  zero			subtract the timestamp of the first point from all the others before returning. default:True
		==============  ============================================================================================

		:return : time

		.. seealso:: timing_example_
		
		
		"""
		try:
			self.H.__sendByte__(CP.TIMING)
			self.H.__sendByte__(CP.TIMING_MEASUREMENTS)
			timeout_msb = int((timeout*64e6))>>16
			#print ('timeout',timeout_msb)
			self.H.__sendInt__(timeout_msb)
			self.H.__sendByte__(self.__calcDChan__(channel1)|(self.__calcDChan__(channel2)<<4))
			params =0
			if edgeType1  == 'rising': params |= 3 
			elif edgeType1=='falling': params |= 2
			else:              params |= 4

			if edgeType2  == 'rising': params |= 3<<3 
			elif edgeType2=='falling': params |= 2<<3
			else:              params |= 4<<3

			if('SQR1' in kwargs):  # User wants to toggle SQ1 before starting the timer
				params|=(1<<6)
				if kwargs['SQR1']=='HIGH':params|=(1<<7)
			self.H.__sendByte__(params)
			if points1>4:points1=4
			if points2>4:points2=4
			self.H.__sendByte__(points1|(points2<<4))  #Number of points to fetch from either channel

			self.H.waitForData(timeout)
			A=np.array([self.H.__getLong__() for a in range(points1)])
			self.H.waitForData(timeout)
			B=np.array([self.H.__getLong__() for a in range(points2)])
			tmt = self.H.__getInt__()
			self.H.__get_ack__()
			#print(A,B)
			if(tmt >= timeout_msb ):return None,None
			rtime = lambda t: t/64e6
			if(kwargs.get('zero',True)):  # User wants set a reference timestamp
				return rtime(A-A[0]),rtime(B-A[0])
			else:
				return rtime(A),rtime(B)
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)


	def SinglePinEdges(self,channel,edgeType,points,timeout=1.0,**kwargs):
		""" 
		Measures a set of timestamped logic level changes(Type can be selected) from one digital input.

		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  ============================================================================================
		**Arguments** 
		==============  ============================================================================================
		channel        The input pin to measure first logic level change
						 -['ID1','ID2','ID3','ID4','SEN','EXT','CNTR']
		edgeType       The type of level change that should be recorded
							* 'rising'
							* 'falling'
							* '4xrising' [default]
							* '16xrising'
		points			Number of data points to obtain for input 1 (Max 4)
		timeout         Use the timeout option if you're unsure of the input signal time period.
						returns -1 if timed out
		==============  ============================================================================================

		:return : time array in uS units
		"""
		data=0
		if 'OD1' in kwargs:
			data|= 0x10|(1 if kwargs.get('OD1') else 0)
		if 'CCS' in kwargs:
			data|= 0x20|(2 if kwargs.get('CCS') else 0)
		if 'SQR1' in kwargs:
			data|= 0x40|(4 if kwargs.get('SQR1') else 0)
		if 'SQR2' in kwargs:
			data|= 0x80|(8 if kwargs.get('SQR2') else 0)

		try:
			self.H.__sendByte__(CP.TIMING)
			self.H.__sendByte__(CP.SINGLE_PIN_EDGES)
			timeout_msb = int((timeout*64e6))>>16
			if timeout_msb > 65535:timeout_msb = 65535
			self.H.__sendInt__(timeout_msb)
			self.H.__sendByte__(self.__calcDChan__(channel))
			ET = {'falling':2,'rising':3,'4xrising':4,'16xrising':5}
			params = ET.get(edgeType,0)
			self.H.__sendByte__(params)
			if points>4:points=4
			self.H.__sendByte__(points)  #Number of points to fetch from either channel
			self.H.__sendByte__(data)

			t = time.time()
			self.H.waitForData(timeout)
			A=np.array([self.H.__getLong__() for a in range(points)])
			tmt = self.H.__getInt__()
			self.H.__get_ack__()
			#print ('timeout : ',timeout, time.time()-t,tmt)
			if(tmt >= timeout_msb ):return None
			return self.rtime(A)
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def DoublePinEdges(self,channel1,channel2,edge1,edge2,points1,points2,timeout=1.0,**kwargs):
		""" 
		Measures a set of timestamped logic level changes(Type can be selected) from one digital input.

		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  ============================================================================================
		**Arguments** 
		==============  ============================================================================================
		channel1        First input pin to measure logic level
						 -['ID1','ID2','ID3','ID4','SEN','EXT','CNTR']
		channel2        Second input pin to measure logic level changes 
						 -['ID1','ID2','ID3','ID4','SEN','EXT','CNTR']
		edgeType1       The type of level change that should be recorded
		edgeType2			* 'rising'
							* 'falling'
							* '4xrising' [default]
							* '16xrising'
		points1			Number of data points to obtain for input 1 (Max 4)
		points2         Number of data points to obtain for input 2 (Max 4)
		timeout         Use the timeout option if you're unsure of the input signal time period.
						returns -1 if timed out
		\*\*kwargs		Timer for channel2 will only start once the edges for channel one have been recorded.
		                for example , if channel 1 was set to record 2x rising edges , the timer for channel 2
		                will start only after that is complete. However , any channel 2 events that occured while
		                channel 1 was running are recorded as 0 value.
		==============  ============================================================================================

		:return : time array in uS units
		"""
		try:
			channel1 = str(channel1);channel2 = str(channel2);edge1=str(edge1);edge2=str(edge2)
			#print(channel1,channel2,edge1,edge2,points1,points2,timeout,kwargs)
			self.H.__sendByte__(CP.TIMING)
			self.H.__sendByte__(CP.DOUBLE_PIN_EDGES)
			timeout_msb = int((timeout*64e6))>>16
			if timeout_msb > 65535:timeout_msb = 65535

			self.H.__sendInt__(timeout_msb)
			self.H.__sendByte__(self.__calcDChan__(channel1)|(self.__calcDChan__(channel2)<<4))
			ET = {'falling':2,'rising':3,'4xrising':4,'16xrising':5}
			params = ET.get(edge1,0)
			params |= (ET.get(edge2,0)<<4)
			self.H.__sendByte__(params)
			if points1>4:points1=4
			if points2>4:points2=4
			SEQ = 0x80#(0x80 if kwargs.get('sequential',False) else 0)
			self.H.__sendByte__(SEQ|points1|(points2<<4))  #Number of points to fetch from either channel |0x80 if sequential is True

			t=time.time()
			self.H.waitForData(timeout)
			A=np.array([self.H.__getLong__() for a in range(points1)])
			self.H.waitForData(timeout)
			B=np.array([self.H.__getLong__() for a in range(points2)])
			#print('waited dp',time.time()-t,timeout_msb,A)
			
			tmt = self.H.__getInt__()
			ack=self.H.__get_ack__()
			if(tmt >= timeout_msb ):
				self.__print__('timed out',tmt,timeout_msb,ack)
				return None,None
			rtime = lambda t: t/64e6
			if kwargs.get('sequential',False):
				for a in range(len(B)):
					if B[a]: B[a]+=4   #Compensation for four Nop delay
			else:
				for a in range(len(B)):
					B[a]+=9  #Compensation for four Nop delay + 5 cycles for if statement

			#print (A,B,tmt,timeout_msb)
			#print ('frq',1./np.diff(rtime(A)),1./np.diff(rtime(B)))
			return rtime(A),rtime(B)
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def get_states(self):
		"""
		gets the state of the digital inputs. returns dictionary with keys 'ID1','ID2','ID3','ID4'

		>>> self.__print__(get_states())
		{'ID1': True, 'ID2': True, 'ID3': True, 'ID4': False}
		
		"""
		try:
			if self.version[:6]=='SJ-2.0':
				self.__write_data_address__(0x0E1E,11) #set IN2 to digital mode

			self.H.__sendByte__(CP.DIN)
			self.H.__sendByte__(CP.GET_STATES)
			s=self.H.__getByte__()
			return {'IN2':(s&1!=0),'SQR1':(s&2!=0),'OD1':(s&4!=0),'SEN':(s&8!=0),'SQR1_OUT':(s&16!=0),'OD1_OUT':(s&32!=0),'CCS':(s&64==0)} #CCS is inverted
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def get_state(self,input_id):
		"""
		returns the logic level on the specified input (ID1,ID2,ID3, or ID4)

		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  ============================================================================================
		**Arguments**    Description
		==============  ============================================================================================
		input_id        the input channel
							'ID1' -> state of ID1
							'ID4' -> state of ID4
		==============  ============================================================================================

		>>> self.__print__(I.get_state(I.ID1))
		False
		
		"""
		return self.get_states()[input_id]

	def set_state(self,**kwargs):
		"""
		
		set the logic level on digital outputs OD1,CCS,SQR1

		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  ============================================================================================
		**Arguments** 
		==============  ============================================================================================
		\*\*kwargs      SQR1,SQR2,SQR3,SQR4
						states(0 or 1)
		==============  ============================================================================================

		>>> I.set_state(OD1=1,CCS=0)
		sets OD1 HIGH, Turn Off CCS, but leave SQR1 untouched.

		"""
		data=0
		if 'OD1' in kwargs:
			data|= 0x10|(1 if kwargs.get('OD1') else 0)
		if 'CCS' in kwargs:
			data|= 0x20|(2 if kwargs.get('CCS') else 0)
		if 'SQR1' in kwargs:
			data|= 0x40|(4 if kwargs.get('SQR1') else 0)
		if 'SQR2' in kwargs:
			data|= 0x80|(8 if kwargs.get('SQR2') else 0)
		try:
			#print (hex(data))
			self.H.__sendByte__(CP.DOUT)
			self.H.__sendByte__(CP.SET_STATE)
			self.H.__sendByte__(data)
			self.H.__get_ack__()
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

#---------- Time Interval Measurements from expEYES-jr ----------------------

	def tim_helper(self, cmd, src, dst,timeout = 2.5):
		'''
		Helper function for all Time measurement calls.
		
		cmd == 'multi_r2r':
		  src = input pin
		  dst = number of edges to detect. dst E {1,2,3,4,8,12,16,32,48}
		cmd in ['r2r','r2f','f2r','f2f']
		  Command, Source and destination pins are inputs.
		
		Returns time in microseconds, -1 on error.
		'''
		allowed_edges = [1,2,3,4,8,12,16,32,48]

		if cmd == 'multi_r2r':
			if src not in self.digital_inputs:
				print ('Pin should be digital input capable: 0,3,4,5,6 or 7')
				self.msg = ('Pin should be digital input capable: 0,3,4,5,6 or 7')
				return -1
			if dst not in allowed_edges:
				self.msg = ('edges allowed : %s'%allowed_edges)
				print ('edge count not in %s'%allowed_edges)
				return -1
			if dst in [1,2,3]:
				edge = 'rising'
				count = dst+1
			elif dst in [4,8,12]:
				edge = '4xrising'
				count = [4,8,12].index(dst)+2
			elif dst in [16,32,48]:
				edge = '16xrising'
				count = [16,32,48].index(dst)+2
			#print (edge,count)
			T = self.SinglePinEdges(src,edge,count,timeout) #src,src,rising edges , rising edges, total 2, total 2, 1 second timeout.
			#print ('multi_r2r',T)
			if T is not None:return T[count-1]-T[0]
			else:return -1

		
		elif cmd in ['r2r','r2f','f2r','f2f']:
			if src not in self.digital_inputs:
				print ('Pin should be digital input capable: 0,3,4,5,6 or 7')
				self.msg = ('Pin should be digital input capable: 0,3,4,5,6 or 7')
				return -1
			if dst not in self.digital_inputs:
				print ('Pin should be digital input capable: 0,3,4,5,6 or 7')
				self.msg = ('Pin should be digital input capable: 0,3,4,5,6 or 7')
				return -1
			edge1 = 'rising' if cmd in ['r2r','r2f'] else 'falling'
			edge2 = 'rising' if cmd in ['f2r','r2r'] else 'falling'
			T1,T2 = self.DoublePinEdges(src,dst,edge1,edge2,1,2,timeout,sequential=True) #src,src,rising edges , rising edges, total 2, total 2, 1 second timeout.
			#print (T1,T2)
			if T2 is not None:
				if T2[0]:return T2[0]
				else: return T2[1]
			else:return -1

		elif cmd in ['s2r','s2f','c2r','c2f']:
			if src not in self.digital_outputs:
				print ('Pin should be digital output capable: %s'%self.digital_outputs)
				self.msg = ('Pin should be digital output capable: %s'%self.digital_outputs)
				return -1
			if dst not in self.digital_inputs:
				print ('Pin should be digital input capable: %s'%self.digital_inputs)
				self.msg = ('Pin should be digital input capable: %s'%self.digital_inputs)
				return -1

			edge = 'rising' if cmd in ['s2r','c2r'] else 'falling'
			if cmd[0]=='s':   T = self.SinglePinEdges(dst,edge,1,timeout,src=1)
			elif cmd[0]=='c': T = self.SinglePinEdges(dst,edge,1,timeout,src=0)
			
			if T is not None:return T[0]
			else:return -1


#-------------------- Passive Time Interval Measurements ----------------------------------
	def duty_cycle(self, pin,timeout=2.0):
		'''
		Time between two rising edges. The pins must be distinct. For same pin, use multi_r2rtime
		'''
		T1,T2 = self.DoublePinEdges(pin,pin,'rising','falling',2,3,timeout,sequential=True)
		if T1 is not None and T2 is not None:
				if T2[1]:return 100*(T2[1])/(T1[1]-T1[0]) #T2[0] will always equal 0 because sequential mode is enabled, but one falling edge must occur between two rising edges.
				elif T2[2]:return 100*(T2[2])/(T1[1]-T1[0]) #T2[1] can be zero on rare occassions if input frequency is too high causing a falling edge to be recorded before the T2 timer is active
		else:
			return -1

	def r2rtime(self, pin1, pin2):
		'''
		Time between two rising edges. The pins must be distinct. For same pin, use multi_r2rtime
		'''
		return self.tim_helper('r2r', pin1, pin2)

	def f2ftime(self, pin1, pin2):
		'''
		Time between two falling edges. The pins must be distinct. 
		For same pin, use multi_r2rtime
		'''
		return self.tim_helper('f2f', pin1, pin2)

	def r2ftime(self, pin1, pin2):
		'''
		Time between a rising edge to a falling edge. 
		The pins could be same or distinct.
		'''
		return self.tim_helper('r2f', pin1, pin2)

	def f2rtime(self, pin1, pin2):
		'''
		Time between a falling edge to a rising edge. 
		The pins could be same or distinct.
		'''
		return self.tim_helper('f2r', pin1, pin2)

	def multi_r2rtime(self, pin, edges=1,timeout=1.0):
		'''
		Time between rising edges. You can specify the number of edges to count.
		(pin, 3) will give time required for 3 cycles of the input. Increases measurement resolution.
		valid edges = [1,2,3,4,8,12,16,32,48]
		'''
		return self.tim_helper('multi_r2r', pin, edges,timeout)

	def set2rtime(self, pin1, pin2):
		'''
		Time from setting pin1 to a rising edge on pin2.
		'''
		return self.tim_helper('s2r', pin1, pin2)

	def set2ftime(self, pin1, pin2):
		'''
		Time from setting pin1 to a falling edge on pin2.
		'''
		return self.tim_helper('s2f', pin1, pin2)

	def clr2rtime(self, pin1, pin2):
		'''
		Time from clearin pin1 to a rising edge on pin2.
		'''
		return self.tim_helper('c2r', pin1, pin2)

	def clr2ftime(self, pin1, pin2):
		'''
		Time from clearing pin1 to a falling edge on pin2.
		'''
		return self.tim_helper('c2f', pin1, pin2)


	def __charge_cap__(self,state,t):
		try:
			self.H.__sendByte__(CP.ADC)
			self.H.__sendByte__(CP.SET_CAP)
			self.H.__sendByte__(state)
			self.H.__sendInt__(t)
			self.H.__get_ack__()
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)
		
	def __capture_capacitance__(self,samples,tg):
		self.__charge_cap__(1,50000)
		x,y=self.capture1_hr('IN1',samples,tg,'READ_CAP')
		try:
			#yfit,fitres =  eyemath17.fit_exp(x*1e-3,y)
			fitres,yfit =  eyemath17.fit_exp2(x*1e-3,y)

			self.__print__ ('N:%d tg:%d fitres:%s'%(samples,tg,str(fitres) ))
			if fitres is not None:
				cVal = fitres
				#from pylab import *
				#plot(x,yfit)
				#show()
				return x,y,yfit,cVal
			else:
				return None
		except Exception as ex:
			raise RuntimeError(" Fit Failed "+ex.message)

	def capacitance_via_RC_discharge(self):
		cap = self.get_capacitor_range()[1]
		self.__print__('trying RC discharge curve fit. estimated cap: ',cap)
		T = 4*cap*10e3*1e6 #uS  #CV charge via 10K
		samples = 500
		try:
			if T>3000 and T<10e6:
				if T>50e3:samples=250
				if cap>10e-6: self.__charge_cap__(1,50000)   #Extra charging time if capacitance is high
				if cap>5e-6: self.__charge_cap__(1,50000)
				step_size = min(8000,int(T/samples))
				RC = self.__capture_capacitance__(samples,step_size)[3][1]
				return self.CAP_RC_SCALING*abs(RC)/10e3
			else:
				self.__print__('cap out of range %f %f'%(T,cap))
				return 0
		except Exception as e:
			self.__print__(e)
			return 0

	def __get_capacitor_range__(self,ctime):
		try:
			self.__charge_cap__(0,30000)
			self.H.__sendByte__(CP.COMMON)
			self.H.__sendByte__(CP.GET_CAP_RANGE)
			self.H.__sendInt__(ctime) 
			V_sum = self.H.__getInt__()
			self.H.__get_ack__()
			V=V_sum*3.3/16/4095
			C = -ctime*1e-6/1e4/np.log(1-V/3.3)
			return  V,C
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def get_capacitor_range(self):
		""" 
		Charges a capacitor connected to IN1 via a 20K resistor from a 3.3V source for a fixed interval
		Returns the capacitance calculated using the formula Vc = Vs(1-exp(-t/RC))
		This function allows an estimation of the parameters to be used with the :func:`get_capacitance` function.

		"""
		t=10
		P=[1.5,50e-12]
		for a in range(4):
			P=list(self.__get_capacitor_range__(50*(10**a)))
			if(P[0]>1.5):
				if a==0 and P[0]>3.28: #pico farads range. Values will be incorrect using this method
					P[1]=50e-12
				break
		return  P

	def get_capacitance(self):  #time in uS
		"""
		measures capacitance of component connected between CAP and ground

		
		:return: Capacitance (F)

		Constant Current Charging
		
		.. math::

			Q_{stored} = C*V
			
			I_{constant}*time = C*V
			
			C = I_{constant}*time/V_{measured}

		Also uses Constant Voltage Charging via 10K resistor if required.

		"""
		GOOD_VOLTS=[2.5,2.8] #voltage range in which CTMU is most accurate
		CT=10
		CR=1
		MAX_CR=3
		MAX_CT=45000
		CC=True #Constant current mode
		iterations = 0
		start_time=time.time()
		self.__charge_cap__(0,20000)
		try:
			self.__print__('measure CAP via CC charge')
			while (time.time()-start_time)<2 and CR<=MAX_CR:
				if CT<65000 and CC:   #Constant current mode
					V,C = self.__get_capacitance__(CR,0,CT)
					self.__print__('%.2f V,%.2e C  %.2f CR,%.2f CT'%(V,C,CR,CT))

					if V>GOOD_VOLTS[0] and V<GOOD_VOLTS[1]:
						return C
					elif V<GOOD_VOLTS[0] and V>0.01 and CT<MAX_CT:  #Room to increase CT (integration time)
						if GOOD_VOLTS[0]/V > 1.1 and iterations<5:
							CT=int(CT*GOOD_VOLTS[0]/V)
							iterations+=1
							self.__print__('increased CT ',CT)
						elif iterations==5:
							return self.capacitance_via_RC_discharge()
						else:
							return C
					elif CT>MAX_CT :
						if V<=0.1 and CR<=MAX_CR:
							iterations=0;CT=10;CR+=1
						else:
							self.__print__('Capacitance too high for this method')
							CC=0
							self.__print__('Capture mode ')
							continue
					else:
						iterations=0;CT=10;CR+=1
				else:
					self.__print__('CT too high')
					return self.capacitance_via_RC_discharge()

			return self.capacitance_via_RC_discharge()
			print ('oh no')
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def __calibrate_ctmu__(self,scalers):
		#self.currents=[0.55e-3/scalers[0],0.55e-6/scalers[1],0.55e-5/scalers[2],0.55e-4/scalers[3]]
		self.currents=[0.55e-3,0.55e-6,0.55e-5,0.55e-4]
		self.currentScalers = scalers
		#print (self.currentScalers,scalers,self.SOCKET_CAPACITANCE)

	def __get_capacitance__(self,current_range,trim, Charge_Time):  #time in uS
		try:
			V = self.__get_capacitance_voltage__(current_range,trim, Charge_Time)
			Charge_Current = self.currents[current_range]*(100+trim)/100.0
			if V:
				C = (Charge_Current*Charge_Time*1e-6/V - self.SOCKET_CAPACITANCE)/self.currentScalers[current_range]
				#print (V,C,(Charge_Current*Charge_Time*1e-6/V)/self.currentScalers[current_range])
				#print (current_range,trim, Charge_Time)
			else: C = 0
			return V,C
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def __get_capacitance_voltage__(self,current_range,trim, Charge_Time):  #time in uS
		try:
			self.__charge_cap__(0,30000)
			self.H.__sendByte__(CP.COMMON)
			self.H.__sendByte__(CP.GET_CAPACITANCE)
			self.H.__sendByte__(current_range)
			if(trim<0):
				self.H.__sendByte__( int(31-abs(trim)/2)|32)
			else:
				self.H.__sendByte__(int(trim/2))
			self.H.__sendInt__(Charge_Time)
			time.sleep(Charge_Time*1e-6+.02)
			VCode = self.H.__getInt__()
			V = 3.3*VCode/4095
			self.H.__get_ack__()
			return V
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def get_temperature(self):
		"""
		return the processor's temperature
		
		:return: Chip Temperature in degree Celcius
		""" 
		cs=3
		V=self.get_ctmu_voltage(0b11110,cs,0)
		
		if cs==1:    return (646-V*1000)/1.92   	#current source = 1
		elif cs==2:  return (701.5-V*1000)/1.74     #current source = 2
		elif cs==3:  return (760-V*1000)/1.56       #current source = 3

	def get_ctmu_voltage(self,channel,Crange,tgen=1):
		"""
		get_ctmu_voltage(5,2)  will activate a constant current source of 5.5uA on IN1 and then measure the voltage at the output.
		If a diode is used to connect IN1 to ground, the forward voltage drop of the diode will be returned. e.g. .6V for a 4148diode.
		
		If a resistor is connected, ohm's law will be followed within reasonable limits
		
		channel=5 for IN1
		
		CRange=0   implies 550uA
		CRange=1   implies 0.55uA
		CRange=2   implies 5.5uA
		CRange=3   implies 55uA
		
		:return: Voltage
		""" 
		if channel=='IN1':channel=5
		try:
			self.H.__sendByte__(CP.COMMON)
			self.H.__sendByte__(CP.GET_CTMU_VOLTAGE)
			self.H.__sendByte__((channel)|(Crange<<5)|(tgen<<7))

			#V = [self.H.__getInt__() for a in range(16)]
			#print(V)
			#V=V[3:]
			v=self.H.__getInt__() #16*voltage across the current source
			#v=sum(V)

			self.H.__get_ack__()
			V=3.3*v/16/4095.
			#print(V)
			return V
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def __start_ctmu__(self,Crange,trim,tgen=1):
		try:
			self.H.__sendByte__(CP.COMMON)
			self.H.__sendByte__(CP.START_CTMU)
			self.H.__sendByte__((Crange)|(tgen<<7))
			self.H.__sendByte__(trim)
			self.H.__get_ack__()
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def __stop_ctmu__(self):
		try:
			self.H.__sendByte__(CP.COMMON)
			self.H.__sendByte__(CP.STOP_CTMU)
			self.H.__get_ack__()
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)
		
	def resetHardware(self):
		"""
		Resets the device, and standalone mode will be enabled if an OLED is connected to the I2C port
		"""
		try:
			self.H.__sendByte__(CP.COMMON)
			self.H.__sendByte__(CP.RESTORE_STANDALONE)
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def read_flash(self,page,location):
		"""
		Reads 16 BYTES from the specified location

		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		================    ============================================================================================
		**Arguments** 
		================    ============================================================================================
		page                page number. 20 pages with 2KBytes each
		location            The flash location(0 to 63) to read from .
		================    ============================================================================================

		:return: a string of 16 characters read from the location
		"""
		try:
			self.H.__sendByte__(CP.FLASH)
			self.H.__sendByte__(CP.READ_FLASH)
			self.H.__sendByte__(page)   #send the page number. 20 pages with 2K bytes each
			self.H.__sendByte__(location)   #send the location
			ss=self.H.fd.read(16)
			self.H.__get_ack__()
			return ss
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def __stoa__(self,s):
		return s
		return [ord(a) for a in s]

	def __atos__(self,a):
		return ''.join(chr(e) for e in a)

	def read_bulk_flash(self,page,numbytes):
		"""
		Reads BYTES from the specified location

		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		================    ============================================================================================
		**Arguments** 
		================    ============================================================================================
		page                Block number. 0-20. each block is 2kB.
		numbytes               Total bytes to read
		================    ============================================================================================

		:return: a string of 16 characters read from the location
		"""
		try:
			self.H.__sendByte__(CP.FLASH)
			self.H.__sendByte__(CP.READ_BULK_FLASH)
			bytes_to_read = numbytes
			if numbytes%2: bytes_to_read+=1     #bytes+1 . stuff is stored as integers (byte+byte) in the hardware
			self.H.__sendInt__(bytes_to_read)   
			self.H.__sendByte__(page)
			ss=self.H.fd.read(int(bytes_to_read))
			self.H.__get_ack__()
			self.__print__('Read from ',page,',',bytes_to_read,' :',self.__stoa__(ss[:40]),'...')
			if numbytes%2: return ss[:-1]   #Kill the extra character we read. Don't surprise the user with extra data
			return ss
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def write_flash(self,page,location,string_to_write):
		"""
		write a 16 BYTE string to the selected location (0-63)

		DO NOT USE THIS UNLESS YOU'RE ABSOLUTELY SURE KNOW THIS!
		YOU MAY END UP OVERWRITING THE CALIBRATION DATA, AND WILL HAVE
		TO GO THROUGH THE TROUBLE OF GETTING IT FROM THE MANUFACTURER AND
		REFLASHING IT.
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		================    ============================================================================================
		**Arguments** 
		================    ============================================================================================
		page                page number. 20 pages with 2KBytes each
		location            The flash location(0 to 63) to write to.
		string_to_write     a string of 16 characters can be written to each location
		================    ============================================================================================

		"""
		try:
			while(len(string_to_write)<16):string_to_write+='.'
			self.H.__sendByte__(CP.FLASH)
			self.H.__sendByte__(CP.WRITE_FLASH)    #indicate a flash write coming through
			self.H.__sendByte__(page)   #send the page number. 20 pages with 2K bytes each
			self.H.__sendByte__(location)   #send the location
			self.H.fd.write(string_to_write)
			time.sleep(0.1)
			self.H.__get_ack__()
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def write_bulk_flash(self,location,data):
		"""
		write a byte array to the entire flash page. Erases any other data

		DO NOT USE THIS UNLESS YOU'RE ABSOLUTELY SURE YOU KNOW THIS!
		YOU MAY END UP OVERWRITING THE CALIBRATION DATA, AND WILL HAVE
		TO GO THROUGH THE TROUBLE OF GETTING IT FROM THE MANUFACTURER AND
		REFLASHING IT.
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		================    ============================================================================================
		**Arguments** 
		================    ============================================================================================
		location            Block number. 0-20. each block is 2kB.
		bytearray           Array to dump onto flash. Max size 2048 bytes
		================    ============================================================================================

		"""
		if(type(data)==str):data = [ord(a) for a in data]
		if len(data)%2==1:data.append(0)
		try:
			#self.__print__('Dumping at',location,',',len(bytearray),' bytes into flash',bytearray[:10])
			self.H.__sendByte__(CP.FLASH)
			self.H.__sendByte__(CP.WRITE_BULK_FLASH)   #indicate a flash write coming through
			self.H.__sendInt__(len(data))  #send the length
			self.H.__sendByte__(location)
			for n in range(len(data)):
				self.H.__sendByte__(data[n])
				#Printer('Bytes written: %d'%(n+1))
			self.H.__get_ack__()
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

			#verification by readback
			tmp=[ord(a) for a in self.read_bulk_flash(location,len(data))]
			print ('Verification done',tmp == data)
			if tmp!=data: raise Exception('Verification by readback failed')

	#-------------------------------------------------------------------------------------------------------------------#

	#|===============================================WAVEGEN SECTION====================================================|   
	#|This section has commands related to waveform generators W1, W2, PWM outputs, servo motor control etc.            |
	#-------------------------------------------------------------------------------------------------------------------#


	def set_sine(self,freq):
		"""
		Set the frequency of wavegen 1 after setting its waveform type to sinusoidal
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  ============================================================================================
		**Arguments** 
		==============  ============================================================================================
		frequency       Frequency to set on wave generator 
		==============  ============================================================================================
		
		
		:return: frequency
		"""
		return self.set_wave(freq,'sine')

	def set_wave(self,freq,waveType=None):
		"""
		Set the frequency of wavegen 1
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  ============================================================================================
		**Arguments** 
		==============  ============================================================================================
		frequency       Frequency to set on wave generator 1. 
		waveType		'sine','tria' . Default : Do not reload table. and use last set table
		==============  ============================================================================================
		
		
		:return: frequency
		"""
		if freq<0.1:
			self.__print__('freq too low. switching off sine',freq)
			self.H.__sendByte__(CP.WAVEGEN)
			self.H.__sendByte__(CP.SET_SINE1)
			self.H.__sendByte__(0x80)    #switch off sine
			self.H.__sendInt__(0)
			self.H.__get_ack__()
			return 0
		elif freq<1100:
			HIGHRES=1
			table_size = 512
		else:
			HIGHRES=0
			table_size = 32
		if freq<0.1:
			self.__print__('freq too low')

		if waveType: #User wants to set a particular waveform type. sine or tria
			if waveType in ['sine','tria']:
				if(self.WaveType!=waveType):
					self.load_equation(waveType)
			else:
				print ('Not a valid waveform. try sine or tria')

		p=[1,8,64,256]
		prescaler=0
		while prescaler<=3:
			wavelength = int(round(64e6/freq/p[prescaler]/table_size))
			freq = (64e6/wavelength/p[prescaler]/table_size)
			if wavelength<65525: break
			prescaler+=1
		if prescaler==4:
			self.__print__('out of range')
			return 0


		try:
			self.H.__sendByte__(CP.WAVEGEN)
			self.H.__sendByte__(CP.SET_SINE1)
			self.H.__sendByte__(HIGHRES|(prescaler<<1))    #use larger table for low frequencies
			self.H.__sendInt__(wavelength-1)        
			self.H.__get_ack__()
			self.sinefreq = freq
			val =  64e6/p[prescaler]/table_size/wavelength
			if self.WaveMode not in ['sine','tria']:
				#print ('switching back to sine..')
				time.sleep(0.3)   
				self.WaveMode = 'sine'


			return val
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)


	def set_sine_amp(self,value):
		"""
		Set the maximum voltage of wavegen 1
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  ============================================================================================
		**Arguments** 
		==============  ============================================================================================
		value           2    1x amplitude (3.3V)
		                1    1V
		                0    100mV
		==============  ============================================================================================		
		
		"""

		try:
			self.H.__sendByte__(CP.WAVEGEN)
			self.H.__sendByte__(CP.SET_SINE_AMP)
			self.H.__sendByte__(value)    #use larger table for low frequencies
			self.H.__get_ack__()
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def readbackWaveform(self,chan):
		"""
		read the frequency of wavegen 
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  ============================================================================================
		**Arguments** 
		==============  ============================================================================================
		chan            Any of WG,SQR1
		==============  ============================================================================================
		
		
		:return: frequency
		"""
		if chan=='WG':return self.sinefreq
		elif chan[:3]=='SQR1':return self.sqrfreq

	def load_equation(self,function,span=None,**kwargs):
		'''
		Load an arbitrary waveform to the waveform generators
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  ============================================================================================
		**Arguments** 
		==============  ============================================================================================
		function            A function that will be used to generate the datapoints
		span                the range of values in which to evaluate the given function
		==============  ============================================================================================
		
		.. code-block:: python
		  
		  fn = lambda x:abs(x-50)  #Triangular waveform 
		  self.I.load_waveform(,fn,[0,100])
		  #Load triangular wave to wavegen 
		  
		  #Load sinusoidal wave to wavegen
		  self.I.load_waveform(np.sin,[0,2*np.pi])

		'''
		if function=='sine' or function==np.sin:
			function = np.sin; span = [0,2*np.pi]
			self.WaveType = 'sine'
		elif function=='tria':
			function = lambda x: abs(x%4-2)-1
			span = [-1,3]
			self.WaveType = 'tria'
		else:
			self.WaveType = 'arbit'

		x1=np.linspace(span[0],span[1],512+1)[:-1]
		y1=function(x1)
		self.load_table(y1,self.WaveType,**kwargs)

	def load_table(self,points,mode='arbit',**kwargs):
		'''
		Load an arbitrary waveform table to the waveform generators
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  ============================================================================================
		**Arguments** 
		==============  ============================================================================================
		points          A list of 512 datapoints exactly
		mode			Optional argument. Type of waveform. default value 'arbit'. accepts 'sine', 'tria'
		==============  ============================================================================================
		
		example::
		  
		  >>> self.I.load_waveform_table(range(512))
		  #Load sawtooth wave to wavegen 1
		'''
		self.WaveType = mode

		
		#Normalize and scale .
		# y1 = array with 512 points between 0 and 512
		# y2 = array with 32 points between 0 and 64

		amp = kwargs.get('amp',0.95)
		LARGE_MAX = 511*amp  # A form of amplitude control. This decides the max PWM duty cycle out of 512 clocks
		SMALL_MAX = 63 *amp  # Max duty cycle out of 64 clocks
		y1=np.array(points)
		y1-=min(y1)
		y1=y1/float(max(y1))
		y1=1.-y1
		y1 = list(np.int16(np.round( LARGE_MAX - LARGE_MAX*y1 )))

		y2=np.array(points[::16])
		y2-=min(y2)
		y2 = y2/float(max(y2))
		y2=1.- y2
		y2 = list(np.int16(np.round( SMALL_MAX - SMALL_MAX*y2 )))

		try:
			self.H.__sendByte__(CP.WAVEGEN)
			self.H.__sendByte__(CP.LOAD_WAVEFORM1)

			#print(max(y1),max(y2))
			for a in y1:
				self.H.__sendInt__(a)
				#time.sleep(0.001)
			for a in y2:
				self.H.__sendByte__(CP.Byte.pack(a))
				#time.sleep(0.001)
			time.sleep(0.01)
			self.H.__get_ack__()        
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def set_sqr1(self,freq,duty_cycle=50):
		"""
		Set the frequency of sqr1
		Minimum possible frequency  is 4 Hz . For slower frequencies, Refer to set_sqr1_slow (Minimum Frequency 0.015Hz)

		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  ============================================================================================
		**Arguments** 
		==============  ============================================================================================
		frequency       Frequency
		duty_cycle      Percentage of high time
		==============  ============================================================================================
		"""
		if freq < 4:              
			return self.set_sqr1_slow(freq, duty_cycle)

		if freq==0:
			self.set_state(SQR1=1)
			return 0
		elif freq==-1:
			self.set_state(SQR1=0)
			return -1
		if duty_cycle==0:
			return None
		if freq>10e6:
			print ('Frequency is greater than 10MHz. ')
			return 0
			
		p=[1,8,64,256]
		prescaler=0
		while prescaler<=3:
			wavelength = int(64e6/freq/p[prescaler])
			if wavelength<65525: break
			prescaler+=1
		if prescaler==4 or wavelength==0:
			self.__print__('out of range')
			return 0
		high_time = wavelength*duty_cycle/100.
		try:
			self.H.__sendByte__(CP.WAVEGEN)
			self.H.__sendByte__(CP.SET_SQR1)
			self.H.__sendInt__(int(round(wavelength)))
			self.H.__sendInt__(int(round(high_time)))
			self.H.__sendByte__(prescaler)
			self.H.__get_ack__()
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

		self.sqrfreq=64e6/wavelength/p[prescaler&0x3]
		return self.sqrfreq

	def set_sqr1_slow(self,freq,duty_cycle=50):
		"""
		Set the frequency of sqr1 using 32 bit counters. Sine wave & SQR2 are disabled
		Minimum possible frequency  is 0.015 Hz
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  ============================================================================================
		**Arguments** 
		==============  ============================================================================================
		frequency       Frequency
		duty_cycle      Percentage of high time
		==============  ============================================================================================
		"""
		if freq==0:
			self.set_state(SQR1=1)
			return 0
		elif freq==-1:
			self.set_state(SQR1=0)
			return -1
		if duty_cycle==0:
			return None
		wavelength = int(64e6/freq)
		if wavelength>(2**32-1):
			self.__print__('out of range')
			return 0
		high_time = wavelength*duty_cycle/100.
		W = int(round(wavelength))
		H = int(round(high_time))
		try:
			self.H.__sendByte__(CP.WAVEGEN)
			self.H.__sendByte__(CP.SET_SQR_LONG)
			self.H.__sendInt__(W&0xFFFF)   #lsb
			self.H.__sendInt__((W>>16)&0xFFFF) #msb
			self.H.__sendInt__(H&0xFFFF)   #lsb
			self.H.__sendInt__((H>>16)&0xFFFF) #msb
			self.H.__get_ack__()
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

		self.sqrfreq=64e6/wavelength
		return self.sqrfreq

	def set_sqr2(self,freq,duty_cycle=50):
		"""
		Set the frequency of sqr1 (output enabled on OD1 . Sine is disabled

		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  ============================================================================================
		**Arguments** 
		==============  ============================================================================================
		frequency       Frequency
		duty_cycle      Percentage of high time
		==============  ============================================================================================
		"""
		if freq==0:
			self.set_state(SQR2=1)
			return 0
		elif freq==-1:
			self.set_state(SQR2=0)
			return -1
		if duty_cycle==0:
			return None

		if freq>10e6:
			print ('Frequency is greater than 10MHz. ')
			return 0
			
		p=[1,8,64,256]
		prescaler=0
		while prescaler<=3:
			wavelength = int(64e6/freq/p[prescaler])
			if wavelength<65525: break
			prescaler+=1
		if prescaler==4 or wavelength==0:
			self.__print__('out of range')
			return 0
		high_time = wavelength*duty_cycle/100.
		#self.__print__(wavelength,':',high_time,':',prescaler)
		try:
			self.H.__sendByte__(CP.WAVEGEN)
			self.H.__sendByte__(CP.SET_SQR1)
			self.H.__sendInt__(int(round(wavelength)))
			self.H.__sendInt__(int(round(high_time)))
			prescaler |= 0x4   # Instruct hardware to set sqr2 , not sqr1
			self.H.__sendByte__(prescaler)
			self.H.__get_ack__()
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)
		self.WaveMode = 'sqr2'
		self.sqrfreq=64e6/wavelength/p[prescaler&0x3]
		return self.sqrfreq

	def set_sqrs(self,freq,diff=0):         # Freq in Hertz, phase difference in % of T
		"""
		TEST
		Set the frequency of sqr1

		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  ============================================================================================
		**Arguments** 
		==============  ============================================================================================
		frequency       Frequency
		duty_cycle      Percentage of high time
		==============  ============================================================================================
		"""
		if freq==0 or diff==0 : return None
		if freq>10e6:
			print ('Frequency is greater than 10MHz. ')
			return 0
			
		p=[1,8,64,256]
		prescaler=0
		while prescaler<=3:
			wavelength = int(64e6/freq/p[prescaler])
			if wavelength<65525: break
			prescaler+=1
		if prescaler==4 or wavelength==0:
			self.__print__('out of range')
			return 0
		phase = wavelength*diff/100.
		self.__print__(wavelength,':',phase,':',prescaler)
		try:
			self.H.__sendByte__(CP.WAVEGEN)
			self.H.__sendByte__(CP.SET_SQR1)
			self.H.__sendInt__(int(round(wavelength)))
			self.H.__sendInt__(int(round(phase)))
			prescaler |= 0x8   # Instruct hardware to set both sqr1 , sqr2
			self.H.__sendByte__(prescaler)
			self.H.__get_ack__()
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

		self.sqrfreq=64e6/wavelength/p[prescaler&0x3]
		return self.sqrfreq

	#|===============================================ANALOG OUTPUTS ====================================================|   
	#|This section has commands related to current and voltage sources PV1,PV2					            |
	#-------------------------------------------------------------------------------------------------------------------#

	def set_pv1(self,val):
		"""
		Set the voltage on PV1
		12-bit DAC...  -5V to 5V
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  ============================================================================================
		**Arguments** 
		==============  ============================================================================================
		val             Output voltage on PV1. -5V to 5V
		==============  ============================================================================================

		"""
		return self.DAC.setVoltage('PV1',val)

	def set_pv2(self,val):
		"""
		Set the voltage on PV2.
		12-bit DAC...  0-3.3V
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  ============================================================================================
		**Arguments** 
		==============  ============================================================================================
		val             Output voltage on PV2. 0-3.3V
		==============  ============================================================================================

		:return: Actual value set on pv2
		"""
		return self.DAC.setVoltage('PV2',val)


	def get_pv1(self):
		"""
		get the last set voltage on PV1
		12-bit DAC...  -5V to 5V
		"""
		return self.DAC.getVoltage('PV1')
	def get_pv2(self):
		return self.DAC.getVoltage('PV2')


	#-------------------------------------------------------------------------------------------------------------------#

	#|======================================READ PROGRAM AND DATA ADDRESSES=============================================|   
	#|Direct access to RAM and FLASH		     																		|
	#-------------------------------------------------------------------------------------------------------------------#

	def read_program_address(self,address):
		"""
		Reads and returns the value stored at the specified address in program memory

		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  ============================================================================================
		**Arguments** 
		==============  ============================================================================================
		address         Address to read from. Refer to PIC24EP64GP204 programming manual
		==============  ============================================================================================
		"""
		try:
			self.H.__sendByte__(CP.COMMON)
			self.H.__sendByte__(CP.READ_PROGRAM_ADDRESS)
			self.H.__sendInt__(address&0xFFFF)
			self.H.__sendInt__((address>>16)&0xFFFF)
			v=self.H.__getInt__()
			self.H.__get_ack__()
			return v
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def device_id(self):
		try:
			a=self.read_program_address(0x800FF8)
			b=self.read_program_address(0x800FFa)
			c=self.read_program_address(0x800FFc)
			d=self.read_program_address(0x800FFe)
			val = d|(c<<16)|(b<<32)|(a<<48)
			self.__print__(a,b,c,d,hex(val))
			return val
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)


	def read_data_address(self,address):
		"""
		Reads and returns the value stored at the specified address in RAM

		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  ============================================================================================
		**Arguments** 
		==============  ============================================================================================
		address         Address to read from.  Refer to PIC24EP64GP204 programming manual|
		==============  ============================================================================================
		"""
		try:
			self.H.__sendByte__(CP.COMMON)
			self.H.__sendByte__(CP.READ_DATA_ADDRESS)
			self.H.__sendInt__(address&0xFFFF)
			v=self.H.__getInt__()
			self.H.__get_ack__()
			return v
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def __write_data_address__(self,address,value):
		#address         Address to write to.  Refer to PIC24EP64GP204 programming manual
		try:
			self.H.__sendByte__(CP.COMMON)
			self.H.__sendByte__(CP.WRITE_DATA_ADDRESS)
			self.H.__sendInt__(address&0xFFFF)
			self.H.__sendInt__(value)
			self.H.__get_ack__()
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

		
	#-------------------------------------------------------------------------------------------------------------------#

	#|==============================================MOTOR SIGNALLING====================================================|   
	#|Set servo motor angles via SQ1-4. Control one stepper motor using SQ1-4											|
	#-------------------------------------------------------------------------------------------------------------------#



	def servo(self,angle,chan='SQR1'):
		'''
		Output A PWM waveform on SQR1/SQR2 corresponding to the angle specified in the arguments.
		This is used to operate servo motors.  Tested with 9G SG-90 Servo motor.
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  ============================================================================================
		**Arguments** 
		==============  ============================================================================================
		angle           0-180. Angle corresponding to which the PWM waveform is generated.
		chan            'SQR1' or 'SQR2'. Whether to use SQ1 or SQ2 to output the PWM waveform used by the servo 
		==============  ============================================================================================
		'''
		if chan=='SQR1':self.set_sqr1(100,7.5+19.*angle/180)#100Hz

	def sr04_distance(self,speed_of_sound=340.):
		'''
		
		Read data from ultrasonic distance sensor HC-SR04/HC-SR05.  Sensors must have separate trigger and output pins.
		First a 10uS pulse is output on SQR2.  SQR2 must be connected to the TRIG pin on the sensor prior to use.

		Upon receiving this pulse, the sensor emits a sequence of sound pulses, and the logic level of its output
		pin(which we will monitor via IN2) is also set high.  The logic level goes LOW when the sound packet
		returns to the sensor, or when a timeout occurs.

		The ultrasound sensor outputs a series of 8 sound pulses at 40KHz which corresponds to a time period
		of 25uS per pulse. These pulses reflect off of the nearest object in front of the sensor, and return to it.
		The time between sending and receiving of the pulse packet is used to estimate the distance.
		If the reflecting object is either too far away or absorbs sound, less than 8 pulses may be received, and this
		can cause a measurement error of 25uS which corresponds to 8mm.
		
		returns 0 upon timeout
		'''
		try:
			self.H.__sendByte__(CP.COMMON)
			self.H.__sendByte__(CP.HCSR04)

			timeout = 0.2
			timeout_msb = int((timeout*64e6))>>16
			self.H.__sendInt__(timeout_msb)
			self.H.waitForData(timeout)
			tmt = self.H.__getByte__()
			A=self.H.__getLong__()
			#B=self.H.__getInt__()
			#print(A,tmt)
			self.H.__get_ack__()
			rtime = lambda t: t/64e6

			if (tmt) or A>10e5: return 0  #2.5 metre limit
			return 100*speed_of_sound*rtime(A)/2.  #multiply by 100 to convert to cms
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def sr04_distance_time(self,speed_of_sound=340.):
		'''

		Return the distance measured by ultrasonic sensor HCSR04 and timestamp (S). Refer to :func:`sr04_distance` for full documentation
		:return: T,S

		'''
		D=self.sr04_distance(speed_of_sound)
		T=time.time()
		return T,D

	def readLog(self):
		'''
		read hardware debug log. 		
		'''
		try:
			self.H.__sendByte__(CP.COMMON)
			self.H.__sendByte__(CP.READ_LOG)
			log  = self.H.fd.readline().strip()
			self.H.__get_ack__()
			return log
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)
	
	def raiseException(self,ex, msg):
			msg += '\n' + ex.message
			#self.H.disconnect()
			raise RuntimeError(msg)

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
		

if __name__ == "__main__":
	print("""this is not an executable file
	import expeyes.eyes17
	I=expeyes.eyes17.open()
	I.get_voltage('A1')
	""")
	
	I=open(verbose = True)
	#print (I.analogInputSources['A1'].calibrationCorrection)
	#I.capture_traces(1,1000,1,'A1')
	
	'''
	for a in [1e6,1e2,1e5,40]:
		t=time.time()
		I.set_sqr1(a)
		#I.set_state(SQR1=1,OD1=1)
		#I.get_states()
		print ('C',time.time()-t)
		print ('FREQ',I.get_high_freq('IN2') , I.get_freq('IN2'),I.DoublePinEdges('IN2','IN2','rising','rising',2,4,sequential=False))
		print (I.multi_r2rtime('IN2',48,2.0),I.r2rtime('IN2','IN2'),I.r2ftime('IN2','IN2'),I.f2rtime('IN2','IN2'),I.f2ftime('IN2','IN2'),)
	'''
	#print (I.set2rtime('SQR1','ID1'),I.clr2ftime('SQR1','IN2'))

	#I.select_range('A1',2)
	#I.set_sqr1_slow(0.1,10)
	
	#I.set_sine(2000)
	#TEST DUTY_CYCLE
	#duty = 50.
	#I.set_sqr1(1e4,duty)
	#I.duty_cycle('IN2')
	#I.get_freq('IN2')
	#while 1:
	#	v=I.duty_cycle('IN2')
	#	print (v,I.get_high_freq('IN2'))
	#	if abs(v-duty)>1:print(v)
		
	#TEST COMPARATOR ON SEN
	#while 1: print (I.get_freq('SEN'))

	#TEST Multi Channel 12-bit scope
	#x,y = I.capture_hr_multiple(200,10,'A1')
	#print (x,y)

	#TEST Wireless functions
	#I.NRF.start_token_manager()
	#while 1:
	#	print(I.readLog(),I.NRF.get_status(),I.NRF.read_register(I.NRF.SETUP_RETR))
	#	time.sleep(0.5)
	


	#print (I.capacitance_via_RC_discharge())
	print (I.get_capacitance())
	#I.set_state(CCS = True)
	#x,y,x2,y2,x3,y3 = I.capture_hr_multiple(1000,1,'A1','A2','A3')
	#print (y,y2,y3)
	#from pylab import *
	#plot(x,y)
	#plot(x2,y2)
	#plot(x3,y3)
	#show()

	#print(I.get_capacitance())
	#TEST DIGITAL OUTPUT
	#I.set_state(SQR2=0)
	#TEST Distance Sensor HC SR04
	#while 1:  print(I.sr04_distance())
	#I.set_pv1(0.01)
	#I.select_range('A1',.5)
	#I.select_range('A2',.5)
	#while 1:
	#	print (I.get_voltage('A1'))
	#from pylab import *
	#x,y,x2,y2 = I.capture2(11,10)
	#print (x,x2)
	#x=[];y=[]
	#I.select_range('A1',8)
	#I.set_pv1(-3.3)
	#time.sleep(0.1)
	#for a in np.linspace(-3.3,3.3,100):
	#	x.append(I.set_pv1(a))
	#	time.sleep(0.02)
	#	y.append(I.get_voltage('A1'))
	#plot(x,np.array(y)-np.array(x))
	#show()
	#x=np.linspace(0,4095,4096)
	#plot(x,I.analogInputSources['A2'].polynomials[7](x)+np.poly1d([0,0.00025183150183150186,-0.515625])(x) )
	#show()
	#for a in range(20):print (I.get_capacitance())
	#I=connect(verbose=True,load_calibration=False)
