# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
from __future__ import print_function
import time

from . import commands_proto as CP
import serial, os, inspect, platform
import socket, queue, threading


class ByteBuffer:
	def __init__(self, max_size):
		self.buffer = bytearray(max_size)
		self.size = 0
		self.lock = threading.Lock()

	def put_data(self, data):
		with self.lock:
			data_size = len(data)
			if self.size + data_size > len(self.buffer):
				# Buffer overflow, handle accordingly (e.g., discard or resize)
				print("Buffer overflow: Discarding data.")
				return

			self.buffer[self.size:self.size + data_size] = data
			self.size += data_size

	def get_size(self):
		return self.size
	def clear(self):
		self.size=0
	def read(self, n):
		with self.lock:
			n = min(n, self.size)
			data = bytes(self.buffer[:n])
			self.buffer[:self.size - n] = self.buffer[n:self.size]
			self.size -= n
			return data

	def hasline(self):
		return b'\n' in self.buffer

	def readline(self):
		with self.lock:
			if self.hasline():
				data = bytes(self.buffer.split(b'\n')[0])
				#n = len(data)
				#self.buffer[:self.size - n] = self.buffer[n:self.size]
				#self.size -= n

				#self.buffer.clear()
				self.size = 0
				return data


class WifiComms():
	timeout = 1.
	in_waiting = False

	def __init__(self, ip, port):
		server_address = (ip, port)
		self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.client_socket.connect(server_address)
		print(f"Connected to {server_address}")
		# self.client_socket.setblocking(0)

		# Create a byte buffer with a maximum size
		max_buffer_size = 1000  # Adjust as needed
		self.data_buffer = ByteBuffer(max_buffer_size)

		# Create a thread to receive data
		receive_thread = threading.Thread(target=self.receive_data, args=(self.client_socket, self.data_buffer))
		receive_thread.start()

	def receive_data(self, sock, buffer):
		while True:
			data, addr = sock.recvfrom(1024)
			if len(data):
				buffer.put_data(data)
				#print(data, buffer)

	def read(self, bytes):
		st = time.time()
		while (time.time() - st) < self.timeout:
			if self.data_buffer.get_size() >= bytes:
				#print(' available: ', self.data_buffer.get_size())
				return self.data_buffer.read(bytes)
		return b''

	def readline(self):
		st = time.time()
		while (time.time() - st) < self.timeout:
			if self.data_buffer.hasline():
				return self.data_buffer.readline()
		#print('read line failed', self.data_buffer, time.time() - st)
		return b''

	def write(self, data):
		#print('writing to IP', data)
		self.data_buffer.clear()
		# self.data_buffer=b''
		self.client_socket.sendall(data)

	def inWaiting(self):
		return False

	def setTimeout(self, t):
		return
	# self.timeout = t


