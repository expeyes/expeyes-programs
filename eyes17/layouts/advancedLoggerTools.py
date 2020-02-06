############# MATHEMATICAL AND ANALYTICS ###############
import functools
from functools import partial
import numpy as np
import time,struct


try:
	from scipy import optimize
except:
	print('scipy not available')

def find_peak(va):
	vmax = 0.0
	size = len(va)
	index = 0
	for i in range(1,size):		# skip first 2 channels, DC
		if va[i] > vmax:
			vmax = va[i]
			index = i
	return index

def bswap(val):
	return struct.unpack('<H', struct.pack('>H', val))[0]
def makeuint16(lsb, msb):
	return ((msb & 0xFF) << 8)  | (lsb & 0xFF)

#-------------------------- Fourier Transform ------------------------------------
def fft(ya, si):
	'''
	Returns positive half of the Fourier transform of the signal ya. 
	Sampling interval 'si', in milliseconds
	'''
	NP = len(ya)
	if NP%2: #odd number
		ya = ya[:-1]
		NP-=1
	v = np.array(ya)
	tr = abs(np.fft.fft(v))/NP
	frq = np.fft.fftfreq(NP, si)
	x = frq.reshape(2,int(NP/2))
	y = tr.reshape(2,int(NP/2))
	return x[0], y[0]    

def find_frequency(x,y):		# Returns the fundamental frequency using FFT
	tx,ty = fft(y, x[1]-x[0])
	index = find_peak(ty)
	if index == 0:
		return None
	else:
		return tx[index]

#-------------------------- Sine Fit ------------------------------------------------
def sine_eval(x,p):			# y = a * sin(2*pi*f*x + phi)+ offset
	return p[0] * np.sin(2*np.pi*p[1]*x+p[2])+p[3]

def sine_erf(p,x,y):					
	return y - sine_eval(x,p)


def fit_sine(xa,ya, freq = 0):	# Time in mS, V in volts, freq in Hz, accepts numpy arrays
	size = len(ya)
	mx = max(ya)
	mn = min(ya)
	amp = (mx-mn)/2
	off = np.average(ya)
	if freq == 0:						# Guess frequency not given
		freq = find_frequency(xa,ya)
	if freq == None:
		return None
	#print 'guess a & freq = ', amp, freq
	par = [amp, freq, 0.0, off] # Amp, freq, phase , offset
	par, pcov = optimize.leastsq(sine_erf, par, args=(xa, ya))
	return par
	

#--------------------------Damped Sine Fit ------------------------------------------------
def dsine_eval(x,p):
	return     p[0] * np.sin(2*np.pi*p[1]*x+p[2]) * np.exp(-p[4]*x) + p[3]
def dsine_erf(p,x,y):
	return y - dsine_eval(x,p)


def fit_dsine(xlist, ylist, freq = 0):
	size = len(xlist)
	xa = np.array(xlist, dtype=np.float)
	ya = np.array(ylist, dtype=np.float)
	amp = (max(ya)-min(ya))/2
	off = np.average(ya)
	if freq == 0:
		freq = find_frequency(xa,ya)
	if freq==None: return None
	par = [amp, freq, 0.0, off, 0.] # Amp, freq, phase , offset, decay constant
	par, pcov = optimize.leastsq(dsine_erf, par,args=(xa,ya))

	return par


############# MATHEMATICAL AND ANALYTICS ###############

