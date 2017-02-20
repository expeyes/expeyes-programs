import struct,time
import numpy as np
Byte =     struct.Struct("B") # size 1
ShortInt = struct.Struct("H") # size 2
Integer=   struct.Struct("I") # size 4


class NRF24L01():
	"""
	Access the onboard wireless transceiver
	
	.. code-block:: python

		from SEEL import interface
		I = interface.connect()

		I.NRF.get_status()  #Returns a byte containing the value of the STATUS register of the transceiver
		I.NRF.start_token_manager() # Start listening to any IoT nodes broadcasting their presence. Whenever a node is switched on, it transmits its address on a common address to anyone who may be listening
		while I.NRF.total_tokens()<2:  #Switch on a minimum of 2 of nodes now
			time.sleep(0.1)   
		I.NRF.stop_token_manager()  #stop listening. we've received information about two ready nodes.
		list = I.NRF.get_nodelist() #returns a dict object wherein the keys are node addresses, and values are lists of I2C sensors connected on the respective nodes
		print list
		>>> {0x01010A:[58],0x01010B:[96,58]}  #two nodes detected . One has 1 sensor attached, and another has 2
		
	"""


	NRFL01                  = Byte.pack(13)
	NRF_SETUP               = Byte.pack(1)
	NRF_RXMODE              = Byte.pack(2)
	NRF_TXMODE              = Byte.pack(3)
	NRF_POWER_DOWN          = Byte.pack(4)
	NRF_RXCHAR              = Byte.pack(5)
	NRF_TXCHAR              = Byte.pack(6)
	NRF_HASDATA             = Byte.pack(7)
	NRF_FLUSH               = Byte.pack(8)
	NRF_WRITEREG            = Byte.pack(9)
	NRF_READREG             = Byte.pack(10)
	NRF_GETSTATUS           = Byte.pack(11)
	NRF_WRITECOMMAND        = Byte.pack(12)
	NRF_WRITEPAYLOAD        = Byte.pack(13)
	NRF_READPAYLOAD         = Byte.pack(14)
	NRF_WRITEADDRESS        = Byte.pack(15)
	NRF_TRANSACTION         = Byte.pack(16)
	NRF_START_TOKEN_MANAGER = Byte.pack(17)
	NRF_STOP_TOKEN_MANAGER  = Byte.pack(18)
	NRF_TOTAL_TOKENS        = Byte.pack(19)
	NRF_REPORTS             = Byte.pack(20)
	NRF_WRITE_REPORT        = Byte.pack(21)
	NRF_DELETE_REPORT_ROW   = Byte.pack(22)

	NRF_WRITEADDRESSES      = Byte.pack(23)

	#Commands
	R_REG = 0x00
	W_REG = 0x20
	RX_PAYLOAD = 0x61
	TX_PAYLOAD = 0xA0
	ACK_PAYLOAD = 0xA8
	FLUSH_TX = 0xE1
	FLUSH_RX = 0xE2
	ACTIVATE = 0x50
	R_STATUS = 0xFF

	#Registers
	NRF_CONFIG = 0x00
	EN_AA = 0x01
	EN_RXADDR = 0x02
	SETUP_AW = 0x03
	SETUP_RETR = 0x04
	RF_CH = 0x05
	RF_SETUP = 0x06
	NRF_STATUS = 0x07
	OBSERVE_TX = 0x08
	CD = 0x09
	RX_ADDR_P0 = 0x0A
	RX_ADDR_P1 = 0x0B
	RX_ADDR_P2 = 0x0C
	RX_ADDR_P3 = 0x0D
	RX_ADDR_P4 = 0x0E
	RX_ADDR_P5 = 0x0F
	TX_ADDR = 0x10
	RX_PW_P0 = 0x11
	RX_PW_P1 = 0x12
	RX_PW_P2 = 0x13
	RX_PW_P3 = 0x14
	RX_PW_P4 = 0x15
	RX_PW_P5 = 0x16
	R_RX_PL_WID = 0x60
	FIFO_STATUS = 0x17
	DYNPD = 0x1C
	FEATURE = 0x1D
	PAYLOAD_SIZE = 0
	ACK_PAYLOAD_SIZE =0
	READ_PAYLOAD_SIZE =0

	NRF_COMMANDS = 3
	NRF_READ_REGISTER =0
	NRF_WRITE_REGISTER =1<<4

	#Valid for broadcast mode
	ALL_BLINK = 1
	ALL_BLINKY = 0
	ALL_BROADCAST = 1

	MISC_COMMANDS = 4  
	WS2812B_CMD  = 0
	SET_DAC = 4
	SET_IO = 6


	CURRENT_ADDRESS=0xAAAA01
	BROADCAST_ADDRESS = 0x111111
	nodelist={}
	nodepos=0
	NODELIST_MAXLENGTH=15
	connected=False
	def __init__(self,H):
		self.H = H
		self.ready=False
		self.sigs={self.CURRENT_ADDRESS:1}
		if self.H.connected:
				self.connected=self.init()

	def init(self):
		try:
			self.H.__sendByte__(self.NRFL01)
			self.H.__sendByte__(self.NRF_SETUP)
			self.H.__get_ack__()
			time.sleep(0.015) #15 mS settling time
			stat = self.get_status()
			if stat & 0x80 or stat==0:
				print ("Radio transceiver not installed/not found")
				return False
			else:
				self.ready=True
			self.selectAddress(self.CURRENT_ADDRESS)
			self.rxmode()
			time.sleep(0.01)
			self.flush()
			return True
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)
		
	def rxmode(self):
		'''
		Puts the radio into listening mode.
		'''
		try:
			self.H.__sendByte__(self.NRFL01)
			self.H.__sendByte__(self.NRF_RXMODE)
			self.H.__get_ack__()
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)
		
	def txmode(self):
		'''
		Puts the radio into transmit mode.
		'''
		try:
			self.H.__sendByte__(self.NRFL01)
			self.H.__sendByte__(self.NRF_TXMODE)
			self.H.__get_ack__()
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def triggerAll(self,val):
		self.txmode()
		self.selectAddress(0x111111)
		self.write_register(self.EN_AA,0x00)
		self.write_payload([val],True)
		self.write_register(self.EN_AA,0x01)
		
	def power_down(self):
		try:
			self.H.__sendByte__(self.NRFL01)
			self.H.__sendByte__(self.NRF_POWER_DOWN)
			self.H.__get_ack__()
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)
		
	def rxchar(self):
		'''
		Receives a 1 Byte payload
		'''
		try:
			self.H.__sendByte__(self.NRFL01)
			self.H.__sendByte__(self.NRF_RXCHAR)
			value = self.H.__getByte__()
			self.H.__get_ack__()
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)
		return value
		
	def txchar(self,char):
		'''
		Transmits a single character
		'''
		try:
			self.H.__sendByte__(self.NRFL01)
			self.H.__sendByte__(self.NRF_TXCHAR)
			self.H.__sendByte__(char)
			return self.H.__get_ack__()>>4
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)
		
	def hasData(self):
		'''
		Check if the RX FIFO contains data
		'''
		try:
			self.H.__sendByte__(self.NRFL01)
			self.H.__sendByte__(self.NRF_HASDATA)
			value = self.H.__getByte__()
			self.H.__get_ack__()
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)
		return value
		
	def flush(self):
		'''
		Flushes the TX and RX FIFOs
		'''
		try:
			self.H.__sendByte__(self.NRFL01)
			self.H.__sendByte__(self.NRF_FLUSH)
			self.H.__get_ack__()
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def write_register(self,address,value):
		'''
		write a  byte to any of the configuration registers on the Radio.
		address byte can either be located in the NRF24L01+ manual, or chosen
		from some of the constants defined in this module.
		'''
		#print ('writing',address,value)
		try:
			self.H.__sendByte__(self.NRFL01)
			self.H.__sendByte__(self.NRF_WRITEREG)
			self.H.__sendByte__(address)
			self.H.__sendByte__(value)
			self.H.__get_ack__()
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def read_register(self,address):
		'''
		Read the value of any of the configuration registers on the radio module.
		
		'''
		try:
			self.H.__sendByte__(self.NRFL01)
			self.H.__sendByte__(self.NRF_READREG)
			self.H.__sendByte__(address)
			val=self.H.__getByte__()
			self.H.__get_ack__()
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)
		return val

	def get_status(self):
		'''
		Returns a byte representing the STATUS register on the radio.
		Refer to NRF24L01+ documentation for further details
		'''
		try:
			self.H.__sendByte__(self.NRFL01)
			self.H.__sendByte__(self.NRF_GETSTATUS)
			val=self.H.__getByte__()
			self.H.__get_ack__()
			return val
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def write_command(self,cmd):
		try:
			self.H.__sendByte__(self.NRFL01)
			self.H.__sendByte__(self.NRF_WRITECOMMAND)
			self.H.__sendByte__(cmd)
			self.H.__get_ack__()
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def write_address(self,register,address):
		'''
		register can be TX_ADDR, RX_ADDR_P0 -> RX_ADDR_P5
		3 byte address.  eg 0xFFABXX . XX cannot be FF
		if RX_ADDR_P1 needs to be used along with any of the pipes
		from P2 to P5, then RX_ADDR_P1 must be updated last.
		Addresses from P1-P5 must share the first two bytes.
		'''
		try:
			self.H.__sendByte__(self.NRFL01)
			self.H.__sendByte__(self.NRF_WRITEADDRESS)
			self.H.__sendByte__(register)
			self.H.__sendByte__(address&0xFF);self.H.__sendByte__((address>>8)&0xFF);
			self.H.__sendByte__((address>>16)&0xFF);
			self.H.__get_ack__()
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def selectAddress(self,address):
		'''
		Sets RX_ADDR_P0 and TX_ADDR to the specified address.
		
		'''
		try:
			self.H.__sendByte__(self.NRFL01)
			self.H.__sendByte__(self.NRF_WRITEADDRESSES)
			self.H.__sendByte__(address&0xFF);self.H.__sendByte__((address>>8)&0xFF);
			self.H.__sendByte__((address>>16)&0xFF);
			self.H.__get_ack__()
			self.CURRENT_ADDRESS=address
			if address not in self.sigs:
				self.sigs[address]=1
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)
		
	def read_payload(self,numbytes):
		try:
			self.H.__sendByte__(self.NRFL01)
			self.H.__sendByte__(self.NRF_READPAYLOAD)
			self.H.__sendByte__(numbytes)
			data=self.H.fd.read(numbytes)
			self.H.__get_ack__()
			return [ord(a) for a in data]
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def write_payload(self,data,verbose=False,**args): 
		try:
			self.H.__sendByte__(self.NRFL01)
			self.H.__sendByte__(self.NRF_WRITEPAYLOAD)
			numbytes=len(data)|0x80   #0x80 implies transmit immediately. Otherwise it will simply load the TX FIFO ( used by ACK_payload)
			if(args.get('rxmode',False)):numbytes|=0x40
			self.H.__sendByte__(numbytes)
			self.H.__sendByte__(self.TX_PAYLOAD)
			for a in data:
				self.H.__sendByte__(a)
			val=self.H.__get_ack__()>>4
			if(verbose):
				if val&0x2: print (' NRF radio not found. Connect one to the add-on port')
				elif val&0x1: print (' Node probably dead/out of range. It failed to acknowledge')
				return
			return val
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def transaction(self,data,**args):
		st = time.time()
		try:
			timeout = args.get('timeout',200)
			verbose = args.get('verbose',False)

			#print ('#################',args)
			if args.get('listen',True):data[0]|=0x80  # You need this if hardware must wait for a reply

			self.H.__sendByte__(self.NRFL01)
			self.H.__sendByte__(self.NRF_TRANSACTION)
			self.H.__sendByte__(len(data)) #total Data bytes coming through
			self.H.__sendInt__(timeout) #timeout.  		
			for a in data:
				self.H.__sendByte__(a)
			self.H.waitForData(timeout/1.e4+0.2) #convert to mS
			numbytes=self.H.__getByte__()
			if numbytes: data = [ord(a) for a in self.H.fd.read(numbytes)]
			else: data=[]
			val=self.H.__get_ack__()>>4
			
			#print ('dt send',time.time()-st,timeout,data,str(bin(val)))
			
			if(verbose):
				if val&0x1: print (time.time(),'%s Err. Node not found'%(hex(self.CURRENT_ADDRESS)))
				if val&0x2: print (time.time(),'%s Err. NRF on-board transmitter not found'%(hex(self.CURRENT_ADDRESS)))
				if val&0x4 and args.get('listen',True): print (time.time(),'%s Err. Node received command but did not reply'%(hex(self.CURRENT_ADDRESS)))
			if val&0x7:	#Something didn't go right.
				self.flush()
				self.sigs[self.CURRENT_ADDRESS] = self.sigs[self.CURRENT_ADDRESS]*50/51.
				return False
			
			self.sigs[self.CURRENT_ADDRESS] = (self.sigs[self.CURRENT_ADDRESS]*50+1)/51.
			return data
		except Exception as ex:
			print('Exception:',ex)

	def transactionWithRetries(self,data,**args):
		retries = args.get('retries',5)
		reply=False
		while retries>0:
			reply = self.transaction(data,verbose=(retries==1),**args)
			if reply:
				break
			retries-=1
		return reply

	def write_ack_payload(self,data,pipe): 
		if(len(data)!=self.ACK_PAYLOAD_SIZE):
			self.ACK_PAYLOAD_SIZE=len(data)
			if self.ACK_PAYLOAD_SIZE>15:
				print ('too large. truncating.')
				self.ACK_PAYLOAD_SIZE=15
				data=data[:15]
			else:
				print ('ack payload size:',self.ACK_PAYLOAD_SIZE)
		try:
			self.H.__sendByte__(self.NRFL01)
			self.H.__sendByte__(self.NRF_WRITEPAYLOAD)
			self.H.__sendByte__(len(data))
			self.H.__sendByte__(self.ACK_PAYLOAD|pipe)
			for a in data:
				self.H.__sendByte__(a)
			return self.H.__get_ack__()>>4
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def start_token_manager(self):
		'''
		'''
		try:
			self.H.__sendByte__(self.NRFL01)
			self.H.__sendByte__(self.NRF_START_TOKEN_MANAGER)
			self.H.__get_ack__()
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def stop_token_manager(self):
		'''
		'''
		try:
			self.H.__sendByte__(self.NRFL01)
			self.H.__sendByte__(self.NRF_STOP_TOKEN_MANAGER)
			self.H.__get_ack__()
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def total_tokens(self):
		'''
		'''
		try:
			self.H.__sendByte__(self.NRFL01)
			self.H.__sendByte__(self.NRF_TOTAL_TOKENS)
			x = self.H.__getByte__()
			self.H.__get_ack__()
			return x
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def fetch_report(self,num):
		'''
		'''
		try:
			self.H.__sendByte__(self.NRFL01)
			self.H.__sendByte__(self.NRF_REPORTS)
			self.H.__sendByte__(num)
			data = [self.H.__getByte__() for a in range(20)]
			self.H.__get_ack__()
			return data
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)

	def __decode_I2C_list__(self,data):
		lst=[]
		if sum(data)==0:
			return lst
		for a in range(len(data)):
			if(data[a]^255):
				for b in range(8):
					if data[a]&(0x80>>b)==0:
						addr = 8*a+b
						lst.append(addr)
		return lst
		
	def get_nodelist(self,check_alive = False):
		'''
		Refer to the variable 'nodelist' if you simply want a list of nodes that either registered while your code was
		running , or were loaded from the firmware buffer(max 15 entries)

		If you plan to use more than 15 nodes, and wish to register their addresses without having to feed them manually,
		then this function must be called each time before the buffer resets (every fifteen nodes).
		
		The dictionary object returned by this function is filtered by checking with each node if they are alive first.
		
		:return: {address_Node1:[[registered sensors(I2C Addresses 0-8 are not auto detected)],battery%],address_Node2:[[registered sensors],battery%] ... }
		
		'''
		total = self.total_tokens()
		total+=1
		if total==self.NODELIST_MAXLENGTH:total=0
		
		if self.nodepos!=total:
			#print ('pos = ',self.nodepos)
			for nm in range(self.nodepos,self.NODELIST_MAXLENGTH)+range(0,self.nodepos):
				dat = self.fetch_report(nm)
				#print (nm,dat)
				txrx=(dat[0])|(dat[1]<<8)|(dat[2]<<16)
				if not txrx:
					continue
				self.nodelist[txrx]=[self.__decode_I2C_list__(dat[3:19]),min(100,int(dat[19]*100./93))]
			self.nodepos=total
			#else:
			#	self.__delete_registered_node__(nm)

		filtered_lst={}
		for a in self.nodelist:
			if check_alive:
				if self.isAlive(a):
					filtered_lst[a]=self.nodelist[a]
					#print (self.nodelist[a][1])			
			else:
				filtered_lst[a]=self.nodelist[a]
		return filtered_lst

	def __delete_registered_node__(self,num):
		try:
			self.H.__sendByte__(self.NRFL01)
			self.H.__sendByte__(self.NRF_DELETE_REPORT_ROW)
			self.H.__sendByte__(num)
			self.H.__get_ack__()
		except Exception as ex:
			self.raiseException(ex, "Communication Error , Function : "+inspect.currentframe().f_code.co_name)
		
	def __delete_all_registered_nodes__(self):
			while self.total_tokens():
				print ('-')
				self.__delete_registered_node__(0)

	def isAlive(self,addr):
		self.selectAddress(addr)
		return self.transaction([self.NRF_COMMANDS,self.NRF_READ_REGISTER]+[self.R_STATUS],timeout=500,verbose=False)

	def init_shockburst_transmitter(self,**args):
		'''
		Puts the radio into transmit mode.
		Dynamic Payload with auto acknowledge is enabled.
		upto 5 retransmits with 1ms delay between each in case a node doesn't respond in time
		Receivers must acknowledge payloads
		'''
		self.PAYLOAD_SIZE=args.get('PAYLOAD_SIZE',self.PAYLOAD_SIZE)
		myaddr=args.get('myaddr',0xAAAA01)
		sendaddr=args.get('sendaddr',0xAAAA01)

		self.init()
		#shockburst
		self.write_address(self.RX_ADDR_P0,myaddr)	#transmitter's address
		self.write_address(self.TX_ADDR,sendaddr)     #send to node with this address
		self.write_register(self.RX_PW_P0,self.PAYLOAD_SIZE) 
		self.rxmode()
		time.sleep(0.1)
		self.flush()

	def init_shockburst_receiver(self,**args):
		'''
		Puts the radio into receive mode.
		Dynamic Payload with auto acknowledge is enabled.
		'''
		self.PAYLOAD_SIZE=args.get('PAYLOAD_SIZE',self.PAYLOAD_SIZE)
		if 'myaddr0' not in args:
			args['myaddr0']=0xA523B5
		#if 'sendaddr' non in args:
		#	args['sendaddr']=0xA523B5
		print (args)
		self.init()
		self.write_register(self.RF_SETUP,0x26)  #2MBPS speed

		#self.write_address(self.TX_ADDR,sendaddr)     #send to node with this address
		#self.write_address(self.RX_ADDR_P0,myaddr)	#will receive the ACK Payload from that node
		enabled_pipes = 0				#pipes to be enabled
		for a in range(0,6):
			x=args.get('myaddr'+str(a),None)
			if x: 
				print (hex(x),hex(self.RX_ADDR_P0+a))
				enabled_pipes|= (1<<a)
				self.write_address(self.RX_ADDR_P0+a,x)
		P15_base_address = args.get('myaddr1',None)
		if P15_base_address: self.write_address(self.RX_ADDR_P1,P15_base_address)

		self.write_register(self.EN_RXADDR,enabled_pipes) #enable pipes
		self.write_register(self.EN_AA,enabled_pipes) #enable auto Acknowledge on all pipes
		self.write_register(self.DYNPD,enabled_pipes) #enable dynamic payload on Data pipes
		self.write_register(self.FEATURE,0x06) #enable dynamic payload length
		#self.write_register(self.RX_PW_P0,self.PAYLOAD_SIZE)

		self.rxmode()
		time.sleep(0.1)
		self.flush()

	def __selectBroadcast__(self):
		if self.CURRENT_ADDRESS!=self.BROADCAST_ADDRESS:
			self.selectAddress(self.BROADCAST_ADDRESS)

	def broadcastBlink(self,number_of_blinks):
		'''
		initiates a blink sequence on all nearby nodes
		'''
		self.__selectBroadcast__()
		return self.transaction([self.ALL_BLINK,self.ALL_BLINKY,number_of_blinks],listen = False)

	def broadcastPing(self):
		'''
		Ping all nodes in the vicinity. All powered up nodes will respond with sensor and battery data
		'''
		self.__selectBroadcast__()
		val = self.transaction([self.ALL_BLINK,self.ALL_BROADCAST],listen = False)
		time.sleep(0.1)

	#Miscellaneous features
	def WS2812B(self,cols):
		"""
		set shade of WS2182 LED on CS1/RC0 for all devices in the vicinity
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  ============================================================================================
		**Arguments** 
		==============  ============================================================================================
		cols                2Darray [[R,G,B],[R2,G2,B2],[R3,G3,B3]...]
							brightness of R,G,B ( 0-255  )
		==============  ============================================================================================

		example::
		
			>>> WS2812B([[10,0,0],[0,10,10],[10,0,10]])
			#sets red, cyan, magenta to three daisy chained LEDs

		"""
		self.__selectBroadcast__()
		colarray=[]
		for a in cols:
			colarray.append(int('{:08b}'.format(int(a[1]))[::-1], 2))
			colarray.append(int('{:08b}'.format(int(a[0]))[::-1], 2))
			colarray.append(int('{:08b}'.format(int(a[2]))[::-1], 2))

		res = self.transaction([self.MISC_COMMANDS,self.WS2812B_CMD]+colarray,listen=False)
		return res



	def raiseException(self,ex, msg):
			msg += '\n' + ex.message
			#self.H.disconnect()
			raise RuntimeError(msg)