class Handler():
	def __init__(self, timeout=1.0, **kwargs):
		self.burstBuffer = b''
		self.loadBurst = False
		self.inputQueueSize = 0
		self.BAUD = 500000
		self.RPIBAUD = 500000
		self.timeout = timeout
		self.version_string = b''
		self.connected = False
		self.fd = None
		self.status = 0
		self.expected_version = b'SJ'
		self.occupiedPorts = set()
		self.blockingSocket = None
		self.ARM = False
		self.portname = ''
		self.fd, self.version_string, self.connected = self.connectToPort(kwargs.get('ip'), kwargs.get('port', 8080))

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
					s = serial.Serial('COM' + str(i))
					available.append('COM' + str(i))
					s.close()
				except serial.SerialException:
					pass
			return available
		elif system_name == "Darwin":
			# Mac
			return glob.glob('/dev/tty.usb*') + glob.glob('/dev/cu*')
		else:
			# Assume Linux or something else
			return glob.glob('/dev/ttyACM*') + glob.glob('/dev/ttyUSB*')

	def connectToPort(self, ip, port):
		'''
        connect to a port, and check for the right version
        '''
		fd = WifiComms(ip, port)
		version = self.get_version(fd)
		if version[:len(self.expected_version)] == self.expected_version:
			return fd, version, True
		print('version check failed', len(version), version)
		return None, '', False

	def switchBaud(self, fd, portname):
		'''
        Change the BAUD rate to 500K if a raspberry pi is the base system
        '''

		if platform.system() != "Windows":  # Do this check only on Unix
			brgval = ((64000000 / self.RPIBAUD) / 4) - 1
			if 'raspberrypi' in os.uname():
				# print ('RPi detected . switching to %d BAUD'%self.RPIBAUD,brgval)
				self.ARM = True
				fd.write(CP.SETBAUD)
				fd.write(chr(brgval))
				fd = serial.Serial(portname, self.RPIBAUD, stopbits=1, timeout=0.3)
				fd.read(20)
				if (fd.inWaiting()):
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

	def get_version(self, fd):
		fd.write(CP.COMMON)
		fd.write(CP.GET_VERSION)
		x = fd.readline()
		# print('remaining',[ord(a) for a in x+fd.read(10)])
		if len(x) > 2:  # remove newline character
			x = x[:-1]
		self.status = 0  # ord(x[-1]) #last byte represents included features such as NRF, HX711 etc
		return x[:-1]

	def reconnect(self, **kwargs):
		if 'port' in kwargs:
			self.portname = kwargs.get('port', None)

		try:
			self.fd, self.version_string, self.connected = self.connectToPort(self.portname)
		except serial.SerialException as ex:
			msg = "failed to reconnect. Check device connections."
			raise RuntimeError(msg)

	def __del__(self):
		# print('closing port')
		try:
			self.fd.close()
		except:
			pass

	def __get_ack__(self):
		"""
        fetches the response byte
        1 SUCCESS
        2 ARGUMENT_ERROR
        3 FAILED
        used as a handshake
        """
		if not self.loadBurst:
			x = self.fd.read(1)
		else:
			self.inputQueueSize += 1
			return 1
		try:
			val = CP.Byte.unpack(x)[0]
			if val & 0x3 != 1:  # Success = 1, err = 2
				self.cleanup_buffer()
				return 0
			else:
				return int(val)
		except:
			self.cleanup_buffer()
			return 0

	def cleanup_buffer(self, fd=None):
		if fd is None: fd = self.fd
		if (fd.in_waiting):
			fd.reset_input_buffer()
			fd.timeout = 0.1
			fd.read(1000)
			fd.flush()
			fd.timeout = 1.0

	def __sendInt__(self, val):
		"""
        transmits an integer packaged as two characters
        :params int val: int to send
        """
		if not self.loadBurst:
			self.fd.write(CP.ShortInt.pack(int(val)))
		else:
			self.burstBuffer += CP.ShortInt.pack(int(val))

	def __sendByte__(self, val):
		"""
        transmits a BYTE
        val - byte to send
        """
		# print (val)
		if (type(val) == int):
			if not self.loadBurst:
				self.fd.write(CP.Byte.pack(val))
			else:
				self.burstBuffer += CP.Byte.pack(val)
		else:
			if not self.loadBurst:
				self.fd.write(val)
			else:
				self.burstBuffer += val

	def __getByte__(self):
		"""
        reads a byte from the serial port and returns it
        """
		ss = self.fd.read(1)
		if len(ss):
			return CP.Byte.unpack(ss)[0]
		else:
			print('byte communication error.', time.ctime())
			self.raiseException("Communication Error , Function : " + inspect.currentframe().f_code.co_name)

	# sys.exit(1)

	def __getInt__(self):
		"""
        reads two bytes from the serial port and
        returns an integer after combining them
        """
		ss = self.fd.read(2)
		if len(ss) == 2:
			return CP.ShortInt.unpack(ss)[0]
		else:
			print('int communication error.', len(ss))

	# sys.exit(1)

	def __getLong__(self):
		"""
        reads four bytes.
        returns long
        """
		ss = self.fd.read(4)
		if len(ss) == 4:
			return CP.Integer.unpack(ss)[0]
		else:
			# print('.')
			return -1

	def waitForData(self, timeout=0.2):
		start_time = time.time()
		while (time.time() - start_time) < timeout:
			if self.fd.inWaiting(): return True
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

		# print([Byte.unpack(a)[0] for a in self.burstBuffer],self.inputQueueSize)
		self.fd.write(self.burstBuffer)
		self.burstBuffer = ''
		self.loadBurst = False
		acks = self.fd.read(self.inputQueueSize)
		self.inputQueueSize = 0
		return [CP.Byte.unpack(a)[0] for a in acks]

	def raiseException(self, ex):
		print(ex)