class LOGGER:	
	def __init__(self,I2C):
		self.sensors={
			0x39:{
				'name':'TSL2561 Luminosity Sensor',
				'init':self.TSL2561_init,
				'read':self.TSL2561_all,
				'fields':['total','IR'],
				'min':[0,0],
				'max':[2**15,2**15],
				'config':[{
							'name':'gain',
							'options':['1x','16x'],
							'function':self.TSL2561_gain
							},
							{
							'name':'Integration Time',
							'options':['3 mS','101 mS','402 mS'],
							'function':self.TSL2561_timing
							}
					] },
			0x1E:{
				'name':'HMC5883L 3 Axis Magnetometer ',
				'init':self.HMC5883L_init,
				'read':self.HMC5883L_all,
				'fields':['Mx','My','Mz'],
				'min':[-5000,-5000,-5000],
				'max':[5000,5000,5000],
				'config':[{
							'name':'gain',
							'options':['1x','16x'],
							'function':self.TSL2561_gain
							},
							{
							'name':'Integration Time',
							'options':['3 mS','101 mS','402 mS'],
							'function':self.TSL2561_timing
							}
					] },
			0x68:{
				'name':'MPU6050 3 Axis Accelerometer and Gyro (Ax, Ay, Az, Temp, Gx, Gy, Gz) ',
				'init':self.MPU6050_init,
				'read':self.MPU6050_all,
				'fields':['Ax','Ay','Az','Temp','Gx','Gy','Gz'],
				'min':[-1*2**15,-1*2**15,-1*2**15,0,-1*2**15,-1*2**15,-1*2**15],
				'max':[2**15,2**15,2**15,2**16,2**15,2**15,2**15],
				'config':[{
					'name':'Gyroscope Range',
					'options':['250','500','1000','2000'],
					'function':self.MPU6050_gyro_range
					},
					{
					'name':'Accelerometer Range',
					'options':['2x','4x','8x','16x'],
					'function':self.MPU6050_accel_range
					},
					{
					'name':'Kalman',
					'options':['OFF','0.001','0.01','0.1','1','10'],
					'function':self.MPU6050_kalman_set
					}
			]},
			118:{
				'name':'BMP280 Pressure and Temperature sensor',
				'init':self.BMP280_init,
				'read':self.BMP280_all,
				'fields':['Pressure','Temp','rH %%'],
				'min':[0,0,0],
				'max':[1600,100,100],
				},
			119:{
				'name':'MS5611 Pressure and Temperature Sensor',
				'init':self.MS5611_init,
				'read':self.MS5611_all,
				'fields':['Pressure','Temp','Alt'],
				'min':[0,0,0],
				'max':[1600,100,10],
				},
			0x41:{  #A0 pin connected to Vs . Otherwise address 0x40 conflicts with PCA board.
				'name':'INA3221 Current Sensor',
				'init':self.INA3221_init,
				'read':self.INA3221_all,
				'fields':['CH1','CH2','CH3'],
				'min':[0,0,0],
				'max':[1000,1000,1000],
				},
			0x29:{  #VL53L0X.
				'name':'VL53L0X time of flight sensor',
				'init':self.VL53L0X_init,
				'read':self.VL53L0X_all,
				'fields':['mm'],
				'min':[0],
				'max':[1000],
				},
			0x5A:{
				'name':'MLX90614 Passive IR thermometer',
				'init':self.MLX90614_init,
				'read':self.MLX90614_all,
				'fields':['TEMP'],
				'min':[0],
				'max':[350]}
		}
		self.controllers={
			0x62:{
				'name':'MCP4725 DAC',
				'init':self.MCP4725_init,
				'write':[['CH0',0,4095,0,self.MCP4725_set]],
				},
		}

		self.special={
			0x40:{
				'name':'PCA9685 PWM',
				'init':self.PCA9685_init,
				'write':[['Channel 1',0,180,90,functools.partial(self.PCA9685_set,1)], #name, start, stop, default, function
						['Channel 2',0,180,90,functools.partial(self.PCA9685_set,2)],
						['Channel 3',0,180,90,functools.partial(self.PCA9685_set,3)],
						['Channel 4',0,180,90,functools.partial(self.PCA9685_set,4)],
						],
				}
		}

		for a in self.sensors:
			self.sensors[a]['type'] = 'input'

		self.I2C = I2C
		self.I2CWriteBulk = I2C.writeBulk
		self.I2CReadBulk = I2C.readBulk
		self.I2CScan = I2C.scan

	'''
	def I2CScan(self):
	def I2CWriteBulk(self,address,bytestream): 
	def I2CReadBulk(self,address,register,total): 
	'''
	class KalmanFilter(object):
		'''
		Credits:http://scottlobdell.me/2014/08/kalman-filtering-python-reading-sensor-input/
		'''
		def __init__(self, var, est,initial_values): #var = process variance. est = estimated measurement var
			self.var = np.array(var)
			self.est = np.array(est)
			self.posteri_estimate = np.array(initial_values)
			self.posteri_error_estimate = np.ones(len(var),dtype=np.float16)

		def input(self, vals):
			vals = np.array(vals)
			priori_estimate = self.posteri_estimate
			priori_error_estimate = self.posteri_error_estimate + self.var

			blending_factor = priori_error_estimate / (priori_error_estimate + self.est)
			self.posteri_estimate = priori_estimate + blending_factor * (vals - priori_estimate)
			self.posteri_error_estimate = (1 - blending_factor) * priori_error_estimate

		def output(self):
			return self.posteri_estimate


	MPU6050_kalman = 0
	def MPU6050_init(self):
		self.I2CWriteBulk(0x68,[0x1B,0<<3]) #Gyro Range . 250
		self.I2CWriteBulk(0x68,[0x1C,0<<3]) #Accelerometer Range. 2
		self.I2CWriteBulk(0x68,[0x6B, 0x00]) #poweron

	def MPU6050_gyro_range(self,val):
		self.I2CWriteBulk(0x68,[0x1B,val<<3]) #Gyro Range . 250,500,1000,2000 -> 0,1,2,3 -> shift left by 3 positions

	def MPU6050_accel_range(self,val):
		print(val)
		self.I2CWriteBulk(0x68,[0x1C,val<<3]) #Accelerometer Range. 2,4,8,16 -> 0,1,2,3 -> shift left by 3 positions

	def MPU6050_kalman_set(self,val):
		if not val:
			self.MPU6050_kalman = 0
			return
		noise=[]
		for a in range(50):
			noise.append(np.array(self.MPU6050_all(disableKalman=True)))
		noise = np.array(noise)
		self.MPU6050_kalman = self.KalmanFilter(1e6*np.ones(noise.shape[1])/(10**val), np.std(noise,0)**2, noise[-1])


	def MPU6050_accel(self):
		b = self.I2CReadBulk(0x68, 0x3B ,6)
		if b is None:return None
		if None not in b:
			return [(b[x*2+1]<<8)|b[x*2] for x in range(3)] #X,Y,Z

	def MPU6050_gyro(self):
		b = self.I2CReadBulk(0x68, 0x3B+6 ,6)
		if b is None:return None
		if None not in b:
			return [(b[x*2+1]<<8)|b[x*2] for x in range(3)] #X,Y,Z

	def MPU6050_all(self,disableKalman=False):
		'''
		returns a 7 element list. Ax,Ay,Az,T,Gx,Gy,Gz
		returns None if communication timed out with I2C sensor
		disableKalman can be set to True if Kalman was previously enabled.
		'''
		b = self.I2CReadBulk(0x68, 0x3B ,14)
		if not b:return None
		if None not in b:
			if len(b)!=14:return None
			if (not self.MPU6050_kalman) or disableKalman:
				return [ np.int16((b[x*2]<<8)|b[x*2+1]) for x in range(7) ] #Ax,Ay,Az, Temp, Gx, Gy,Gz
			else:
				self.MPU6050_kalman.input([ np.int16((b[x*2]<<8)|b[x*2+1]) for x in range(7) ])
				return self.MPU6050_kalman.output()


	####### BMP280 ###################
	# https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf
	## Partly from https://github.com/farmerkeith/BMP280-library/blob/master/farmerkeith_BMP280.cpp
	BMP280_ADDRESS = 118
	BMP280_REG_CONTROL = 0xF4
	BMP280_REG_RESULT = 0xF6
	BMP280_HUMIDITY_ENABLED = False
	_BMP280_humidity_calib = [0]*6
	BMP280_oversampling = 0
	_BMP280_PRESSURE_MIN_HPA = 0
	_BMP280_PRESSURE_MAX_HPA = 1600
	_BMP280_sea_level_pressure = 1013.25 #for calibration.. from circuitpython library
	def BMP280_init(self):
		b = self.I2CWriteBulk(self.BMP280_ADDRESS,[0xE0,0xB6]) #reset
		time.sleep(0.1)
		self.BMP280_HUMIDITY_ENABLED = False
		b = self.I2CReadBulk(self.BMP280_ADDRESS, 0xD0 ,1)
		print(b)
		if b is None:return None
		b = b[0]
		if b in [0x58,0x56,0x57]:
			print('BMP280. ID:',b)
		elif b==0x60:
			self.BMP280_HUMIDITY_ENABLED = True
			print('BME280 . includes humidity')
		else:
			print('ID unknown',b)
		# get calibration data
		b = self.I2CReadBulk(self.BMP280_ADDRESS, 0x88 ,24) #24 bytes containing calibration data
		coeff = list(struct.unpack('<HhhHhhhhhhhh', bytes(b)))
		coeff = [float(i) for i in coeff]
		self._BMP280_temp_calib = coeff[:3]
		self._BMP280_pressure_calib = coeff[3:]
		self._BMP280_t_fine = 0.


		if self.BMP280_HUMIDITY_ENABLED:
			self.I2CWriteBulk(self.BMP280_ADDRESS, [0xF2,0b101]) #ctrl_hum. oversampling x 16
			#humidity calibration read 
			self._BMP280_humidity_calib = [0]*6
			self._BMP280_humidity_calib[0] = self.I2CReadBulk(self.BMP280_ADDRESS,0xA1,1)[0]#H1
			coeff = self.I2CReadBulk(self.BMP280_ADDRESS,0xE1, 7) 
			coeff = list(struct.unpack('<hBbBbb', bytes(coeff)))
			self._BMP280_humidity_calib[1] = float(coeff[0])
			self._BMP280_humidity_calib[2] = float(coeff[1])
			self._BMP280_humidity_calib[3] = float((coeff[2] << 4) |  (coeff[3] & 0xF))
			self._BMP280_humidity_calib[4] = float((coeff[4] << 4) | (coeff[3] >> 4))
			self._BMP280_humidity_calib[5] = float(coeff[5])

		self.I2CWriteBulk(self.BMP280_ADDRESS, [0xF4,0xFF]) # ctrl_meas (oversampling of pressure, temperature)


	def _BMP280_calcTemperature(self,adc_t):
		v1 = (adc_t / 16384.0 - self._BMP280_temp_calib[0] / 1024.0) * self._BMP280_temp_calib[1]
		v2 = ((adc_t / 131072.0 - self._BMP280_temp_calib[0] / 8192.0) * ( adc_t / 131072.0 - self._BMP280_temp_calib[0] / 8192.0)) * self._BMP280_temp_calib[2]
		self._BMP280_t_fine = int(v1+v2)
		return (v1+v2) / 5120.0  #actual temperature. 

	def _BMP280_calcPressure(self,adc_p,adc_t):
		self._BMP280_calcTemperature(adc_t) #t_fine has been set now.
		# Algorithm from the BMP280 driver. adapted from adafruit adaptation of
		# https://github.com/BoschSensortec/BMP280_driver/blob/master/bmp280.c
		var1 = self._BMP280_t_fine / 2.0 - 64000.0
		var2 = var1 * var1 * self._BMP280_pressure_calib[5] / 32768.0
		var2 = var2 + var1 * self._BMP280_pressure_calib[4] * 2.0
		var2 = var2 / 4.0 + self._BMP280_pressure_calib[3] * 65536.0
		var3 = self._BMP280_pressure_calib[2] * var1 * var1 / 524288.0
		var1 = (var3 + self._BMP280_pressure_calib[1] * var1) / 524288.0
		var1 = (1.0 + var1 / 32768.0) * self._BMP280_pressure_calib[0]
		if not var1:
			return _BMP280_PRESSURE_MIN_HPA
		pressure = 1048576.0 - adc_p
		pressure = ((pressure - var2 / 4096.0) * 6250.0) / var1
		var1 = self._BMP280_pressure_calib[8] * pressure * pressure / 2147483648.0
		var2 = pressure * self._BMP280_pressure_calib[7] / 32768.0
		pressure = pressure + (var1 + var2 + self._BMP280_pressure_calib[6]) / 16.0
		pressure /= 100
		if pressure < self._BMP280_PRESSURE_MIN_HPA:
			return self._BMP280_PRESSURE_MIN_HPA
		if pressure > self._BMP280_PRESSURE_MAX_HPA:
			return self._BMP280_PRESSURE_MAX_HPA
		return pressure

	def _BMP280_calcHumidity(self,adc_h,adc_t):
		self._BMP280_calcTemperature(adc_t) #t fine set.
		var1 = float(self._BMP280_t_fine) - 76800.0
		var2 = (self._BMP280_humidity_calib[3] * 64.0 + (self._BMP280_humidity_calib[4] / 16384.0) * var1)
		var3 = adc_h - var2
		var4 = self._BMP280_humidity_calib[1] / 65536.0
		var5 = (1.0 + (self._BMP280_humidity_calib[2] / 67108864.0) * var1)
		var6 = 1.0 + (self._BMP280_humidity_calib[5] / 67108864.0) * var1 * var5
		var6 = var3 * var4 * (var5 * var6)
		humidity = var6 * (1.0 - self._BMP280_humidity_calib[0] * var6 / 524288.0)
		if humidity > 100:
			return 100
		if humidity < 0:
			return 0

		return humidity

	def BMP280_all(self):
		if self.BMP280_HUMIDITY_ENABLED:
			data = self.I2CReadBulk(self.BMP280_ADDRESS, 0xF7,8)
		else:
			data = self.I2CReadBulk(self.BMP280_ADDRESS, 0xF7,6)
		if data is None:return None
		if None not in data:
			# Convert pressure and temperature data to 19-bits
			adc_p = (((data[0] & 0xFF) * 65536.) + ((data[1] & 0xFF) * 256.) + (data[2] & 0xF0)) / 16.
			adc_t = (((data[3] & 0xFF) * 65536.) + ((data[4] & 0xFF) * 256.) + (data[5] & 0xF0)) / 16.
			if self.BMP280_HUMIDITY_ENABLED:
				adc_h = (data[6] * 256.) + data[7]
				return [self._BMP280_calcPressure(adc_p,adc_t), self._BMP280_calcTemperature(adc_t), self._BMP280_calcHumidity(adc_h,adc_t)]
			else:
				return [self._BMP280_calcPressure(adc_p,adc_t), self._BMP280_calcTemperature(adc_t), 0]

		return None

	####### MS5611 Altimeter ###################
	MS5611_ADDRESS = 119

	def MS5611_init(self):
		self.I2CWriteBulk(self.MS5611_ADDRESS, [0x1E]) # reset
		time.sleep(0.5)
		self._MS5611_calib = np.zeros(6)

		#calibration data.
		#pressure gain, offset . T coeff of P gain, offset. Ref temp. T coeff of T. all unsigned shorts.
		b = self.I2CReadBulk(self.MS5611_ADDRESS, 0xA2 ,2) 
		if b is None:return None
		self._MS5611_calib[0] = struct.unpack('!H', bytes(b))[0]
		b = self.I2CReadBulk(self.MS5611_ADDRESS, 0xA4 ,2) 
		self._MS5611_calib[1] = struct.unpack('!H', bytes(b))[0]
		b = self.I2CReadBulk(self.MS5611_ADDRESS, 0xA6 ,2) 
		self._MS5611_calib[2] = struct.unpack('!H', bytes(b))[0]
		b = self.I2CReadBulk(self.MS5611_ADDRESS, 0xA8 ,2) 
		self._MS5611_calib[3] = struct.unpack('!H', bytes(b))[0]
		b = self.I2CReadBulk(self.MS5611_ADDRESS, 0xAA ,2) 
		self._MS5611_calib[4] = struct.unpack('!H', bytes(b))[0]
		b = self.I2CReadBulk(self.MS5611_ADDRESS, 0xAC ,2) 
		self._MS5611_calib[5] = struct.unpack('!H', bytes(b))[0]
		print('Calibration for MS5611:',self._MS5611_calib)
		

	def MS5611_all(self):
		self.I2CWriteBulk(self.MS5611_ADDRESS, [0x48]) #  0x48 Pressure conversion(OSR = 4096) command
		time.sleep(0.01) #10mS
		b = self.I2CReadBulk(self.MS5611_ADDRESS, 0x00 ,3) #data.
		D1 = b[0]*65536 + b[1]*256 + b[2] #msb2, msb1, lsb

		self.I2CWriteBulk(self.MS5611_ADDRESS, [0x58]) #  0x58 Temperature conversion(OSR = 4096) command
		time.sleep(0.01)
		b = self.I2CReadBulk(self.MS5611_ADDRESS, 0x00 ,3) #data.
		D2 = b[0]*65536 + b[1]*256 + b[2] #msb2, msb1, lsb
		

		dT = D2 - self._MS5611_calib[4] * 256
		TEMP = 2000 + dT * self._MS5611_calib[5] / 8388608
		OFF = self._MS5611_calib[1] * 65536 + (self._MS5611_calib[3] * dT) / 128
		SENS = self._MS5611_calib[0] * 32768 + (self._MS5611_calib[2] * dT ) / 256
		T2 = 0;	OFF2 = 0;	SENS2 = 0
		if TEMP >= 2000 :
			T2 = 0
			OFF2 = 0
			SENS2 = 0
		elif TEMP < 2000 :
			T2 = (dT * dT) / 2147483648
			OFF2 = 5 * ((TEMP - 2000) * (TEMP - 2000)) / 2
			SENS2 = 5 * ((TEMP - 2000) * (TEMP - 2000)) / 4
			if TEMP < -1500 :
				OFF2 = OFF2 + 7 * ((TEMP + 1500) * (TEMP + 1500))
				SENS2 = SENS2 + 11 * ((TEMP + 1500) * (TEMP + 1500)) / 2

		TEMP = TEMP - T2
		OFF = OFF - OFF2
		SENS = SENS - SENS2
		pressure = ((((D1 * SENS) / 2097152) - OFF) / 32768.0) / 100.0
		cTemp = TEMP / 100.0
		return [pressure,cTemp,0]


	### INA3221 3 channel , high side current sensor #############
	INA3221_ADDRESS  = 0x41
	_INA3221_REG_CONFIG = 0x0
	_INA3221_SHUNT_RESISTOR_VALUE = 0.1
	_INA3221_REG_SHUNTVOLTAGE = 0x01
	_INA3221_REG_BUSVOLTAGE = 0x02

	def INA3221_init(self):
		self.I2CWriteBulk(self.INA3221_ADDRESS,[self._INA3221_REG_CONFIG, 0b01110101, 0b00100111 ])  #cont shunt.

	def INA3221_all(self):
		I = [0.,0.,0.]
		b = self.I2CReadBulk(self.INA3221_ADDRESS,self._INA3221_REG_SHUNTVOLTAGE  , 2) 
		if b is None:return None
		b[1]&=0xF8; I[0] = struct.unpack('!h',bytes(b))[0]
		b = self.I2CReadBulk(self.INA3221_ADDRESS,self._INA3221_REG_SHUNTVOLTAGE  +2 , 2) 
		if b is None:return None
		b[1]&=0xF8; I[1] = struct.unpack('!h',bytes(b))[0]
		b = self.I2CReadBulk(self.INA3221_ADDRESS,self._INA3221_REG_SHUNTVOLTAGE  +4 , 2) 
		if b is None:return None
		b[1]&=0xF8; I[2] = struct.unpack('!h',bytes(b))[0]
		return [0.005*I[0]/self._INA3221_SHUNT_RESISTOR_VALUE,0.005*I[1]/self._INA3221_SHUNT_RESISTOR_VALUE,0.005*I[2]/self._INA3221_SHUNT_RESISTOR_VALUE]
	

	TSL_GAIN = 0x00 # 0x00=1x , 0x10 = 16x
	TSL_TIMING = 0x00 # 0x00=3 mS , 0x01 = 101 mS, 0x02 = 402mS
	def TSL2561_init(self):
		self.I2CWriteBulk(0x39,[0x80 , 0x03 ]) #poweron
		self.I2CWriteBulk(0x39,[0x80 | 0x01, self.TSL_GAIN|self.TSL_TIMING ]) 
		return self.TSL2561_all()

	def TSL2561_gain(self,gain):
		self.TSL_GAIN = gain<<4
		self.TSL2561_config(self.TSL_GAIN,self.TSL_TIMING)
		
	def TSL2561_timing(self,timing):
		self.TSL_TIMING = timing
		self.TSL2561_config(self.TSL_GAIN,self.TSL_TIMING)

	def TSL2561_rate(self,timing):
		self.TSL_TIMING = timing
		self.TSL2561_config(self.TSL_GAIN,self.TSL_TIMING)

	def TSL2561_config(self,gain,timing):
		self.I2CWriteBulk(0x39,[0x80 | 0x01, gain|timing]) #Timing register 0x01. gain[1x,16x] | timing[13mS,100mS,400mS]

	def TSL2561_all(self):
		'''
		returns a 2 element list. total,IR
		returns None if communication timed out with I2C sensor
		'''
		b = self.I2CReadBulk(0x39,0x80 | 0x20 | 0x0C ,4)
		if b is None:return None
		if None not in b:
			return [ (b[x*2+1]<<8)|b[x*2] for x in range(2) ] #total, IR

	def MLX90614_init(self):
		pass

	def MLX90614_all(self):
		'''
		return a single element list.  None if failed
		'''
		vals = self.I2CReadBulk(0x5A, 0x07 ,3)
		if vals is None:return None
		if vals:
			if len(vals)==3:
				return [((((vals[1]&0x007f)<<8)+vals[0])*0.02)-0.01 - 273.15]
			else:
				return None
		else:
			return None

	def MCP4725_init(self):
		pass

	def MCP4725_set(self,val):
		'''
		Set the DAC value. 0 - 4095
		'''
		self.I2CWriteBulk(0x62, [0x40,(val>>4)&0xFF,(val&0xF)<<4])

	####################### HMC5883L MAGNETOMETER ###############

	HMC5883L_ADDRESS = 0x1E
	HMC_CONFA=0x00
	HMC_CONFB=0x01
	HMC_MODE=0x02
	HMC_STATUS=0x09

	#--------CONFA register bits. 0x00-----------
	HMCSamplesToAverage=0
	HMCSamplesToAverage_choices=[1,2,4,8]
	
	HMCDataOutputRate=6
	HMCDataOutputRate_choices=[0.75,1.5,3,7.5,15,30,75]
	
	HMCMeasurementConf=0
	
	#--------CONFB register bits. 0x01-----------
	HMCGainValue = 7 #least sensitive
	HMCGain_choices = [8,7,6,5,4,3,2,1]
	HMCGainScaling=[1370.,1090.,820.,660.,440.,390.,330.,230.]

	def HMC5883L_init(self):
		self.__writeHMCCONFA__()
		self.__writeHMCCONFB__()
		self.I2CWriteBulk(self.HMC5883L_ADDRESS,[self.HMC_MODE,0]) #enable continuous measurement mode

	def __writeHMCCONFB__(self):
		self.I2CWriteBulk(self.HMC5883L_ADDRESS,[self.HMC_CONFB,self.HMCGainValue<<5]) #set gain

	def __writeHMCCONFA__(self):
		self.I2CWriteBulk(self.HMC5883L_ADDRESS,[self.HMC_CONFA,(self.HMCDataOutputRate<<2)|(self.HMCSamplesToAverage<<5)|(self.HMCMeasurementConf)])

	def HMC5883L_getVals(self,addr,bytes):
		vals = self.I2C.readBulk(self.ADDRESS,addr,bytes) 
		return vals
	
	def HMC5883L_all(self):
		vals=self.HMC5883L_getVals(0x03,6)
		if vals:
			if len(vals)==6:
				return [np.int16(vals[a*2]<<8|vals[a*2+1])/self.HMCGainScaling[self.HMCGainValue] for a in range(3)]
			else:
				return False
		else:
			return False

	PCA9685_address = 64
	def PCA9685_init(self):
		prescale_val = int((25000000.0 / 4096 / 60.)  - 1) # default clock at 25MHz
		#self.I2CWriteBulk(self.PCA9685_address, [0x00,0x10]) #MODE 1 , Sleep
		print('clock set to,',prescale_val)
		self.I2CWriteBulk(self.PCA9685_address, [0xFE,prescale_val]) #PRESCALE , prescale value
		self.I2CWriteBulk(self.PCA9685_address, [0x00,0x80]) #MODE 1 , restart
		self.I2CWriteBulk(self.PCA9685_address, [0x01,0x04]) #MODE 2 , Totem Pole
		
		pass

	CH0 = 0x6	 		    #LED0 start register
	CH0_ON_L =  0x6		#channel0 output and brightness control byte 0
	CH0_ON_H =  0x7		#channel0 output and brightness control byte 1
	CH0_OFF_L = 0x8		#channel0 output and brightness control byte 2
	CH0_OFF_H = 0x9		#channel0 output and brightness control byte 3
	CHAN_WIDTH = 4
	def PCA9685_set(self,chan,angle):
		'''
		chan: 1-16
		Set the servo angle for SG90: angle(0 - 180)
		'''
		Min = 180
		Max = 650
		val = int((( Max-Min ) * ( angle/180. ))+Min)
		print(chan,angle,val)
		self.I2CWriteBulk(self.PCA9685_address, [self.CH0_ON_L + self.CHAN_WIDTH * (chan - 1),0]) #
		self.I2CWriteBulk(self.PCA9685_address, [self.CH0_ON_H + self.CHAN_WIDTH * (chan - 1),0]) # Turn on immediately. At 0.
		self.I2CWriteBulk(self.PCA9685_address, [self.CH0_OFF_L + self.CHAN_WIDTH * (chan - 1),val&0xFF]) #Turn off after val width 0-4095
		self.I2CWriteBulk(self.PCA9685_address, [self.CH0_OFF_H + self.CHAN_WIDTH * (chan - 1),(val>>8)&0xFF])



	def VL53L0X_decode_vcsel_period(self,vcsel_period_reg):
		vcsel_period_pclks = (vcsel_period_reg + 1) << 1;
		return vcsel_period_pclks

	VL53L0X_REG_IDENTIFICATION_MODEL_ID		= 0x00c0
	VL53L0X_REG_IDENTIFICATION_REVISION_ID		= 0x00c2
	VL53L0X_REG_PRE_RANGE_CONFIG_VCSEL_PERIOD	= 0x0050
	VL53L0X_REG_FINAL_RANGE_CONFIG_VCSEL_PERIOD	= 0x0070
	VL53L0X_REG_SYSRANGE_START			= 0x000

	VL53L0X_REG_RESULT_INTERRUPT_STATUS 		= 0x0013
	VL53L0X_REG_RESULT_RANGE_STATUS 		= 0x0014


	VL53L0X_address = 0x29 #41

	def VL53L0X_init(self):
		val1 = self.I2CReadBulk(self.VL53L0X_address, self.VL53L0X_REG_IDENTIFICATION_REVISION_ID,1)[0]
		#print ("Revision ID: " + hex(val1))
		val1 = self.I2CReadBulk(self.VL53L0X_address, self.VL53L0X_REG_IDENTIFICATION_MODEL_ID,1)[0]
		#print ("Device ID: " + hex(val1))
		val1 = self.I2CReadBulk(self.VL53L0X_address, self.VL53L0X_REG_PRE_RANGE_CONFIG_VCSEL_PERIOD,1)[0]
		#print ("PRE_RANGE_CONFIG_VCSEL_PERIOD=" + hex(val1) + " decode: " + str(self.VL53L0X_decode_vcsel_period(val1)))
		val1 = self.I2CReadBulk(self.VL53L0X_address, self.VL53L0X_REG_FINAL_RANGE_CONFIG_VCSEL_PERIOD,1)[0]
		#print ("FINAL_RANGE_CONFIG_VCSEL_PERIOD=" + hex(val1) + " decode: " + str(self.VL53L0X_decode_vcsel_period(val1)))

	def VL53L0X_all(self):
		val1 = self.I2CWriteBulk(self.VL53L0X_address, [self.VL53L0X_REG_SYSRANGE_START, 0x01])
		cnt = 0
		while (cnt < 100): # 1 second waiting time max
			time.sleep(0.010)
			val = self.I2CReadBulk(self.VL53L0X_address, self.VL53L0X_REG_RESULT_RANGE_STATUS,1)[0]
			if (val & 0x01):
				break
			cnt += 1
		if(cnt == 100): #timeout
			return None
		if not (val & 0x01): # Not ready.
			return None

		#	Status = VL53L0X_ReadMulti(Dev, 0x14, localBuffer, 12);
		data = self.I2CReadBulk(self.VL53L0X_address, 0x14, 12)
		#print ("ambient count " + str(makeuint16(data[7], data[6])))
		#print ("signal count " + str(makeuint16(data[9], data[8])))
		d = makeuint16(data[11], data[10])

		DeviceRangeStatusInternal = ((data[0] & 0x78) >> 3)
		#print (DeviceRangeStatusInternal)

		return [d]