class RadioLink():
	'''
	A simplified wrapper for interacting with IoT Nodes.
	
	.. tabularcolumns:: |p{3cm}|p{11cm}|
	
	
	==============  ============================================================================================
	**Arguments**   Description
	==============  ============================================================================================
	NRF             ~interface.NRF instance 
	*\*\args
	address         3-byte address of the node. e.g 0x01010A
	==============  ============================================================================================		
	
	Example for connecting to a wireless node, and setting the color of its on-board neopixel. Also scan the I2C bus
	
	.. code-block:: python
	
		link = I.newRadioLink(address = 0x01010A)   #This address is unique for each IoT node, and is printed on it
		link.WS2812B([[0,255,255]])  #Set the colour of the onboard RGB LED to cyan
		print link.I2C_scan()        #Scan the I2C bus of the IoT node, and return detected addresses
		>>> [58]
		
	Example for connecting to a wireless node, and reading the values from a magnetometer connected to its I2C port
	
	.. code-block:: python
	
		link = I.newRadioLink(address = 0x01010A)   #This address is unique for each IoT node, and is printed on it
		from SEEL.SENSORS import HMC5883L
		mag = HMC5883L.connect(link)  # Tell the magnetometer's class to use the IoT node with address 0x01010A as the link to the magnetometer
		print mag.getRaw()
		>>> [0.01,126.3,24.0]  # magnetic fields along the x,y, and z axes of the sensor


		
	'''
	ADC_COMMANDS =1
	CAPTURE_ADC =0
	READ_ADC =1


	SPI_COMMANDS =6
	SPI_TRANSACTION =0

	I2C_COMMANDS =2
	I2C_TRANSACTION =0
	I2C_WRITE =1
	SCAN_I2C =2
	PULL_SCL_LOW = 3
	I2C_CONFIG = 4
	I2C_READ = 5

	NRF_COMMANDS = 3
	NRF_READ_REGISTER =0
	NRF_WRITE_REGISTER =1
	NRF_BLE = 2

	MISC_COMMANDS = 4
	WS2812B_CMD  = 0
	EEPROM_WRITE = 1
	EEPROM_READ  = 2
	RESET_DEVICE = 3
	SET_DAC = 4
	SET_DOZE = 5
	SET_IO = 6
	
	PWM_COMMANDS = 5
	SET_PWM      = 0
	GET_FREQ     = 1
	
	
	def __init__(self,NRF,**args):
		self.NRF = NRF
		if 'address' in args:
			self.ADDRESS = args.get('address',False)
		else:
			print ('Address not specified. Add "address=0x....." argument while instantiating')
			self.ADDRESS=0x010101
		self.adc_map = {
			'BAT':self.adc_chan(0b100,0,6.6),
			'CS3':self.adc_chan(0b10111,0,3.3),
			'FVR':self.adc_chan(0b111111,0,3.3),
			'DAC':self.adc_chan(0b111110,0,3.3),
			'TEMP':self.adc_chan(0b111101,0,3.3),
			'AVss':self.adc_chan(0b111100,0,3.3),
		}
		#self.write_register(self.NRF.SETUP_RETR,0x12)

	def __selectMe__(self):
		if self.NRF.CURRENT_ADDRESS!=self.ADDRESS:
			self.NRF.selectAddress(self.ADDRESS)

	#ADC Commands
	class adc_chan:
		def __init__(self,AN,minV,maxV):
			self.AN = AN
			self.minV = minV
			self.maxV = maxV
			self.poly = np.poly1d([0,(maxV-minV)/1023.,minV])
		def applyCal(self,code):
			return self.poly(code)

	def captureADC(self,channel):
		'''
		Read 16 bytes from the ADC
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		
		==============  ============================================================================================
		**Arguments**   Description
		==============  ============================================================================================
		channel         'BAT' , 'CS3'
		==============  ============================================================================================		
		
		'''
		self.__selectMe__()
		chan = self.adc_map.get(channel,None)
		if not chan:
			print ('channel not available')
			return False
		
		vals = self.NRF.transactionWithRetries([self.ADC_COMMANDS,self.CAPTURE_ADC]+[chan.AN],timeout=400)
		if vals:
			if len(vals)==32:
				intvals = []
				for a in range(16): intvals.append ( (vals[a*2]<<8)|vals[a*2+1]  )
				return chan.applyCal(intvals)
			else:
				print ('packet dropped')
				return False
		else:
			print ('packet dropped')
			return False

	def readADC(self,channel,verbose=False):
		'''
		Read bytes from the ADC
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		
		==============  ============================================================================================
		**Arguments**   Description
		==============  ============================================================================================
		channel         'BAT' , 'CS3'
		==============  ============================================================================================		
		
		'''
		self.__selectMe__()
		chan = self.adc_map.get(channel,None)
		if not chan:
			print ('channel not available')
			return False		
		vals = self.NRF.transactionWithRetries([self.ADC_COMMANDS,self.READ_ADC]+[chan.AN],timeout=400)
		if vals:
			if len(vals)==2:
				if verbose: print (vals)
				return chan.applyCal((vals[0]<<8)|vals[1])
			else:
				print ('packet dropped')
				return False
		else:
			print ('packet dropped')
			return False

	#I2C Commands
	def I2C_scan(self):
		'''
		Scans the I2C bus and returns a list of active addresses. 
		'''
		self.__selectMe__()
		import sensorlist
		print ('Scanning addresses 0-127...')
		x = self.NRF.transaction([self.I2C_COMMANDS,self.SCAN_I2C],timeout=500)
		if not x:return []
		if not sum(x):return []
		addrs=[]
		print ('Address','\t','Possible Devices')

		for a in range(16):
			if(x[a]^255):
				for b in range(8):
					if x[a]&(0x80>>b)==0:
						addr = 8*a+b
						addrs.append(addr)
						print (hex(addr),'\t\t',sensorlist.sensors.get(addr,'None'))
						
		return addrs

	def __decode_I2C_list__(self,data):
		lst=[]
		if sum(data)==0:
			return lst
		for a in range(len(data)):
			if(data[a]^255):
				for b in range(8):
					if data[a]&(0x80>>b)==0:
						addr = 8*a+b
						lst.append(addr)
		return lst

	def writeI2C(self,I2C_addr,regaddress,bytes):
		self.__selectMe__()
		return self.NRF.transaction([self.I2C_COMMANDS,self.I2C_WRITE]+[I2C_addr]+[regaddress]+bytes)
		
	def readI2C(self,I2C_addr,regaddress,numbytes):
		self.__selectMe__()
		return self.NRF.transaction([self.I2C_COMMANDS,self.I2C_TRANSACTION]+[I2C_addr]+[regaddress]+[numbytes])

	def writeBulk(self,I2C_addr,bytes):
		'''
		Write bytes to an I2C sensor
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		
		==============  ============================================================================================
		**Arguments**   Description
		==============  ============================================================================================
		I2C_addr        address of the I2C sensor
		bytes           an array of bytes to be written
		==============  ============================================================================================		
		
		'''
		self.__selectMe__()
		return self.NRF.transaction([self.I2C_COMMANDS,self.I2C_WRITE]+[I2C_addr]+bytes)
		
	def readBulk(self,I2C_addr,regaddress,numbytes):
		'''
		Read bytes from an I2C sensor
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		
		==============  ============================================================================================
		**Arguments**   Description
		==============  ============================================================================================
		I2C_addr        address of the I2C sensor
		regaddress      address of the register to read from
		numbytes        number of bytes to read
		==============  ============================================================================================		
		
		'''
		self.__selectMe__()
		return self.NRF.transactionWithRetries([self.I2C_COMMANDS,self.I2C_TRANSACTION]+[I2C_addr]+[regaddress]+[numbytes],timeout = 30)

	def simpleRead(self,I2C_addr,numbytes):
		self.__selectMe__()
		return self.NRF.transactionWithRetries([self.I2C_COMMANDS,self.I2C_READ]+[I2C_addr]+[numbytes])

	def pullSCLLow(self,t_ms):
		'''
		hold the SCL line low for a defined period. Used by sensors such as MLX90316
		
		
		'''
		self.__selectMe__()
		dat=self.NRF.transaction([self.I2C_COMMANDS,self.PULL_SCL_LOW]+[t_ms])
		if dat:
			return self.__decode_I2C_list__(dat)
		else:
			return []

	def configI2C(self,freq):
		'''
		Set the frequency of the I2C port on the wireless node.
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		
		==============  ============================================================================================
		**Arguments**   Description
		==============  ============================================================================================
		freq            Frequency
		==============  ============================================================================================		
		
		'''
		self.__selectMe__()
		brgval=int(32e6/freq/4 - 1)
		print (brgval)
		return self.NRF.transaction([self.I2C_COMMANDS,self.I2C_CONFIG]+[brgval],listen=False)

	#SPI commands
	def readSPI(self,chip_select,data):
		'''
		Accepts an array
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		
		==============  ============================================================================================
		**Arguments**   Description
		==============  ============================================================================================
		chip_select     'CS1' or 'CS2'
		data            array of elements to write to SDO while data is simultaneously clocked in via SDI
		==============  ============================================================================================		
		
		'''
		self.__selectMe__()
		if chip_select=='CS1':cs=1
		elif chip_select=='CS2':cs=2
		else:
			print ('invalid chip select')
			return
		return self.NRF.transactionWithRetries([self.SPI_COMMANDS,self.SPI_TRANSACTION,cs]+data)


	#NRF Commands
	def write_register(self,reg,val):
		self.__selectMe__()
		#print ('writing to ',reg,val)
		return self.NRF.transaction([self.NRF_COMMANDS,self.NRF_WRITE_REGISTER]+[reg,val],listen=False)

	def read_register(self,reg):
		self.__selectMe__()
		x=self.NRF.transaction([self.NRF_COMMANDS,self.NRF_READ_REGISTER]+[reg])
		if x:
			return x[0]
		else:
			return False
			
	#Miscellaneous features
	def WS2812B(self,cols):
		"""
		set shade of WS2182 LED on CS1/RC0
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  ============================================================================================
		**Arguments** 
		==============  ============================================================================================
		cols                2Darray [[R,G,B],[R2,G2,B2],[R3,G3,B3]...]
							brightness of R,G,B ( 0-255  )
		==============  ============================================================================================

		example::
		
			>>> WS2812B([[10,0,0],[0,10,10],[10,0,10]])
			#sets red, cyan, magenta to three daisy chained LEDs

		"""
		self.__selectMe__()
		colarray=[]
		for a in cols:
			colarray.append(int('{:08b}'.format(int(a[1]))[::-1], 2))
			colarray.append(int('{:08b}'.format(int(a[0]))[::-1], 2))
			colarray.append(int('{:08b}'.format(int(a[2]))[::-1], 2))

		res = self.NRF.transaction([self.MISC_COMMANDS,self.WS2812B_CMD]+colarray,listen=False)
		return res

	def reset(self):
		"""
		Reset the wireless node.
		If EEPROM locations 0,1,2 were updated, the node will restart at the new address
		"""

		self.__selectMe__()
		res = self.NRF.transactionWithRetries([self.MISC_COMMANDS,self.RESET_DEVICE],listen=False)
		return res

	def batteryLevel(self):
		"""
		Read the battery status, and return a percentage value.
		Do not operate at very low levels if running on a Lithium battery. It reduces their lifetime
		"""
		return max(min((self.readADC('BAT')-3.7)*200,100),0)

	def setDAC(self,val):
		"""
		Write to 5 bit DAC 
		0 < val < 3.3
		"""
		code = int(val*31/3.3)
		self.__selectMe__()
		res = self.NRF.transactionWithRetries([self.MISC_COMMANDS,self.SET_DAC,code],timeout=100)
		if res:return 3.3*res[0]/31
		else : return False

	def lowPowerMode(self,level = False):
		"""
		Reduce the CPU frequency of the node's processor
		Level  in [False, 1 ... 7 ] 
		"""
		self.__selectMe__()
		if level : self.NRF.transactionWithRetries([self.MISC_COMMANDS,self.SET_DOZE,(1<<6)|(level)],listen = False) #111 = 1/256 scaling
		else : self.NRF.transactionWithRetries([self.MISC_COMMANDS,self.SET_DOZE,0],listen = False)  #disable low power mode

	def setIO(self,**kwargs):
		"""
		Toggle CS1 or CS2 digital output. up to 5mA sink/source capacity
		These pins also serve as chip selects for SPI devices. If any of the
		chip selects are connected to an SPI device, toggling them can cause an SPI clash and
		will result in the node becoming unresponsive until a power reset.

		==============  ============================================================================================
		**Arguments** 
		==============  ============================================================================================
		*\*\kwargs      CS1 = 1/0
						CS2 = 1/0
		==============  ============================================================================================

		example::
		
			>>> link.setIO(CS1 = False, CS2 = True)  #Set CS1 to 0V , CS2 to 3.3V
			#sets red, cyan, magenta to three daisy chained LEDs
		"""
		io=0
		if 'CS1' in kwargs: io |= 1|(kwargs.get('CS1')<<4)
		if 'CS2' in kwargs: io |= 2|(kwargs.get('CS2')<<5)
		self.__selectMe__()
		if io: return self.NRF.transaction([self.MISC_COMMANDS,self.SET_IO,io],listen = False)  #disable low power mode
		else: return False

	def readFrequency(self,prescaler = 6):
		'''
		Read frequency of input TTL signal on CS3 (0-3.3V)
		
		Select a prescaler value that obtains maximum resolution for your measurement range.
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		Range = 250/(2**prescaler) - 8e6/(2**prescaler)
		
		==============  ============================================================================================
		**Prescaler**   **Frequency Range**
		==============  ============================================================================================
		2               62.5Hz to 2MHz
		3               31.25Hz to 1MHz
		4               16Hz  to 500KHz
		5               8Hz  to 250KHz
		6               4Hz  to 125KHz
		7               2Hz  to 62.5KHz
		==============  ============================================================================================		
		
		'''
		prescaler = min(7,max(2,prescaler)) # fix prescaler between 2 and 7
		self.__selectMe__()
		vals = self.NRF.transactionWithRetries([self.PWM_COMMANDS,self.GET_FREQ]+[(0b110<<4)|prescaler],timeout=int(min(max(30,40*2**prescaler),65000)) ) #0b110 = 4 edges . 0b111 = every 16 edges
		if vals:
			dcode = ((vals[2]<<8)|vals[3] ) - ((vals[0]<<8)|vals[1])
			dt = (2**prescaler)*( dcode )/8e6/4.  # prescale * counts /8e6/4
			if dcode<2:
				if prescaler<8 and dcode<0:print ('frequency too low . increase prescaler')			
				elif prescaler>0 and dcode<2:print ('frequency too high . decrease prescaler')			
				else: print ('frequency out of range')
				return False
			return 1./dt
		else:
			return False

	def readHighFrequency(self):
		'''
		Read frequencies between 10KHz and 8MHz from input TTL signal on CS3 (0-3.3V)
		'''
		self.__selectMe__()
		vals = self.NRF.transactionWithRetries([self.PWM_COMMANDS,self.GET_FREQ]+[(0b111<<4)],timeout=3000 ) # 0b111 = every 16 edges
		if vals:
			dcode = ((vals[2]<<8)|vals[3] ) - ((vals[0]<<8)|vals[1])
			dt = ( dcode )/8e6/16.  # prescale * counts /8e6/4
			if dcode<2:
				print ('frequency out of range')
				return False
			return 1./dt
		else:
			return False

	def write_eeprom(self,locations,values):
		"""
		Write to EEPROM Locations
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  ============================================================================================
		**Arguments** 
		==============  ============================================================================================
		locations       Array of positions between 0 and 255 e.g. : [4,5,6]
		values          Array of values to write to those locations
 		==============  ============================================================================================

		Caution : Positions 0,1,2 are used for storing the address of the wireless node. If you change these, you
		will have to reconnect to the new address once the wireless node is reset/power cycled.
		
		example::
		
			>>> write_eeprom([3,4,5],[3,3,3])
			write the value 3 to locations 3,4,5

		"""
		self.__selectMe__()
		mixarray=[]
		if len(locations) != len(values):
			print ('mismatch in number of locations and values')
			return False

		for a,b in zip(locations,values):
			mixarray+=[a,b]

		res = self.NRF.transaction([self.MISC_COMMANDS,self.EEPROM_WRITE]+mixarray,timeout=100)
		print (res)

	def read_eeprom(self,locations):
		"""
		read from EEPROM Locations
		
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		
		==============  ============================================================================================
		**Arguments** 
		==============  ============================================================================================
		locations       Array of positions between 0 and 255 e.g. : [4,5,6]
 		==============  ============================================================================================

		Positions 0,1,2 are used for storing the address of the wireless node.
		
		example::
		
			>>> read_eeprom([3,4,5])
			read from locations 3,4,5

		"""
		self.__selectMe__()
		res = self.NRF.transactionWithRetries([self.MISC_COMMANDS,self.EEPROM_READ]+locations)
		return res

	def raiseException(self,ex, msg):
			msg += '\n' + ex.message
			#self.H.disconnect()
			raise RuntimeError(msg)
	def __ble__(self):
		self.__selectMe__()
		#print ('writing to ',reg,val)
		return self.NRF.transaction([self.NRF_COMMANDS,self.NRF_BLE],listen=False)
		
