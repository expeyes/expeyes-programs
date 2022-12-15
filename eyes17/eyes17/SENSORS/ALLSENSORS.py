import numpy as np
import functools, time
from collections import OrderedDict
def bswap(val):
	return struct.unpack('<H', struct.pack('>H', val))[0]
def makeuint16(lsb, msb):
	return ((msb & 0xFF) << 8)  | (lsb & 0xFF)

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
				'max':[5000,5000,5000]
				},
			0x1E:{
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
			87:{ 
				'name':'MAX30100 Oximeter',
				'init':self.MAX30100_init,
				'read':self.MAX30100_all,
				'fields':['IR','Red'],
				'min':[-2000,-2000],
				'max':[2000,2000],
				'config':[{
					'name':'RED LED Current',
					'options':['0mA','4.4mA','7.6mA','11mA','14.2mA','17.4mA','20.8mA','24mA','27.1mA','30.6mA','33.8mA','37mA','40.2mA','43.6mA','46.8mA','50mA'],
					'function':self.MAX30100_set_red_led
					},{
					'name':'IR LED Current',
					'options':['0mA','4.4mA','7.6mA','11mA','14.2mA','17.4mA','20.8mA','24mA','27.1mA','30.6mA','33.8mA','37mA','40.2mA','43.6mA','46.8mA','50mA'],
					'function':self.MAX30100_set_ir_led
					},
					{
					'name':'Sampling Rate',
					'options':['50Hz','100','167Hz','200Hz','400Hz','600Hz','800Hz','1000Hz'],
					'function':self.MAX30100_set_rate
					},
					{
					'name':'Pulse Width',
					'options':['200uS 13Bits','400uS 14bits','800uS 15bits','1600uS 16 bits'],
					'function':self.MAX30100_set_pulse
					}
				]},
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


	######## AK8963 magnetometer attacched to MPU925x #######
	AK8963_ADDRESS =0x0C
	_AK8963_CNTL = 0x0A
	def AK8963_init(self):
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

	############# MAX030100 Heart rate sensor ##################



	MAX30100_address = 87 #0x57

	# Interrupt status register (RO)
	MAX30100_REG_INTERRUPT_STATUS          = 0x00
	MAX30100_IS_PWR_RDY                    = (1 << 0)
	MAX30100_IS_SPO2_RDY                   = (1 << 4)
	MAX30100_IS_HR_RDY                     = (1 << 5)
	MAX30100_IS_TEMP_RDY                   = (1 << 6)
	MAX30100_IS_A_FULL                     = (1 << 7)

	# Interrupt enable register
	MAX30100_REG_INTERRUPT_ENABLE          = 0x01
	MAX30100_IE_ENB_SPO2_RDY               = (1 << 4)
	MAX30100_IE_ENB_HR_RDY                 = (1 << 5)
	MAX30100_IE_ENB_TEMP_RDY               = (1 << 6)
	MAX30100_IE_ENB_A_FULL                 = (1 << 7)

	# FIFO control and data registers
	MAX30100_REG_FIFO_WRITE_POINTER        = 0x02
	MAX30100_REG_FIFO_OVERFLOW_COUNTER     = 0x03
	MAX30100_REG_FIFO_READ_POINTER         = 0x04
	MAX30100_REG_FIFO_DATA                 = 0x05  # Burst read does not autoincrement the address

	# Mode Configuration register
	MAX30100_REG_MODE_CONFIGURATION        = 0x06
	MAX30100_MC_TEMP_EN                    = (1 << 3)
	MAX30100_MC_RESET                      = (1 << 6)
	MAX30100_MC_SHDN           			   = (1 << 7)

	MAX30100_MODE_HRONLY    = 0x02
	MAX30100_MODE_SPO2_HR   = 0x03

	# SpO2 Configuration register
	# Check tables 8 and 9, p19 of the MAX30100 datasheet to see the permissible
	# combinations of sampling rates and pulse widths
	MAX30100_REG_SPO2_CONFIGURATION        = 0x07
	MAX30100_SPC_SPO2_HI_RES_EN            = (1 << 6)

	MAX30100_SAMPRATE_50HZ      = 0x00
	MAX30100_SAMPRATE_100HZ     = 0x01
	MAX30100_SAMPRATE_167HZ     = 0x02
	MAX30100_SAMPRATE_200HZ     = 0x03
	MAX30100_SAMPRATE_400HZ     = 0x04
	MAX30100_SAMPRATE_600HZ     = 0x05
	MAX30100_SAMPRATE_800HZ     = 0x06
	MAX30100_SAMPRATE_1000HZ    = 0x07

	MAX30100_SPC_PW_200US_13BITS    = 0x00
	MAX30100_SPC_PW_400US_14BITS    = 0x01
	MAX30100_SPC_PW_800US_15BITS    = 0x02
	MAX30100_SPC_PW_1600US_16BITS   = 0x03


	MAX30100_REG_LED_CONFIGURATION         = 0x09
	MAX30100_LED_CURR_0MA      = 0x00
	MAX30100_LED_CURR_4_4MA    = 0x01
	MAX30100_LED_CURR_7_6MA    = 0x02
	MAX30100_LED_CURR_11MA     = 0x03
	MAX30100_LED_CURR_14_2MA   = 0x04
	MAX30100_LED_CURR_17_4MA   = 0x05
	MAX30100_LED_CURR_20_8MA   = 0x06
	MAX30100_LED_CURR_24MA     = 0x07
	MAX30100_LED_CURR_27_1MA   = 0x08
	MAX30100_LED_CURR_30_6MA   = 0x09
	MAX30100_LED_CURR_33_8MA   = 0x0a
	MAX30100_LED_CURR_37MA     = 0x0b
	MAX30100_LED_CURR_40_2MA   = 0x0c
	MAX30100_LED_CURR_43_6MA   = 0x0d
	MAX30100_LED_CURR_46_8MA   = 0x0e
	MAX30100_LED_CURR_50MA     = 0x0f

	#Temperature integer part register
	MAX30100_REG_TEMPERATURE_DATA_INT      = 0x16
	# Temperature fractional part register
	MAX30100_REG_TEMPERATURE_DATA_FRAC     = 0x17

	# Revision ID register (RO)
	MAX30100_REG_REVISION_ID                =0xfe
	# Part ID register
	MAX30100_REG_PART_ID                    =0xff
	MAX30100_FIFO_DEPTH                     =0x10


	MAX30100_DEFAULT_MODE               = MAX30100_MODE_HRONLY
	MAX30100_DEFAULT_SAMPLING_RATE      = MAX30100_SAMPRATE_100HZ
	MAX30100_DEFAULT_PULSE_WIDTH        = MAX30100_SPC_PW_1600US_16BITS
	MAX30100_DEFAULT_RED_LED_CURRENT    = MAX30100_LED_CURR_20_8MA
	MAX30100_DEFAULT_IR_LED_CURRENT     = MAX30100_LED_CURR_20_8MA
	MAX30100_EXPECTED_PART_ID           = 0x11
	MAX30100_RINGBUFFER_SIZE            = 16
	MAX30100_SPO2 = 0
	MAX30100_BUF_IR=[]
	MAX30100_BUF_RED=[]
	MAX30100_IR_INTENSITY = MAX30100_LED_CURR_20_8MA
	MAX30100_RED_INTENSITY = MAX30100_LED_CURR_20_8MA
	
	MAX30100_avg_red = 0
	MAX30100_avg_ir = 0
	MAX30100_time=0


	def MAX30100_init(self):
		print('MAX30100 ID:',self.I2CReadBulk(self.MAX30100_address, 0xFF ,1))
		self.I2CWriteBulk(self.MAX30100_address, [self.MAX30100_REG_MODE_CONFIGURATION, self.MAX30100_MODE_SPO2_HR])

		self.MAX30100_SPO2 = self.I2CReadBulk(self.MAX30100_address, self.MAX30100_REG_SPO2_CONFIGURATION ,1)[0]
		self.MAX30100_SPO2 = (self.MAX30100_SPO2&0xfc)|self.MAX30100_DEFAULT_PULSE_WIDTH
		self.MAX30100_SPO2 = (self.MAX30100_SPO2&0xe3)|(self.MAX30100_SAMPRATE_400HZ<<2)
		self.MAX30100_SPO2 |= self.MAX30100_SPC_SPO2_HI_RES_EN
		self.I2CWriteBulk(self.MAX30100_address, [self.MAX30100_REG_SPO2_CONFIGURATION, self.MAX30100_SPO2])
		self.I2CWriteBulk(self.MAX30100_address, [self.MAX30100_REG_LED_CONFIGURATION, (self.MAX30100_RED_INTENSITY<<4)|self.MAX30100_IR_INTENSITY])

		data = self.I2CReadBulk(self.MAX30100_address, self.MAX30100_REG_FIFO_DATA ,8)
		self.MAX30100_avg_ir = (data[0]<<8)|data[1]
		self.MAX30100_avg_red = (data[2]<<8)|data[3]
		self.MAX30100_time  = time.time()


	def MAX30100_set_red_led(self,conf):
		self.MAX30100_RED_INTENSITY = conf
		self.I2CWriteBulk(self.MAX30100_address, [self.MAX30100_REG_LED_CONFIGURATION, (self.MAX30100_RED_INTENSITY<<4)|self.MAX30100_IR_INTENSITY])

	def MAX30100_set_ir_led(self,conf):
		self.MAX30100_IR_INTENSITY = conf
		self.I2CWriteBulk(self.MAX30100_address, [self.MAX30100_REG_LED_CONFIGURATION, (self.MAX30100_RED_INTENSITY<<4)|self.MAX30100_IR_INTENSITY])


	def MAX30100_set_rate(self,rate):
		self.MAX30100_SPO2 = (self.MAX30100_SPO2&0xe3)|(rate<<2)
		self.I2CWriteBulk(self.MAX30100_address, [self.MAX30100_REG_SPO2_CONFIGURATION, self.MAX30100_SPO2])

	def MAX30100_set_pulse(self,conf):
		self.MAX30100_SPO2 = (self.MAX30100_SPO2&0xfc)|(conf)
		self.I2CWriteBulk(self.MAX30100_address, [self.MAX30100_REG_SPO2_CONFIGURATION, self.MAX30100_SPO2])

	def MAX30100_all(self):
		data = self.I2CReadBulk(self.MAX30100_address, self.MAX30100_REG_FIFO_DATA ,8)
		self.MAX30100_BUF_IR.append((data[0]<<8)|data[1])
		self.MAX30100_BUF_RED.append((data[2]<<8)|data[3])
		
		if(time.time() - self.MAX30100_time >5): #Every 5 seconds
			self.MAX30100_avg_red = np.average(self.MAX30100_BUF_RED[-400:])
			self.MAX30100_avg_ir = np.average(self.MAX30100_BUF_IR[-400:])

		#t_int = self.I2CReadBulk(self.MAX30100_address, self.MAX30100_REG_TEMPERATURE_DATA_INT ,1)[0]
		#t_frac = self.I2CReadBulk(self.MAX30100_address, self.MAX30100_REG_TEMPERATURE_DATA_FRAC ,1)[0]
		#temp = t_int+ 0.0625*t_frac

		return [self.MAX30100_BUF_IR[-1] - self.MAX30100_avg_ir,self.MAX30100_BUF_RED[-1] - self.MAX30100_avg_red]

		'''
		#Ignore the FIFO nonsense . I only want to see the latest point.
		self.MAX30100_WRITEPOS = self.I2CReadBulk(self.MAX30100_address, self.MAX30100_REG_FIFO_WRITE_POINTER ,1)
		self.MAX30100_READPOS = self.I2CReadBulk(self.MAX30100_address, self.MAX30100_REG_FIFO_READ_POINTER ,1)
		if(len(self.MAX30100_WRITEPOS) and len(self.MAX30100_READPOS)):
			toRead = (self.MAX30100_WRITEPOS[0] - self.MAX30100_READPOS[0]) & (self.MAX30100_FIFO_DEPTH-1)
			time.sleep(0.01)
			data = self.I2CReadBulk(self.MAX30100_address, self.MAX30100_REG_FIFO_DATA ,toRead*4)
			print(toRead,len(data))
			if len (data) == toRead*4:
				for i in range(toRead):
					self.MAX30100_BUF_IR.append((data[i*4]<<8)|data[i*4+1])
					self.MAX30100_BUF_RED.append((data[i*4+2]<<8)|data[i*4+3])
			else:
				print('read mismatch:',toRead,data)
		else:
			print('Comm err')
		if(len(self.MAX30100_BUF_IR)):
			return [self.MAX30100_BUF_IR[-1],self.MAX30100_BUF_RED[-1]]
		'''



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
		vals = self.I2C.readBulk(self.HMC5883L_ADDRESS,addr,bytes) 
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


	####################### QMC5883L MAGNETOMETER ###############

	QMC5883L_ADDRESS = 13
	QMC_scaling = 3000

	def QMC5883L_init(self):
		self.I2CWriteBulk(self.QMC5883L_ADDRESS,[0x0A,0x80]) #0x80=reset. 0x40= rollover
		self.I2CWriteBulk(self.QMC5883L_ADDRESS,[0x0B,0x01]) #init , set/reset period
		self.I2CWriteBulk(self.QMC5883L_ADDRESS,[0x09,0b001|0b000 | 0b100 | 0b10000]) #Mode. continuous|oversampling(512) | rate 50Hz | range(8g)


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
				return [np.int16(vals[a*2+1]&0xff<<8|vals[a*2]&0xff)/self.QMC_scaling for a in range(3)]
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
	
	def ADS1115_init(self):
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