class inputs():
	def __init__(self,p):
		self.p = p
		self.analogInputs = self.p.allAnalogChannels
		self.permanentInputs = [{
				'name':'Voltmeter',
				'init':self.init,
				'read':self.readAllVoltages,
				'fields':self.analogInputs,
				'min':[min(self.p.analogInputSources[a].R[0],self.p.analogInputSources[a].R[1]) for a in self.analogInputs],
				'max':[max(self.p.analogInputSources[a].R[0],self.p.analogInputSources[a].R[1]) for a in self.analogInputs],
			},{
				'name':'Time',
				'init':self.initTime,
				'read':self.getTime,
				'fields':['Seconds'],
				'min':[0],
				'max':[100],
			},{
				'name':'Frequency',
				'init':self.init,
				'read':self.get_frequency,
				'fields':['IN2','SEN'],
				'min':[0,0],
				'max':[1e6,1e4],
				'autorefresh':False,
			},{
				'name':'Capacitance',
				'init':self.init,
				'read':self.get_capacitance,
				'fields':['pF'],
				'min':[1.],
				'max':[1.e8],
				'autorefresh':False,
			},{
				'name':'Resistance',
				'init':self.init,
				'read':self.get_resistance,
				'fields':['R'],
				'min':[1],
				'max':[1e6],
			},{
				'name':'Ultrasound Echo',
				'init':self.init,
				'read':self.sr04_distance,
				'fields':['Distance(cm)'],
				'min':[1],
				'max':[80],
				'autorefresh':False,
			},{
				'name':'Oscilloscope',
				'init':self.init,
				'read':None,
				'min':[0],
				'max':[10],
			},]

		for a in self.permanentInputs:
			a['type'] = 'input'

	def initTime(self):
		self.startTime = time.time()
	def getTime(self):
		return [time.time() - self.startTime]
	
	def get_frequency(self):
		return [self.p.get_freq('IN2'),self.p.get_freq('SEN')]
	def get_capacitance(self):
		return [self.p.get_capacitance()*1e12]
	def get_resistance(self):
		return [self.p.get_resistance()]
	def sr04_distance(self):
		return [self.p.sr04_distance()]
	def init(self):
		pass
	def readAllVoltages(self):
		return [self.p.get_average_voltage(a) for a in self.analogInputs]

class outputs():
	p=None
	def __init__(self,p):
		self.permanentOutputs=[]
		self.setDevice(p)
	def setDevice(self,dev):
		self.p = dev
		self.permanentOutputs = [{
				'name':'PV1',
				'init':self.init,
				'write':self.p.set_pv1,
				'fields':['PV1'],
				'min':[-5],
				'max':[5],
			},{
				'name':'PV2',
				'init':self.init,
				'write':self.p.set_pv2,
				'fields':['PV2'],
				'min':[-3.3],
				'max':[3.3],
			},{
				'name':'SQ1',
				'init':self.init,
				'write':self.p.set_sqr1,
				'fields':['SQ1'],
				'min':[1],
				'max':[100000],
			},{
				'name':'WG',
				'init':self.init,
				'write':self.p.set_sine,
				'fields':['WG'],
				'min':[1],
				'max':[5000],
			},]
		for a in self.permanentOutputs:
			a['type'] = 'output'
	def init(self):
		pass

