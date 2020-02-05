# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
from __future__ import print_function
from . import commands_proto as CP
import numpy as np 
import time,inspect

	
class I2C():
	"""
	Methods to interact with the I2C port.



	.. code-block:: python

		#Code Example : Read Values from an HMC5883L 3-axis Magnetometer(compass) [GY-273 sensor] connected to the I2C port
		ADDRESS = 0x1E
		import expeyes.eyes17
		I = expeyes.eyes17.connect() 
		
		# writing to 0x1E, set gain(0x01) to smallest(0 : 1x)
		I.I2C.bulkWrite(ADDRESS,[0x01,0])
		
		# writing to 0x1E, set mode conf(0x02), continuous measurement(0)
		I.I2C.bulkWrite(ADDRESS,[0x02,0])

		# read 6 bytes from addr register on I2C device located at ADDRESS
		vals = I.I2C.bulkRead(ADDRESS,addr,6)
			
		from numpy import int16
		#conversion to signed datatype
		x=int16((vals[0]<<8)|vals[1])
		y=int16((vals[2]<<8)|vals[3])
		z=int16((vals[4]<<8)|vals[5])
		print (x,y,z)

	"""

	def __init__(self,H):
		self.H = H
		from .import sensorlist
		self.SENSORS=sensorlist.sensors
		self.buff=np.zeros(10000)

	def init(self):
		try:
			self.H.__sendByte__(CP.I2C_HEADER)
			self.H.__sendByte__(CP.I2C_INIT)
			self.H.__get_ack__()
		except Exception as ex:
			print(ex, "Communication Error")
			return False

	def enable_smbus(self):
		try:
			self.H.__sendByte__(CP.I2C_HEADER)
			self.H.__sendByte__(CP.I2C_ENABLE_SMBUS)
			self.H.__get_ack__()
		except Exception as ex:
			print(ex, "Communication Error")
			return False

	def pullSCLLow(self,uS):
		"""
		Hold SCL pin at 0V for a specified time period. Used by certain sensors such
		as MLX90316 PIR for initializing.
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		================    ============================================================================================
		**Arguments** 
		================    ============================================================================================
		uS                  Time(in uS) to hold SCL output at 0 Volts
		================    ============================================================================================

		"""
		try:
			self.H.__sendByte__(CP.I2C_HEADER)
			self.H.__sendByte__(CP.I2C_PULLDOWN_SCL)
			self.H.__sendInt__(uS)
			self.H.__get_ack__()
		except Exception as ex:
			print(ex, "Communication Error")
			return False
		 
	def config(self,freq,verbose=True):
		"""
		Sets frequency for I2C transactions
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		================    ============================================================================================
		**Arguments** 
		================    ============================================================================================
		freq                I2C frequency
		================    ============================================================================================
		"""
		try:
			self.H.__sendByte__(CP.I2C_HEADER)
			self.H.__sendByte__(CP.I2C_CONFIG)
			#freq=1/((BRGVAL+1.0)/64e6+1.0/1e7)
			BRGVAL=int( (1./freq-1./1e7)*64e6-1 )
			if BRGVAL>511:
				BRGVAL=511
				if verbose:print ('Frequency too low. Setting to :',1/((BRGVAL+1.0)/64e6+1.0/1e7))
			self.H.__sendInt__(BRGVAL) 
			self.H.__get_ack__()
		except Exception as ex:
			print(ex, "Communication Error")
			return False

	def start(self,address,rw):
		"""
		Initiates I2C transfer to address via the I2C port
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		================    ============================================================================================
		**Arguments** 
		================    ============================================================================================
		address             I2C slave address\n
		rw                  Read/write.
							- 0 for writing
							- 1 for reading.
		================    ============================================================================================
		"""
		try:
			self.H.__sendByte__(CP.I2C_HEADER)
			self.H.__sendByte__(CP.I2C_START)
			self.H.__sendByte__(((address<<1)|rw)&0xFF) # address
			return self.H.__get_ack__()>>4
		except Exception as ex:
			print(ex, "Communication Error")
			return False

	def stop(self):
		"""
		stops I2C transfer
		
		:return: Nothing
		"""
		try:
			self.H.__sendByte__(CP.I2C_HEADER)
			self.H.__sendByte__(CP.I2C_STOP)
			self.H.__get_ack__()
		except Exception as ex:
			print(ex, "Communication Error")
			return False

	def wait(self):
		"""
		wait for I2C

		:return: Nothing
		"""
		try:
			self.H.__sendByte__(CP.I2C_HEADER)
			self.H.__sendByte__(CP.I2C_WAIT)
			self.H.__get_ack__()
		except Exception as ex:
			print(ex, "Communication Error")
			return False

	def send(self,data):
		"""
		SENDS data over I2C.
		The I2C bus needs to be initialized and set to the correct slave address first.
		Use I2C.start(address) for this.
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		================    ============================================================================================
		**Arguments** 
		================    ============================================================================================
		data                Sends data byte over I2C bus
		================    ============================================================================================

		:return: Nothing
		"""
		try:
			self.H.__sendByte__(CP.I2C_HEADER)
			self.H.__sendByte__(CP.I2C_SEND)
			self.H.__sendByte__(data)        #data byte
			return self.H.__get_ack__()>>4
		except Exception as ex:
			print(ex, "Communication Error")
			return False
		
	def send_burst(self,data):
		"""
		SENDS data over I2C. The function does not wait for the I2C to finish before returning.
		It is used for sending large packets quickly.
		The I2C bus needs to be initialized and set to the correct slave address first.
		Use start(address) for this.

		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		================    ============================================================================================
		**Arguments** 
		================    ============================================================================================
		data                Sends data byte over I2C bus
		================    ============================================================================================

		:return: Nothing
		"""
		try:
			self.H.__sendByte__(CP.I2C_HEADER)
			self.H.__sendByte__(CP.I2C_SEND_BURST)
			self.H.__sendByte__(data)        #data byte
		except Exception as ex:
			print(ex, "Communication Error")
			return False

	def restart(self,address,rw):
		"""
		Initiates I2C transfer to address

		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		================    ============================================================================================
		**Arguments** 
		================    ============================================================================================
		address             I2C slave address
		rw                  Read/write.
							* 0 for writing
							* 1 for reading.
		================    ============================================================================================

		"""
		try:
			self.H.__sendByte__(CP.I2C_HEADER)
			self.H.__sendByte__(CP.I2C_RESTART)
			self.H.__sendByte__(((address<<1)|rw)&0xFF) # address
		except Exception as ex:
			print(ex, "Communication Error")
		return self.H.__get_ack__()>>4

	def simpleRead(self,addr,numbytes):
		"""
		Read bytes from I2C slave without first transmitting the read location.
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		================    ============================================================================================
		**Arguments** 
		================    ============================================================================================
		addr                Address of I2C slave
		numbytes            Total Bytes to read
		================    ============================================================================================
		"""
		self.start(addr,1)
		vals=self.read(numbytes)
		return vals

	def read(self,length):
		"""
		Reads a fixed number of data bytes from I2C device. Fetches length-1 bytes with acknowledge bits for each, +1 byte
		with Nack.

		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		================    ============================================================================================
		**Arguments** 
		================    ============================================================================================
		length              number of bytes to read from I2C bus
		================    ============================================================================================
		"""
		data=[]
		try:
			for a in range(length-1):
				self.H.__sendByte__(CP.I2C_HEADER)
				self.H.__sendByte__(CP.I2C_READ_MORE)
				data.append(self.H.__getByte__())
				self.H.__get_ack__()
			self.H.__sendByte__(CP.I2C_HEADER)
			self.H.__sendByte__(CP.I2C_READ_END)
			data.append(self.H.__getByte__())
			self.H.__get_ack__()
		except Exception as ex:
			print(ex, "Communication Error")
			return False
		return data

	def read_repeat(self):
		try:
			self.H.__sendByte__(CP.I2C_HEADER)
			self.H.__sendByte__(CP.I2C_READ_MORE)
			val=self.H.__getByte__()
			self.H.__get_ack__()
		except Exception as ex:
			print(ex, "Communication Error")
			return False
		return val

	def read_end(self):
		try:
			self.H.__sendByte__(CP.I2C_HEADER)
			self.H.__sendByte__(CP.I2C_READ_END)
			val=self.H.__getByte__()
			self.H.__get_ack__()
		except Exception as ex:
			print(ex, "Communication Error")
			return False
		return val


	def read_status(self):
		try:
			self.H.__sendByte__(CP.I2C_HEADER)
			self.H.__sendByte__(CP.I2C_STATUS)
			val=self.H.__getInt__()
			self.H.__get_ack__()
		except Exception as ex:
			print(ex, "Communication Error")
			return False
		return val

	def readBulk(self,device_address,register_address,bytes_to_read):
		try:
			self.H.__sendByte__(CP.I2C_HEADER)
			self.H.__sendByte__(CP.I2C_READ_BULK)
			self.H.__sendByte__(device_address)
			self.H.__sendByte__(register_address)
			self.H.__sendByte__(bytes_to_read)
			data=self.H.fd.read(bytes_to_read)
			self.H.__get_ack__()
			try:
				#print (data)
				#The following try block should be resolved depending on Python Version. P3-serial treats it as Byte arrays
				try:
					return [int(a) for a in data]
				except:
					return [ord(a) for a in data]
				
			except Exception as e:
				print ('Transaction failed',str(e))
				return False
		except Exception as ex:
			print(ex, "Communication Error")
			return False
		
	def writeBulk(self,device_address,bytestream):
		"""
		write bytes to I2C slave
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		================    ============================================================================================
		**Arguments** 
		================    ============================================================================================
		device_address      Address of I2C slave
		bytestream          List of bytes to write
		================    ============================================================================================
		"""
		try:
			self.H.__sendByte__(CP.I2C_HEADER)
			self.H.__sendByte__(CP.I2C_WRITE_BULK)
			self.H.__sendByte__(device_address)
			self.H.__sendByte__(len(bytestream))
			for a in bytestream:
				self.H.__sendByte__(a)
			self.H.__get_ack__()
		except Exception as ex:
			print(ex, "Communication Error")
			return False

	def scan(self,frequency = 200000,verbose=False):
		"""
		Scan I2C port for connected devices
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		================    ============================================================================================
		**Arguments** 
		================    ============================================================================================
		Frequency           I2C clock frequency
		================    ============================================================================================

		:return: Array of addresses of connected I2C slave devices

		"""

		self.config(frequency,verbose)
		addrs=[]
		n=0
		if verbose:
			print ('Scanning addresses 0-127...')
			print ('Address','\t','Possible Devices')
		for a in range(0,128):
			x = self.start(a,0)
			if x&1 == 0:    #ACK received
				addrs.append(a)
				if verbose: print (hex(a),'\t\t',self.SENSORS.get(a,'None'))
				n+=1
			self.stop()

		return addrs


