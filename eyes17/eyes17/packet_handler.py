# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
from __future__ import print_function
import time

from . import commands_proto as CP
import serial, os, inspect,platform


class Handler():
	def __init__(self,timeout=1.0,**kwargs):
		self.burstBuffer=b''
		self.loadBurst=False
		self.inputQueueSize=0
		self.BAUD = 500000
		self.RPIBAUD = 500000
		self.timeout=timeout
		self.version_string=b''
		self.connected=False
		self.fd = None
		self.status = 0
		self.expected_version=b'SJ'
		self.occupiedPorts=set()
		self.blockingSocket = None
		self.ARM = False
		if 'port' in kwargs:
			self.portname=kwargs.get('port',None)
			try:
				self.fd,self.version_string,self.connected=self.connectToPort(self.portname)
				if self.connected:return
			except Exception as ex:
				print('Failed to connect to ',self.portname,ex.message)
				
		else:	#Scan and pick a port	
			L = self.listPorts()
			for a in L:
				try:
					self.portname=a
					self.fd,self.version_string,self.connected=self.connectToPort(self.portname)			
					if self.connected:return
				except :
					pass
			if not self.connected:
					if len(self.occupiedPorts) : print('Device not found. Programs already using :',self.occupiedPorts)
		

	def listPorts(self):
		'''
		Make a list of available serial ports. For auto scanning and connecting
		'''
		import glob
		system_name = platform.system()
		if system_name == "Windows":
			# Scan for available ports.
			available = []
			for i in range(256):
				try:
					s = serial.Serial('COM'+str(i))
					available.append('COM'+str(i))
					s.close()
				except serial.SerialException:
					pass
			return available
		elif system_name == "Darwin":
			# Mac
			return glob.glob('/dev/tty*') + glob.glob('/dev/cu*')
		else:
			# Assume Linux or something else
			return glob.glob('/dev/ttyACM*') + glob.glob('/dev/ttyUSB*')


	def connectToPort(self,portname):
		'''
		connect to a port, and check for the right version
		'''
		
		if platform.system() not in ["Windows","Darwin"]:   #Do this check only on Unix
			try:
				import socket
				self.blockingSocket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
				self.blockingSocket.bind('\0eyesj2%s'%portname) 
				self.blockingSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			except socket.error as e:
				self.occupiedPorts.add(portname)
				raise RuntimeError("Another program is using %s (%d)" % (portname) )
		
		fd = serial.Serial(portname, 9600, stopbits=1, timeout = 0.02)
		fd.read(100);fd.close()
		fd = serial.Serial(portname, self.BAUD, stopbits=1, timeout = 1.0,writeTimeout = 0)

		self.cleanup_buffer(fd)
		if(fd.inWaiting()):
			fd.setTimeout(0.1)
			fd.read(1000)
			fd.flush()
			fd.setTimeout(1.0)
		#fd = self.switchBaud(fd,portname) # change if raspberrypi detected
		version= self.get_version(fd)
		if version[:len(self.expected_version)]==self.expected_version:
			return fd,version,True
		print ('version check failed',len(version),version)
		return None,'',False

	def switchBaud(self,fd,portname):
		'''
		Change the BAUD rate to 500K if a raspberry pi is the base system
		'''

		if platform.system()!="Windows":   #Do this check only on Unix
			brgval = ((64000000/self.RPIBAUD)/4)-1
			if 'raspberrypi' in os.uname():
				#print ('RPi detected . switching to %d BAUD'%self.RPIBAUD,brgval)
				self.ARM = True
				fd.write(CP.SETBAUD)
				fd.write(chr(brgval))
				fd = serial.Serial(portname, self.RPIBAUD, stopbits=1, timeout = 0.3)
				fd.read(20)
				if(fd.inWaiting()):
					fd.setTimeout(0.1)
					fd.read(1000)
					fd.flush()
				fd.setTimeout(1.0)
		return fd

	def disconnect(self):
		if self.connected:
			self.fd.close()
		if self.blockingSocket:
			self.blockingSocket.shutdown(1)
			self.blockingSocket.close()
			self.blockingSocket = None

	def get_version(self,fd):
		fd.write(CP.COMMON)
		fd.write(CP.GET_VERSION)
		x=fd.readline()
		#print('remaining',[ord(a) for a in x+fd.read(10)])
		if len(x)>2:#remove newline character
			x=x[:-1]
		self.status = 0#ord(x[-1]) #last byte represents included features such as NRF, HX711 etc
		return x[:-1]

	def reconnect(self,**kwargs):
		if 'port' in kwargs:
			self.portname=kwargs.get('port',None)

		try:
			self.fd,self.version_string,self.connected=self.connectToPort(self.portname)
		except serial.SerialException as ex:
			msg = "failed to reconnect. Check device connections."
			raise RuntimeError(msg)

	def __del__(self):
		#print('closing port')
		try:self.fd.close()
		except: pass

	def __get_ack__(self):
		"""
		fetches the response byte
		1 SUCCESS
		2 ARGUMENT_ERROR
		3 FAILED
		used as a handshake
		"""
		if not self.loadBurst:
			x=self.fd.read(1)
		else:
			self.inputQueueSize+=1
			return 1
		try:
			val = CP.Byte.unpack(x)[0]
			if val&0x3!= 1: #Success = 1, err = 2
				self.cleanup_buffer()
				return 0
			else:
				return int(val)
		except:
			self.cleanup_buffer()
			return 0

	def cleanup_buffer(self,fd=None):
		if fd is None: fd = self.fd
		if(fd.in_waiting):
			fd.reset_input_buffer()
			fd.timeout=0.1
			fd.read(1000)
			fd.flush()
			fd.timeout=1.0

	def __sendInt__(self,val):
		"""
		transmits an integer packaged as two characters
		:params int val: int to send
		"""
		if not self.loadBurst:self.fd.write(CP.ShortInt.pack(int(val)))
		else: self.burstBuffer+=CP.ShortInt.pack(int(val))

	def __sendByte__(self,val):
		"""
		transmits a BYTE
		val - byte to send
		"""
		#print (val)
		if(type(val)==int):
			if not self.loadBurst:self.fd.write(CP.Byte.pack(val))
			else:self.burstBuffer+=CP.Byte.pack(val)
		else:
			if not self.loadBurst:self.fd.write(val)
			else:self.burstBuffer+=val
			
	def __getByte__(self):
		"""
		reads a byte from the serial port and returns it
		"""
		ss=self.fd.read(1)
		if len(ss): return CP.Byte.unpack(ss)[0]
		else:
			print('byte communication error.',time.ctime())
			self.raiseException("Communication Error , Function : "+inspect.currentframe().f_code.co_name)
			#sys.exit(1)

	def __getInt__(self):
		"""
		reads two bytes from the serial port and
		returns an integer after combining them
		"""
		ss = self.fd.read(2)
		if len(ss)==2: return CP.ShortInt.unpack(ss)[0]
		else:
			print('int communication error.',time.ctime())
			self.raiseException("Communication Error , Function : "+inspect.currentframe().f_code.co_name)
			#sys.exit(1)

	def __getLong__(self):
		"""
		reads four bytes.
		returns long
		"""
		ss = self.fd.read(4)
		if len(ss)==4: return CP.Integer.unpack(ss)[0]
		else:
			#print('.')
			return -1

	def waitForData(self,timeout=0.2):
		start_time = time.time()
		while (time.time()-start_time)<timeout:
			if self.fd.inWaiting():return True
		return False


	def sendBurst(self):
		"""
		Transmits the commands stored in the burstBuffer.
		empties input buffer
		empties the burstBuffer.
		
		The following example initiates the capture routine and sets OD1 HIGH immediately.
		
		It is used by the Transient response experiment where the input needs to be toggled soon
		after the oscilloscope has been started.
		
		>>> I.loadBurst=True
		>>> I.capture_traces(4,800,2)
		>>> I.set_state(I.OD1,I.HIGH)
		>>> I.sendBurst()
		"""

		#print([Byte.unpack(a)[0] for a in self.burstBuffer],self.inputQueueSize)
		self.fd.write(self.burstBuffer)
		self.burstBuffer=''
		self.loadBurst=False
		acks=self.fd.read(self.inputQueueSize)
		self.inputQueueSize=0
		return [Byte.unpack(a)[0] for a in acks]

	def raiseException(self,ex):
			raise RuntimeError(ex)

				
