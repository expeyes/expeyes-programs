############# MATHEMATICAL AND ANALYTICS ###############
import functools,sys
from functools import partial
import numpy as np
import time,struct
from collections import OrderedDict


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
				'min':[-8,-8,-8],
				'max':[8,8,8]
				 },
			13:{
				'name':'QMC5883L 3 Axis Magnetometer ',
				'init':self.QMC5883L_init,
				'read':self.QMC5883L_all,
				'fields':['Mx','My','Mz'],
				'min':[-8,-8,-8],
				'max':[8,8,8],
				'config':[{
							'name':'range',
							'options':['2g','8g'],
							'function':self.QMC_RANGE
							}
					] },
			0x48:{
				'name':'ADS1115',
				'init':self.ADS1115_init,
				'read':self.ADS1115_read,
				'fields':['Voltage'],
				'min':[-20],
				'max':[20],
				'config':[{
							'name':'channel',
							'options':['UNI_0','UNI_1','UNI_2','UNI_3','DIFF_01','DIFF_23'],
							'function':self.ADS1115_channel
							},
							{
							'name':'Data Rate',
							'options':['8','16','32','64','128','250','475','860'],
							'function':self.ADS1115_rate
							},
							{
							'name':'Gain',
							'options':['GAIN_TWOTHIRDS','GAIN_ONE','GAIN_TWO','GAIN_FOUR','GAIN_EIGHT','GAIN_SIXTEEN'],
							'function':self.ADS1115_gain
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
			12:{ #0xc
				'name':'AK8963 Mag',
				'init':self.AK8963_init,
				'read':self.AK8963_all,
				'fields':['X','Y','Z'],
				'min':[-32767,-32767,-32767],
				'max':[32767,32767,32767],
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
				'max':[350]},
			0x5A:{ #Overrides MLX(0x5A). revise this address:sensor map to sensor:[addr.., options] map
				'name':'MPR1221 capacitive touch sensor',
				'init':self.MPR121_init,
				'read':self.MPR121_all,
				'fields':['0','1','2','3','4','5','6','7','8','9','10','11'],
				'min':[0,0,0,0,0,0,0,0,0,0,0,0],
				'max':[1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000]}
		}
		self.namedsensors={
			'TSL2561':{
				'address':[0x29,0x39,0x49],
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
			'HMC5883L':{
				'address':[0x1E,0x3D,0x3C],
				'name':'HMC5883L 3 Axis Magnetometer ',
				'init':self.HMC5883L_init,
				'read':self.HMC5883L_all,
				'fields':['Mx','My','Mz'],
				'min':[-8,-8,-8],
				'max':[8,8,8]
				 },
			'QMC3883':{
				'address':[0x13],
				'name':'QMC5883L 3 Axis Magnetometer ',
				'init':self.QMC5883L_init,
				'read':self.QMC5883L_all,
				'fields':['Mx','My','Mz'],
				'min':[-8,-8,-8],
				'max':[8,8,8],
				'config':[{
							'name':'range',
							'options':['2g','8g'],
							'function':self.QMC_RANGE
							}
					] },
			'ADS1115':{
				'address':[0x48,0x49,0x4A,0x4B],
				'name':'ADS1115',
				'init':self.ADS1115_init,
				'read':self.ADS1115_read,
				'fields':['Voltage'],
				'min':[-20],
				'max':[20],
				'config':[{
							'name':'channel',
							'options':['UNI_0','UNI_1','UNI_2','UNI_3','DIFF_01','DIFF_23'],
							'function':self.ADS1115_channel
							},
							{
							'name':'Data Rate',
							'options':['8','16','32','64','128','250','475','860'],
							'function':self.ADS1115_rate
							},
							{
							'name':'Gain',
							'options':['GAIN_TWOTHIRDS','GAIN_ONE','GAIN_TWO','GAIN_FOUR','GAIN_EIGHT','GAIN_SIXTEEN'],
							'function':self.ADS1115_gain
							}
					] },
			'MPU6050':{
				'address':[0x68,0x69],
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
			'BMP280':{
				'address':[0x76],
				'name':'BMP280 Pressure and Temperature sensor',
				'init':self.BMP280_init,
				'read':self.BMP280_all,
				'fields':['Pressure','Temp','rH %%'],
				'min':[0,0,0],
				'max':[1600,100,100],
				},
			'AK8963':{ #0xc
				'address':[12],
				'name':'AK8963 Mag',
				'init':self.AK8963_init,
				'read':self.AK8963_all,
				'fields':['X','Y','Z'],
				'min':[-32767,-32767,-32767],
				'max':[32767,32767,32767],
				},
			'MS5611':{
				'address':[119],
				'name':'MS5611 Pressure and Temperature Sensor',
				'init':self.MS5611_init,
				'read':self.MS5611_all,
				'fields':['Pressure','Temp','Alt'],
				'min':[0,0,0],
				'max':[1600,100,10],
				},
			'INA3221':{  #A0 pin connected to Vs . Otherwise address 0x40 conflicts with PCA board.
				'address':[0x40,0x41],
				'name':'INA3221 Current Sensor',
				'init':self.INA3221_init,
				'read':self.INA3221_all,
				'fields':['CH1','CH2','CH3'],
				'min':[0,0,0],
				'max':[1000,1000,1000],

			},
			'TSL2591':{
				'address':[0x29],
				'name':'TSL2591 Luminosity Sensor',
				'init':self.TSL2591_init,
				'read':self.TSL2591_all,
				'fields':['Raw','full','IR'],
				'min':[0,0,0],
				'max':[37889,88000,88000],
				'config':[{
							'name':'gain',
							'options':['1x','25x','428x','9876x'],
							'function':self.TSL2591_gain
							},
							{
							'name':'Integration Time',
							'options':['100 mS','200 mS','300 mS','400 mS','500 mS','600 mS'],
							'function':self.TSL2591_timing
							}
					] },
			'VL53L0X':{  #VL53L0X.
				'address':[0x29],
				'name':'VL53L0X time of flight sensor',
				'init':self.VL53L0X_init,
				'read':self.VL53L0X_all,
				'fields':['mm'],
				'min':[0],
				'max':[1000],
				},
			'MLX90614':{
				'address':[0x5A],
				'name':'MLX90614 Passive IR thermometer',
				'init':self.MLX90614_init,
				'read':self.MLX90614_all,
				'fields':['TEMP'],
				'min':[0],
				'max':[350]},
			'MPR1221':{ #Overrides MLX(0x5A). revise this address:sensor map to sensor:[addr.., options] map
				'address':[0x5A],
				'name':'MPR1221 capacitive touch sensor',
				'init':self.MPR121_init,
				'read':self.MPR121_all,
				'fields':['0','1','2','3','4','5','6','7','8','9','10','11'],
				'min':[0,0,0,0,0,0,0,0,0,0,0,0],
				'max':[1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000]}
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

		self.sensormap = {}
		for a in range(128):
			self.sensormap[a] = []
		for a in self.namedsensors:
			if a in self.namedsensors:
				for addr in self.namedsensors[a]['address']:
					self.sensormap[addr].append(a)

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
	MPU6050_ADDRESS = 0x68
	def MPU6050_init(self, **kwargs):
		self.MPU6050_ADDRESS = kwargs.get('address',self.MPU6050_ADDRESS)
		self.I2CWriteBulk(self.MPU6050_ADDRESS,[0x1B,0<<3]) #Gyro Range . 250
		self.I2CWriteBulk(0x68,[0x1C,0<<3]) #Accelerometer Range. 2
		self.I2CWriteBulk(self.MPU6050_ADDRESS,[0x6B, 0x00]) #poweron

	def MPU6050_gyro_range(self,val):
		self.I2CWriteBulk(self.MPU6050_ADDRESS,[0x1B,val<<3]) #Gyro Range . 250,500,1000,2000 -> 0,1,2,3 -> shift left by 3 positions

	def MPU6050_accel_range(self,val):
		self.I2CWriteBulk(self.MPU6050_ADDRESS,[0x1C,val<<3]) #Accelerometer Range. 2,4,8,16 -> 0,1,2,3 -> shift left by 3 positions

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
		b = self.I2CReadBulk(self.MPU6050_ADDRESS, 0x3B ,6)
		if b is None:return None
		if None not in b:
			return [(b[x*2+1]<<8)|b[x*2] for x in range(3)] #X,Y,Z

	def MPU6050_gyro(self):
		b = self.I2CReadBulk(self.MPU6050_ADDRESS, 0x3B+6 ,6)
		if b is None:return None
		if None not in b:
			return [(b[x*2+1]<<8)|b[x*2] for x in range(3)] #X,Y,Z

	def MPU6050_all(self,disableKalman=False):
		'''
		returns a 7 element list. Ax,Ay,Az,T,Gx,Gy,Gz
		returns None if communication timed out with I2C sensor
		disableKalman can be set to True if Kalman was previously enabled.
		'''
		b = self.I2CReadBulk(self.MPU6050_ADDRESS, 0x3B ,14)
		if not b:return None
		if None not in b:
			if len(b)!=14:return None
			if (not self.MPU6050_kalman) or disableKalman:
				return [ np.int16((b[x*2]<<8)|b[x*2+1]) for x in range(7) ] #Ax,Ay,Az, Temp, Gx, Gy,Gz
			else:
				self.MPU6050_kalman.input([ np.int16((b[x*2]<<8)|b[x*2+1]) for x in range(7) ])
				return self.MPU6050_kalman.output()


	######## AK8963 magnetometer attacched to MPU925x #######
	AK8963_ADDRESS =0x0C
	_AK8963_CNTL = 0x0A
	def AK8963_init(self, **kwargs):
			self.AK8963_ADDRESS = kwargs.get('address',self.AK8963_ADDRESS)
			self.I2CWriteBulk(self.AK8963_ADDRESS,[self._AK8963_CNTL,0]) #power down mag
			self.I2CWriteBulk(self.AK8963_ADDRESS,[self._AK8963_CNTL,(1<<4)|6]) #mode   (0=14bits,1=16bits) <<4 | (2=8Hz , 6=100Hz)
	def AK8963_all(self,disableKalman=False):
		vals,tmt=self.I2CReadBulk(self.AK8963_ADDRESS,0x03,7) #6+1 . 1(ST2) should not have bit 4 (0x8) true. It's ideally 16 . overflow bit
		if tmt:return None
		ax,ay,az = struct.unpack('hhh',bytes(vals[:6]))
		if not vals[6]&0x08:return [ax,ay,az]
		else: return None



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
	def BMP280_init(self, **kwargs):
		self.BMP280_ADDRESS = kwargs.get('address',self.BMP280_ADDRESS)
		b = self.I2CWriteBulk(self.BMP280_ADDRESS,[0xE0,0xB6]) #reset
		time.sleep(0.1)
		self.BMP280_HUMIDITY_ENABLED = False
		b = self.I2CReadBulk(self.BMP280_ADDRESS, 0xD0 ,1)
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

	def MS5611_init(self, **kwargs):
		self.MS5611_ADDRESS = kwargs.get('address',self.MS5611_ADDRESS)
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

	def INA3221_init(self, **kwargs):
		self.INA3221_ADDRESS = kwargs.get('address',self.INA3221_ADDRESS)
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
	TSL_ADDRESS = 0x39
	def TSL2561_init(self, **kwargs):
		self.TSL_ADDRESS = kwargs.get('address',self.TSL_ADDRESS)
		self.I2CWriteBulk(self.TSL_ADDRESS,[0x80 , 0x03 ]) #poweron
		self.I2CWriteBulk(self.TSL_ADDRESS,[0x80 | 0x01, self.TSL_GAIN|self.TSL_TIMING ])
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
		self.I2CWriteBulk(self.TSL_ADDRESS,[0x80 | 0x01, gain|timing]) #Timing register 0x01. gain[1x,16x] | timing[13mS,100mS,400mS]

	def TSL2561_all(self):
		'''
		returns a 2 element list. total,IR
		returns None if communication timed out with I2C sensor
		'''
		b = self.I2CReadBulk(self.TSL_ADDRESS,0x80 | 0x20 | 0x0C ,4)
		if b is None:return None
		if None not in b:
			return [ (b[x*2+1]<<8)|b[x*2] for x in range(2) ] #total, IR



	TSL2591_GAIN = 0x00 # 0x00=1x , 0x10 = medium 25x, 0x20 428x , 0x30 Max 9876x
	TSL2591_TIMING = 0x00 # 0x00=100 mS , 0x05 = 600mS

	TSL2591_ADDRESS                = 0x29

	TSL2591_COMMAND_BIT         = 0xA0
	#Register (0x00)
	TSL2591_ENABLE_REGISTER     = 0x00
	TSL2591_ENABLE_POWERON      = 0x01
	TSL2591_ENABLE_POWEROFF     = 0x00
	TSL2591_ENABLE_AEN          = 0x02
	TSL2591_ENABLE_AIEN         = 0x10
	TSL2591_ENABLE_SAI          = 0x40
	TSL2591_ENABLE_NPIEN        = 0x80

	TSL2591_CONTROL_REGISTER    = 0x01
	TSL2591_SRESET              = 0x80
	#AGAIN
	TSL2591_LOW_AGAIN           = 0X00 #Low gain (1x)
	TSL2591_MEDIUM_AGAIN        = 0X10 #Medium gain (25x)
	TSL2591_HIGH_AGAIN          = 0X20 #High gain (428x)
	TSL2591_MAX_AGAIN           = 0x30 #Max gain (9876x)
	#ATIME
	TSL2591_ATIME_100MS         = 0x00 #100 millis #MAX COUNT 36863
	TSL2591_ATIME_200MS         = 0x01 #200 millis #MAX COUNT 65535
	TSL2591_ATIME_300MS         = 0x02 #300 millis #MAX COUNT 65535
	TSL2591_ATIME_400MS         = 0x03 #400 millis #MAX COUNT 65535
	TSL2591_ATIME_500MS         = 0x04 #500 millis #MAX COUNT 65535
	TSL2591_ATIME_600MS         = 0x05 #600 millis #MAX COUNT 65535

	TSL2591_AILTL_REGISTER      = 0x04
	TSL2591_AILTH_REGISTER      = 0x05
	TSL2591_AIHTL_REGISTER      = 0x06
	TSL2591_AIHTH_REGISTER      = 0x07
	TSL2591_NPAILTL_REGISTER    = 0x08
	TSL2591_NPAILTH_REGISTER    = 0x09
	TSL2591_NPAIHTL_REGISTER    = 0x0A
	TSL2591_NPAIHTH_REGISTER    = 0x0B
	TSL2591_PERSIST_REGISTER    = 0x0C

	TSL2591_ID_REGISTER         = 0x12

	TSL2591_STATUS_REGISTER     = 0x13

	TSL2591_CHAN0_LOW           = 0x14
	TSL2591_CHAN0_HIGH          = 0x15
	TSL2591_CHAN1_LOW           = 0x16
	TSL2591_CHAN1_HIGH          = 0x14

	#LUX_DF = GA * 53   GA is the Glass Attenuation factor
	TSL2591_LUX_DF = 408.0
	TSL2591_LUX_COEFB = 1.64
	TSL2591_LUX_COEFC = 0.59
	TSL2591_LUX_COEFD = 0.86

	# LUX_DF              = 408.0
	TSL2591_MAX_COUNT_100MS     = (36863) # 0x8FFF
	TSL2591_MAX_COUNT           = (65535) # 0xFFFF

	def TSL2591_init(self, **kwargs):
		self.TSL2591_ADDRESS = kwargs.get('address',self.TSL2591_ADDRESS)

		b = self.I2CReadBulk(self.TSL2591_ADDRESS, self.TSL2591_COMMAND_BIT|self.TSL2591_ID_REGISTER ,1)
		if b is None:return None
		b = b[0]
		if b != 0x50:
			print('TSL. wrong ID:',b)


		self.I2CWriteBulk(self.TSL2591_ADDRESS,[self.TSL2591_COMMAND_BIT|self.TSL2591_ENABLE_REGISTER, self.TSL2591_ENABLE_AIEN | self.TSL2591_ENABLE_POWERON | self.TSL2591_ENABLE_AEN | self.TSL2591_ENABLE_NPIEN ])
		self.I2CWriteBulk(self.TSL2591_ADDRESS,[self.TSL2591_COMMAND_BIT|self.TSL2591_PERSIST_REGISTER, 0x01 ])
		self.TSL2591_config(self.TSL2591_GAIN,self.TSL2591_TIMING)
		return self.TSL2591_all()

	def TSL2591_gain(self,gain):
		self.TSL2591_GAIN = gain<<4  # 0x00=1x , 0x10 = medium 25x, 0x20 428x , 0x30 Max 9876x
		self.TSL2591_config(self.TSL2591_GAIN,self.TSL2591_TIMING)

	def TSL2591_timing(self,timing):
		self.TSL2591_TIMING = timing
		self.TSL2591_config(self.TSL2591_GAIN,self.TSL2591_TIMING)


	def TSL2591_config(self,gain,timing):
		self.I2CWriteBulk(self.TSL2591_ADDRESS,[self.TSL2591_COMMAND_BIT|self.TSL2591_CONTROL_REGISTER,gain|timing])


	def TSL2591_Read_CHAN0(self):
		b = self.I2CReadBulk(self.TSL2591_ADDRESS, self.TSL2591_COMMAND_BIT|self.TSL2591_CHAN0_LOW ,2)
		if b is None:return None
		if None not in b:
			return (b[1]<<8)|b[0]

	def TSL2591_Read_CHAN1(self):
		b = self.I2CReadBulk(self.TSL2591_ADDRESS, self.TSL2591_COMMAND_BIT|self.TSL2591_CHAN1_LOW ,2)
		if b is None:return None
		if None not in b:
			return (b[1]<<8)|b[0]

	def TSL2591_Read_FullSpectrum(self):
		"""Read the full spectrum (IR + visible) light and return its value"""
		data = (self.TSL2591_Read_CHAN1()  << 16) | TSL2591_self.Read_CHAN0()
		return data

	def TSL2591_Read_Infrared(self):
		'''Read the infrared light and return its value as a 16-bit unsigned number'''
		data = self.TSL2591_Read_CHAN0()
		return data

	def TSL2591_all(self):
		b = self.I2CReadBulk(self.TSL2591_ADDRESS, self.TSL2591_COMMAND_BIT|self.TSL2591_CHAN0_LOW ,4)
		if b is None:return None
		if None not in b:
			channel_0 = (b[1]<<8)|b[0]
			channel_1 = (b[3]<<8)|b[2]

		#channel_0 = self.TSL2591_Read_CHAN0()
		#channel_1 = self.TSL2591_Read_CHAN1()
		#for i in range(0, self.TSL2591_TIMING+2):
		#	time.sleep(0.1)

		atime = 100.0 * self.TSL2591_TIMING + 100.0

		# Set the maximum sensor counts based on the integration time (atime) setting
		if self.TSL2591_TIMING == 0:
			max_counts = self.TSL2591_MAX_COUNT_100MS
		else:
			max_counts = self.TSL2591_MAX_COUNT

		'''
		if channel_0 >= max_counts or channel_1 >= max_counts:
			if(self.TSL2591_GAIN != self.TSL2591_LOW_AGAIN):
				self.TSL2591_GAIN = ((self.TSL2591_GAIN>>4)-1)<<4
				self.TSL2591_config(self.self.TSL2591_GAIN,self.TSL2591_TIMING)
				channel_0 = 0
				channel_1 = 0
				while(channel_0 <= 0 and channel_1 <=0):
					channel_0 = self.TSL2591_Read_CHAN0()
					channel_1 = self.TSL2591_Read_CHAN1()
					time.sleep(0.1)
			else :
				return 0
		'''

		if channel_0 >= max_counts or channel_1 >= max_counts:
			return [(channel_1&0xFFFFFFFF <<16) |channel_0,0, 0 ]

		again = 1.0
		if self.TSL2591_GAIN == self.TSL2591_MEDIUM_AGAIN:
			again = 25.0
		elif self.TSL2591_GAIN == self.TSL2591_HIGH_AGAIN:
			again = 428.0
		elif self.TSL2591_GAIN == self.TSL2591_MAX_AGAIN:
			again = 9876.0

		cpl = (atime * again) / self.TSL2591_LUX_DF

		lux1 = (channel_0 - (self.TSL2591_LUX_COEFB * channel_1)) / cpl

		lux2 = ((self.TSL2591_LUX_COEFC * channel_0) - (self.TSL2591_LUX_COEFD * channel_1) ) / cpl


		return [(channel_1&0xFFFFFFFF <<16) |channel_0,lux1, lux2 ]























	MLX90614_ADDRESS = 0x5A
	def MLX90614_init(self, **kwargs):
		self.MLX90614_ADDRESS = kwargs.get('address',self.MLX90614_ADDRESS)

	def MLX90614_all(self):
		'''
		return a single element list.  None if failed
		'''
		vals = self.I2CReadBulk(self.MLX90614_ADDRESS, 0x07 ,3)
		if vals is None:return None
		if vals:
			if len(vals)==3:
				return [((((vals[1]&0x007f)<<8)+vals[0])*0.02)-0.01 - 273.15]
			else:
				return None
		else:
			return None

	MCP4725_ADDRESS = 0x62
	def MCP4725_init(self, **kwargs):
		self.MCP4725_ADDRESS = kwargs.get('address',self.MCP4725_ADDRESS)

	def MCP4725_set(self,val):
		'''
		Set the DAC value. 0 - 4095
		'''
		self.I2CWriteBulk(self.MCP4725_ADDRESS, [0x40,(val>>4)&0xFF,(val&0xF)<<4])

	######### MPR121 capacitive touch
	MPR121_TOUCH_THRESHOLD_MAX=0XF0
	MPR121_CHANNEL_NUM = 12
	MPR121_TOUCH_STATUS_REG_ADDR_L = 0X00
	MPR121_TOUCH_STATUS_REG_ADDR_H = 0X01
	MPR121_FILTERED_DATA_REG_START_ADDR_L = 0X04
	MPR121_FILTERED_DATA_REG_START_ADDR_H =0X05
	MPR121_BASELINE_VALUE_REG_START_ADDR = 0X1E
	MPR121_BASELINE_FILTERING_CONTROL_REG_START_ADDR= 0X2B
	MPR121_THRESHOLD_REG_START_ADDR = 0X41
	MPR121_DEBOUNCE_REG_ADDR = 0X5B

	MPR121_FILTER_AND_GLOBAL_CDC_CFG_ADDR = 0X5C
	MPR121_FILTER_AND_GLOBAL_CDT_CFG_ADDR = 0X5D

	MPR121_ELEC_CHARGE_CURRENT_REG_START_ADDR = 0X5F
	MPR121_ELEC_CHARGE_TIME_REG_START_ADDR = 0X6C

	MPR121_ELEC_CFG_REG_ADDR = 0X5E

	MPR121_ADDRESS = 0x5B
	def MPR121_init(self, **kwargs):
		self.MPR121_ADDRESS = kwargs.get('address',self.MPR121_ADDRESS)
		self.I2CWriteBulk(self.MPR121_ADDRESS,[self.MPR121_FILTER_AND_GLOBAL_CDC_CFG_ADDR,0x10]) #
		self.I2CWriteBulk(self.MPR121_ADDRESS,[self.MPR121_FILTER_AND_GLOBAL_CDT_CFG_ADDR,0x23]) #
		self.I2CWriteBulk(self.MPR121_ADDRESS,[self.MPR121_DEBOUNCE_REG_ADDR,0x22]) # debounce value
		for a in range(self.MPR121_CHANNEL_NUM):
			self.I2CWriteBulk(self.MPR121_ADDRESS,[self.MPR121_THRESHOLD_REG_START_ADDR + 2*a,0x08]) # touch
			self.I2CWriteBulk(self.MPR121_ADDRESS,[self.MPR121_THRESHOLD_REG_START_ADDR + 2*a +1 ,0x08]) # release threshold

		self.I2CWriteBulk(self.MPR121_ADDRESS,[self.MPR121_ELEC_CFG_REG_ADDR,0x3c]) # start proximity disable mode

	def MPR121_all(self):
		vals=self.I2C.readBulk(self.MPR121_ADDRESS,self.MPR121_FILTERED_DATA_REG_START_ADDR_L,26)
		vals = struct.unpack('<hhhhhhhhhhhhh',bytes(vals))
		return vals

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

	def HMC5883L_init(self, **kwargs):
		self.HMC5883L_ADDRESS = kwargs.get('address',self.HMC5883L_ADDRESS)
		self.__writeHMCCONFA__()
		self.__writeHMCCONFB__()
		self.I2CWriteBulk(self.HMC5883L_ADDRESS,[self.HMC_MODE,0]) #enable continuous measurement mode

	def __writeHMCCONFB__(self):
		self.I2CWriteBulk(self.HMC5883L_ADDRESS,[self.HMC_CONFB,self.HMCGainValue<<5]) #set gain

	def __writeHMCCONFA__(self):
		self.I2CWriteBulk(self.HMC5883L_ADDRESS,[self.HMC_CONFA,(self.HMCDataOutputRate<<2)|(self.HMCSamplesToAverage<<5)|(self.HMCMeasurementConf)])

	def HMC5883L_getVals(self,addr,numbytes):
		vals = self.I2C.readBulk(self.HMC5883L_ADDRESS,addr,numbytes)
		return vals

	def HMC5883L_all(self):
		vals=self.HMC5883L_getVals(0x03,6)
		if vals:
			if len(vals)==6:
				return [np.int16((vals[a*2]<<8)|vals[a*2+1])/self.HMCGainScaling[self.HMCGainValue] for a in range(3)]
			else:
				return False
		else:
			return False




	####################### QMC5883L MAGNETOMETER ###############

	QMC5883L_ADDRESS = 13
	QMC_scaling = 3000

	def QMC5883L_init(self, **kwargs):
		self.QMC5883L_ADDRESS = kwargs.get('address',self.QMC5883L_ADDRESS)
		self.I2CWriteBulk(self.QMC5883L_ADDRESS,[0x0A,0x80]) #0x80=reset. 0x40= rollover
		self.I2CWriteBulk(self.QMC5883L_ADDRESS,[0x0B,0x01]) #init , set/reset period
		self.QMC_RANGE(1)

	def QMC_RANGE(self,r): #0=2G, 1=8G
		if r==1 :
			self.I2CWriteBulk(self.QMC5883L_ADDRESS,[0x09,0b001|0b000 | 0b100 | 0b10000]) #Mode. continuous|oversampling(512) | rate 50Hz | range(8g)
			self.QMC_scaling = 3000
		elif r==0 :
			self.I2CWriteBulk(self.QMC5883L_ADDRESS,[0x09,0b001|0b000 | 0b100 | 0b00000]) #Mode. continuous|oversampling(512) | rate 50Hz | range(2g)
			self.QMC_scaling = 12000

	def QMC5883L_getVals(self,addr,numbytes):
		vals = self.I2C.readBulk(self.QMC5883L_ADDRESS,addr,numbytes)
		return vals

	def QMC5883L_all(self):
		vals=self.QMC5883L_getVals(0x00,6)
		if vals:
			if len(vals)==6:
				v = [np.int16((vals[a*2+1]<<8)|vals[a*2])/self.QMC_scaling for a in range(3)]
				return v
			else:
				return False
		else:
			return False

	###### PCA9685 Servo PWM driver. 16 channel.

	PCA9685_ADDRESS = 64
	def PCA9685_init(self, **kwargs):
		self.PCA9685_ADDRESS = kwargs.get('address',self.PCA9685_ADDRESS)
		prescale_val = int((25000000.0 / 4096 / 60.)  - 1) # default clock at 25MHz
		#self.I2CWriteBulk(self.PCA9685_ADDRESS, [0x00,0x10]) #MODE 1 , Sleep
		print('clock set to,',prescale_val)
		self.I2CWriteBulk(self.PCA9685_ADDRESS, [0xFE,prescale_val]) #PRESCALE , prescale value
		self.I2CWriteBulk(self.PCA9685_ADDRESS, [0x00,0x80]) #MODE 1 , restart
		self.I2CWriteBulk(self.PCA9685_ADDRESS, [0x01,0x04]) #MODE 2 , Totem Pole

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
		self.I2CWriteBulk(self.PCA9685_ADDRESS, [self.CH0_ON_L + self.CHAN_WIDTH * (chan - 1),0]) #
		self.I2CWriteBulk(self.PCA9685_ADDRESS, [self.CH0_ON_H + self.CHAN_WIDTH * (chan - 1),0]) # Turn on immediately. At 0.
		self.I2CWriteBulk(self.PCA9685_ADDRESS, [self.CH0_OFF_L + self.CHAN_WIDTH * (chan - 1),val&0xFF]) #Turn off after val width 0-4095
		self.I2CWriteBulk(self.PCA9685_ADDRESS, [self.CH0_OFF_H + self.CHAN_WIDTH * (chan - 1),(val>>8)&0xFF])



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


	VL53L0X_ADDRESS = 0x29 #41

	def VL53L0X_init(self, **kwargs):
		self.VL53L0X_ADDRESS = kwargs.get('address',self.VL53L0X_ADDRESS)
		val1 = self.I2CReadBulk(self.VL53L0X_ADDRESS, self.VL53L0X_REG_IDENTIFICATION_MODEL_ID,1)[0]
		print ("Device ID: " + hex(val1))
		val1 = self.I2CReadBulk(self.VL53L0X_ADDRESS, self.VL53L0X_REG_PRE_RANGE_CONFIG_VCSEL_PERIOD,1)[0]
		print ("PRE_RANGE_CONFIG_VCSEL_PERIOD=" + hex(val1) + " decode: " + str(self.VL53L0X_decode_vcsel_period(val1)))
		val1 = self.I2CReadBulk(self.VL53L0X_ADDRESS, self.VL53L0X_REG_FINAL_RANGE_CONFIG_VCSEL_PERIOD,1)[0]
		print ("FINAL_RANGE_CONFIG_VCSEL_PERIOD=" + hex(val1) + " decode: " + str(self.VL53L0X_decode_vcsel_period(val1)))
		val1 = self.I2CReadBulk(self.VL53L0X_ADDRESS, self.VL53L0X_REG_IDENTIFICATION_REVISION_ID,1)[0]
		print ("Revision ID: " + hex(val1))
		if val1 == 0x00 or val1 == 0xFF: # No device
			return False
		return True

	def VL53L0X_all(self):
		val1 = self.I2CWriteBulk(self.VL53L0X_ADDRESS, [self.VL53L0X_REG_SYSRANGE_START, 0x01])
		cnt = 0
		while (cnt < 50): # 1 second waiting time max
			time.sleep(0.005)
			val = self.I2CReadBulk(self.VL53L0X_ADDRESS, self.VL53L0X_REG_RESULT_RANGE_STATUS,1)[0]
			if (val & 0x01):
				break
			cnt += 1
		if(cnt == 100): #timeout
			return None
		if not (val & 0x01): # Not ready.
			return None

		data = self.I2CReadBulk(self.VL53L0X_ADDRESS, 0x14, 12)
		#print ("ambient count " + str(makeuint16(data[7], data[6])))
		#print ("signal count " + str(makeuint16(data[9], data[8])))
		d = makeuint16(data[11], data[10])
		DeviceRangeStatusInternal = ((data[0] & 0x78) >> 3)
		#print (data,d,DeviceRangeStatusInternal)
		if DeviceRangeStatusInternal !=11:
			d=None

		return [d]


	## ADS1115
	REG_POINTER_MASK    = 0x3
	REG_POINTER_CONVERT = 0
	REG_POINTER_CONFIG  = 1
	REG_POINTER_LOWTHRESH=2
	REG_POINTER_HITHRESH =3

	REG_CONFIG_OS_MASK      =0x8000
	REG_CONFIG_OS_SINGLE    =0x8000
	REG_CONFIG_OS_BUSY      =0x0000
	REG_CONFIG_OS_NOTBUSY   =0x8000

	REG_CONFIG_MUX_MASK     =0x7000
	REG_CONFIG_MUX_DIFF_0_1 =0x0000  # Differential P = AIN0, N = AIN1 =default)
	REG_CONFIG_MUX_DIFF_0_3 =0x1000  # Differential P = AIN0, N = AIN3
	REG_CONFIG_MUX_DIFF_1_3 =0x2000  # Differential P = AIN1, N = AIN3
	REG_CONFIG_MUX_DIFF_2_3 =0x3000  # Differential P = AIN2, N = AIN3
	REG_CONFIG_MUX_SINGLE_0 =0x4000  # Single-ended AIN0
	REG_CONFIG_MUX_SINGLE_1 =0x5000  # Single-ended AIN1
	REG_CONFIG_MUX_SINGLE_2 =0x6000  # Single-ended AIN2
	REG_CONFIG_MUX_SINGLE_3 =0x7000  # Single-ended AIN3

	REG_CONFIG_PGA_MASK     =0x0E00  #bits 11:9
	REG_CONFIG_PGA_6_144V   =(0<<9)  # +/-6.144V range = Gain 2/3
	REG_CONFIG_PGA_4_096V   =(1<<9)  # +/-4.096V range = Gain 1
	REG_CONFIG_PGA_2_048V   =(2<<9)  # +/-2.048V range = Gain 2 =default)
	REG_CONFIG_PGA_1_024V   =(3<<9)  # +/-1.024V range = Gain 4
	REG_CONFIG_PGA_0_512V   =(4<<9)  # +/-0.512V range = Gain 8
	REG_CONFIG_PGA_0_256V   =(5<<9)  # +/-0.256V range = Gain 16

	REG_CONFIG_MODE_MASK    =0x0100   #bit 8
	REG_CONFIG_MODE_CONTIN  =(0<<8)   # Continuous conversion mode
	REG_CONFIG_MODE_SINGLE  =(1<<8)   # Power-down single-shot mode =default)

	REG_CONFIG_DR_MASK      =0x00E0
	REG_CONFIG_DR_8SPS    =(0<<5)   #8 SPS
	REG_CONFIG_DR_16SPS    =(1<<5)   #16 SPS
	REG_CONFIG_DR_32SPS    =(2<<5)   #32 SPS
	REG_CONFIG_DR_64SPS    =(3<<5)   #64 SPS
	REG_CONFIG_DR_128SPS   =(4<<5)   #128 SPS
	REG_CONFIG_DR_250SPS   =(5<<5)   #260 SPS
	REG_CONFIG_DR_475SPS   =(6<<5)   #475 SPS
	REG_CONFIG_DR_860SPS   =(7<<5)   #860 SPS

	REG_CONFIG_CMODE_MASK   =0x0010
	REG_CONFIG_CMODE_TRAD   =0x0000
	REG_CONFIG_CMODE_WINDOW =0x0010

	REG_CONFIG_CPOL_MASK    =0x0008
	REG_CONFIG_CPOL_ACTVLOW =0x0000
	REG_CONFIG_CPOL_ACTVHI  =0x0008

	REG_CONFIG_CLAT_MASK    =0x0004
	REG_CONFIG_CLAT_NONLAT  =0x0000
	REG_CONFIG_CLAT_LATCH   =0x0004

	REG_CONFIG_CQUE_MASK    =0x0003
	REG_CONFIG_CQUE_1CONV   =0x0000
	REG_CONFIG_CQUE_2CONV   =0x0001
	REG_CONFIG_CQUE_4CONV   =0x0002
	REG_CONFIG_CQUE_NONE    =0x0003
	ADS1115_gains = OrderedDict([('GAIN_TWOTHIRDS',REG_CONFIG_PGA_6_144V),('GAIN_ONE',REG_CONFIG_PGA_4_096V),('GAIN_TWO',REG_CONFIG_PGA_2_048V),('GAIN_FOUR',REG_CONFIG_PGA_1_024V),('GAIN_EIGHT',REG_CONFIG_PGA_0_512V),('GAIN_SIXTEEN',REG_CONFIG_PGA_0_256V)])
	ADS1115_gain_scaling =  OrderedDict([('GAIN_TWOTHIRDS',0.1875),('GAIN_ONE',0.125),('GAIN_TWO',0.0625),('GAIN_FOUR',0.03125),('GAIN_EIGHT',0.015625),('GAIN_SIXTEEN',0.0078125)])
	ADS1115_scaling = 0.125
	ADS1115_channels = OrderedDict([('UNI_0',0),('UNI_1',1),('UNI_2',2),('UNI_3',3),('DIFF_01','01'),('DIFF_23','23')])
	ADS1115_rates = OrderedDict([(8,REG_CONFIG_DR_8SPS),(16,REG_CONFIG_DR_16SPS),(32,REG_CONFIG_DR_32SPS),(64,REG_CONFIG_DR_64SPS),(128,REG_CONFIG_DR_128SPS),(250,REG_CONFIG_DR_250SPS),(475,REG_CONFIG_DR_475SPS),(860,REG_CONFIG_DR_860SPS)]) #sampling data rate
	ADS1115_DATARATE = 250 #250SPS [ 8, 16, 32, 64, 128, 250, 475, 860 ]
	ADS1115_GAIN = REG_CONFIG_PGA_4_096V  # +/-4.096V range = Gain 1 . [+-6, +-4, +-2, +-1, +-0.5, +- 0.25]
	ADS1115_CHANNEL = 0 # ref: type_selection
	ADS1115_ADDRESS = 0x48

	def ADS1115_init(self, **kwargs):
		self.ADS1115_ADDRESS = kwargs.get('address',self.ADS1115_ADDRESS)
		self.I2CWriteBulk(self.ADS1115_ADDRESS,[0x80 , 0x03 ]) #poweron

	def ADS1115_gain(self,gain):
		'''
		options : 'GAIN_TWOTHIRDS','GAIN_ONE','GAIN_TWO','GAIN_FOUR','GAIN_EIGHT','GAIN_SIXTEEN'
		'''
		print('setting gain:',str(gain))
		if(type(gain) == int): #From the UI selectors which return index
			self.ADS1115_GAIN = list(self.ADS1115_gains.items())[gain][1]
			print('set gain with index selection:',self.ADS1115_GAIN)
			self.ADS1115_scaling = list(self.ADS1115_gain_scaling.items())[gain][1]
			print('Scaling factor:',self.ADS1115_scaling)
		else:
			self.ADS1115_GAIN = self.ADS1115_gains.get(gain,self.REG_CONFIG_PGA_4_096V)
			self.ADS1115_scaling = self.ADS1115_gain_scaling.get(gain)
			print('set gain type B:',str(gain),self.ADS1115_GAIN, self.ADS1115_scaling)


	def ADS1115_channel(self,channel):
		'''
		options 'UNI_0','UNI_1','UNI_2','UNI_3','DIFF_01','DIFF_23'
		'''
		self.ADS1115_CHANNEL = self.ADS1115_channels.get(channel,0)

	def ADS1115_rate(self,rate):
		'''
		data rate options 8,16,32,64,128,250,475,860 SPS
		'''
		self.ADS1115_DATARATE = int(rate) # #default 250 sps

	def ADS1115_read(self):
		'''
		returns a voltage from ADS1115 channel selected using ADS1115_channel. default UNI_0 (Unipolar from channel 0)
		'''
		if self.ADS1115_CHANNEL in [0,1,2,3]:
			config = (self.REG_CONFIG_CQUE_NONE # Disable the comparator (default val)
			|self.REG_CONFIG_CLAT_NONLAT        # Non-latching (default val)
			|self.REG_CONFIG_CPOL_ACTVLOW 	    #Alert/Rdy active low   (default val)
			|self.REG_CONFIG_CMODE_TRAD         # Traditional comparator (default val)
			|(self.ADS1115_rates.get(self.ADS1115_DATARATE,self.REG_CONFIG_DR_250SPS))      # 250 samples per second (default)
			|(self.REG_CONFIG_MODE_SINGLE)        # Single-shot mode (default)
			|self.ADS1115_GAIN)
			if self.ADS1115_CHANNEL == 0   : config |= self.REG_CONFIG_MUX_SINGLE_0
			elif self.ADS1115_CHANNEL == 1 : config |= self.REG_CONFIG_MUX_SINGLE_1
			elif self.ADS1115_CHANNEL == 2 : config |= self.REG_CONFIG_MUX_SINGLE_2
			elif self.ADS1115_CHANNEL == 3 : config |= self.REG_CONFIG_MUX_SINGLE_3
			#Set 'start single-conversion' bit
			config |= self.REG_CONFIG_OS_SINGLE
			self.I2CWriteBulk(self.ADS1115_ADDRESS,[self.REG_POINTER_CONFIG,(config>>8)&0xFF,config&0xFF])
			time.sleep(1./self.ADS1115_DATARATE+.002) #convert to mS to S

			b = self.I2CReadBulk(self.ADS1115_ADDRESS, self.REG_POINTER_CONVERT ,2)
			if b is not None:
				x = ( (b[0]<<8)|b[1] )*self.ADS1115_scaling*1e-3
				return [( (b[0]<<8)|b[1] )*self.ADS1115_scaling*1e-3] # scale and convert to volts

		elif self.ADS1115_CHANNEL in ['01','23']:
			return [0]


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

		if self.p.version_number>=5: #SEELAB 3.0 . Includes SPI
			self.permanentInputs.append({
				'name':'MAX6675_temp',
				'init':self.init_MAX6675,
				'read':self.read_MAX6675,
				'fields':['TEMP'],
				'min':[0],
				'max':[400],
				'autorefresh':True,
				'refreshDelay':500, #mS.
			})
			self.permanentInputs.append({
				'name':'MAX31865_temp',
				'init':self.init_MAX31865,
				'read':self.read_MAX31865,
				'fields':['TEMP','Res'],
				'min':[-30,50],
				'max':[400,200],
				'autorefresh':True,
				'refreshDelay':60, #mS.
				'spinboxes':[{
					'name':'Immerse in Ice Bath & Adjust till Temp = 0',
					'minimum':800,
					'maximum':1200,
					'value':1017,
					'function':self.MAX31865_zero
					}
			]


			})


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

	def init_MAX6675(self):
		self.startTime = time.time()
		self.p.SPI.set_parameters(1,2,0,0,1)

	def read_MAX6675(self):
		try:
			self.startTime = time.time()
			self.p.SPI.start('CS1')
			time.sleep(0.003)
			self.p.SPI.stop('CS1')
			time.sleep(0.001)
			self.p.SPI.start('CS1')
			#v1 = self.p.SPI.send8(0xFF)
			#v2 = self.p.SPI.send8(0xFF)
			#val = (v1<<8)|v2
			val = self.p.SPI.send16(0xFFFF)
			self.p.SPI.stop('CS1')


			if(val&0x4):
				print('thermocouple not attached. :',val)
				return [0]
			return [(val>>3)*0.25]
		except Exception as e:
			print (e)
			return [0]

	MAX31865_Res0 = 101.7; # Resistance at 0 degC for 430ohm R_Ref
	def init_MAX31865(self):
		self.p.SPI.set_parameters(1,2,0,0,1)
		self.p.SPI.start('CS1')
		val = self.p.SPI.send16(0x8000|0x00C3) #address 0 , value B2
		self.p.SPI.stop('CS1')

	def read_MAX31865(self):
		try:
			self.p.SPI.start('CS1')
			cnf = self.p.SPI.send16(0x0000)
			RTD_ADC_Code = self.p.SPI.send16(0x0000)>>1
			self.p.SPI.stop('CS1')

			R_REF = 430.0 # Reference Resistor
			a = .00390830;	b = -.000000577500;		c = -0.00000000000418301
			Res_RTD = (RTD_ADC_Code * R_REF) / 32768.0 # PT100 Resistance
			temp_C = -(a*self.MAX31865_Res0) + np.sqrt(a*a*self.MAX31865_Res0*self.MAX31865_Res0 - 4*(b*self.MAX31865_Res0)*(self.MAX31865_Res0 - Res_RTD))
			temp_C = temp_C / (2*(b*self.MAX31865_Res0))
			temp_C_line = (RTD_ADC_Code/32.0) - 256.0
			if (temp_C < 0):
				temp_C = (RTD_ADC_Code/32) - 256

			return [temp_C,Res_RTD]
		except Exception as e:
			print (e)
			return [0,0]

	def MAX31865_zero(self,val):
		val = val/10.
		print('zero:',val)
		self.MAX31865_Res0 = val


class outputs():
	p=None
	if sys.version_info.major==3:
		DDS_MAX_FREQ = 0xFFFFFFF-1    #24 bit resolution
	else:
		DDS_MAX_FREQ = eval("0xFFFFFFFL-1")    #24 bit resolution
	#control bytes
	DDS_B28 = 13
	DDS_HLB = 12
	DDS_FSELECT = 11
	DDS_PSELECT = 10
	DDS_RESET = 8
	DDS_SLEEP1 =7
	DDS_SLEEP12 =6
	DDS_OPBITEN =5
	DDS_DIV2 =3
	DDS_MODE =1

	DDS_FSYNC =9

	DDS_SINE =(0)
	DDS_TRIANGLE =(1<<DDS_MODE)
	DDS_SQUARE =(1<<DDS_OPBITEN)
	DDS_RESERVED =(1<<DDS_OPBITEN)|(1<<DDS_MODE)
	clockScaler = 4 # 8MHz

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
		if self.p.version_number>=5: #SEELAB 3.0 . Includes SPI
			self.permanentOutputs.append({
				'name':'AD9833_DDS',
				'init':self.init_AD9833,
				'write':self.set_AD9833,
				'fields':['FREQ'],
				'min':[1],
				'max':[2e6],
				'outputconfig':[{
							'name':'wavetype',
							'options':['Sine','Triangle'],
							'function':self.set_waveform_mode
							},
					],
			})
		for a in self.permanentOutputs:
			a['type'] = 'output'
	def init(self):
		pass

	def write(self,con):
		self.p.SPI.start(self.CS)
		self.p.SPI.send16(con)
		self.p.SPI.stop(self.CS)

	def init_AD9833(self):
		self.CS='CS1'
		self.p.SPI.set_parameters(2,2,1,1,0)
		self.p.SPI.map_reference_clock(self.clockScaler,'CS3')
		print ('clock set to ',self.p.SPI.DDS_CLOCK )
		self.waveform_mode = self.DDS_SINE;
		self.write(1<<self.DDS_RESET)
		self.write((1<<self.DDS_B28) | self.waveform_mode )               #finished loading data
		self.active_channel = 0
		self.frequency  =  1000

	def set_AD9833(self,freq,register=0,**args):
		self.active_channel = register
		self.frequency  =  freq

		freq_setting = int(round(freq * self.DDS_MAX_FREQ / self.p.SPI.DDS_CLOCK))
		modebits = (1<<self.DDS_B28)| self.waveform_mode
		if register:
			modebits|=(1<<self.DDS_FSELECT)
			regsel = 0x8000
		else:
			regsel=0x4000

		self.write( (1<<self.DDS_RESET) | modebits ) #Ready to load DATA
		self.write( (regsel |  (freq_setting&0x3FFF))&0xFFFF      )           #LSB
		self.write( (regsel | ((freq_setting>>14)&0x3FFF))&0xFFFF )           #MSB
		phase = args.get('phase',0)
		self.write( 0xc000|phase)                            #Phase
		self.write(modebits)               #finished loading data

	def set_voltage_AD9833(self,v):
		self.waveform_mode=self.DDS_TRIANGLE
		self.set_AD9833(0,0,phase = v)#0xfff*v/.6)

	def select_frequency_register(self,register):
		self.active_channel = register
		modebits = self.waveform_mode
		if register:    modebits|=(1<<self.DDS_FSELECT)
		self.write(modebits)


	def set_waveform_mode(self,mode):
		self.waveform_mode=mode+1
		modebits = mode+1
		if self.active_channel:    modebits|=(1<<self.DDS_FSELECT)
		self.write(modebits )