class DACCHAN:
	def __init__(self,name,span,channum,**kwargs):
		self.name = name
		self.channum=channum
		self.VREF = kwargs.get('VREF',0)
		self.SwitchedOff = kwargs.get('STATE',0)
		self.range = span
		slope = (span[1]-span[0])
		intercept = span[0]
		self.VToCode = np.poly1d([4095./slope,-4095.*intercept/slope ])
		self.CodeToV = np.poly1d([slope/4095.,intercept ])
		self.calibration_enabled = False
		self.calibration_table = []
		self.slope=1
		self.offset=0

	def load_calibration_twopoint(self,slope,offset):
		self.calibration_enabled='twopoint'
		self.slope = slope
		self.offset = offset

	def load_calibration_polynomial(self,poly):
		self.calibration_enabled='poly'
		self.polynomial = np.poly1d(poly)

	def apply_calibration(self,v):
		if self.calibration_enabled=='twopoint':		#Overall slope and offset correction is applied
			return int(np.clip(v*self.slope+self.offset,0,4095)	)
		elif self.calibration_enabled=='poly':		    #3 degree polynomial
			return int(np.clip(self.polynomial(v) ,0,4095))
		else:
			return v

	
class PWMDAC:
	defaultVDD =3300.
	RESET =6
	WAKEUP =9
	UPDATE =8
	WRITEALL =64
	WRITEONE =88
	SEQWRITE =80
	VREFWRITE =128
	GAINWRITE =192
	POWERDOWNWRITE =160
	GENERALCALL =0
	def __init__(self,H,vref=3.3,devid=0):
		self.devid = devid
		self.addr = 0x60|self.devid		#0x60 is the base address
		self.H=H
		self.VREF = vref
		self.I2C = I2C(self.H)
		self.SWITCHEDOFF=[0,0,0,0]
		self.VREFS=[0,0,0,0]  #0=Vdd,1=Internal reference
		self.CHANS = {'PV2':DACCHAN('PV2',[-3.3,3.3],2),'PV1':DACCHAN('PV1',[-5.,5.],3)}
		self.CHANNEL_MAP={0:'PCS',2:'PV2',3:'PV1'}
		self.values = {'PV1':0,'PV2':0,'PCS':0}



	def __ignoreCalibration__(self,name):
		self.CHANS[name].calibration_enabled=False

	def setVoltage(self,name,v):
		chan = self.CHANS[name]
		v = int(round(chan.VToCode(v)))		
		return  self.__setRawVoltage__(name,v)

	def getVoltage(self,name):
		return self.values[name]



	def __setRawVoltage__(self,name,v):
		CHAN = self.CHANS[name]
		val = self.CHANS[name].apply_calibration(v)
		self.H.__sendByte__(CP.DAC) #DAC write coming through.(PWM DAC)
		self.H.__sendByte__(CP.SET_DAC)
		if name == 'PV1':
			self.H.__sendInt__(val)
		else:
			self.H.__sendInt__(0x8000|val)
		self.H.__get_ack__()
		
		self.values[name] =  CHAN.CodeToV(v)
		return self.values[name]


