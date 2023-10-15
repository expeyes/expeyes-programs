# I2C Communication interface

The I2C interface consists of 2 pins:

+ SCL, also known as the clock pin. PC0 on Atmega32
+ SDA, also known as the data pin. PC1 on Atmega32

With these two connections, it is possible to get data from a variety of sensors measuring
physical parameters. Visit the [sensors page](../../sensors) for details on using them via the GUI.


## I2C function calls

```python tab="I2CScan" hl_lines="1"
def I2CScan()
scan the I2C bus, and return a list of addresses that responded

  return: list of numbers between 0-127.

```

```python tab="I2CWriteBulk" hl_lines="1"
def I2CWriteBulk(address,bytestream)
write a set of bytes to an I2C address

  address: Address of I2C slave device. 0-127
  bytestream: list of bytes to write
  return: True if success.

```

```python tab="I2CReadBulk" hl_lines="1"
def I2CReadBulk(address,register,total_bytes)
write a set of bytes to an I2C address

  address: Address of I2C slave device. 0-127
  register: The starting address in the I2C slave device from where bytes are to be read
  total_bytes: Total number of bytes to read
  return: bytes, timeout
  "ignore contents if timeout==True"

```


```python tab="MPU6050 example"  hl_lines="1"
# read values from MPU6050 accelerometer+gyro with address 0x68. refer datasheet.
from kuttyPy import *
I2CWriteBulk(0x68,[0x1B,0<<3]) #250-> Gyro Range . 250,500,1000,2000 -> 0,1,2,3 -> shift left by 3 positions
I2CWriteBulk(0x68,[0x1C,0<<3]) #2-> Accelerometer Range. 2,4,8,16 -> 0,1,2,3 -> shift left by 3 positions
I2CWriteBulk(0x68,[0x6B, 0x00]) #poweron

bytevalues,timeout = self.I2CReadBulk(0x68, 0x3B ,14)
if not timeout:
	values = [(bytevalues[x*2+1]<<8)|b[x*2] for x in range(7)] #Ax,Ay,Az,temp,Gx,Gy,Gz are 16-bit from 2 b-bit each.
	print('Ax = %d, Ay = %d, Az = %d'%(values[0],values[1],values[2]))
	print('Gx = %d, Gy = %d, Gz = %d'%(values[4],values[5],values[6]))

```


## Pre-Supported I2C Sensors

  - MPU6050 3 Axis Accelerometer, 3 axis Angular velocity (Gyro)
  - MPU9250 9-DOF sensor
  - MS5611 : 24 bit pressure and temperature sensor. Can resolve 15cm height variations
  - TSL2561 Luminosity measurements
  - BMP280 Pressure and Temperature sensor
  - MCP4725 Single channel DAC
  - PCA9685 PWM controller
  - MLX90614 Passive IR


### MPU6050 accelerometer + gyroscope
The MPU6050 is a Micro Electro-Mechanical Systems (MEMS) which consists of a 3-axis Accelerometer
 and 3-axis Gyroscope inside it. It can measure acceleration, velocity, orientation,
 and many other motion related parameters. Commonly used in drones for stability feedback,
 it also has a lot of potential applications in Physics Experiments.

```python hl_lines="1"
def MPU6050_init()
initialize the MPU6050 sensor(address=0x68), and set ranges to max sensitivity.
```

```python hl_lines="1"
def MPU6050_gyro_range(range)
set the sensitivity of the gyroscope
range: 0,1,2 or 3 corresponding to +-250,+-500,+-1000,+-2000
```

```python hl_lines="1"
def MPU6050_accel_range(range)
set the sensitivity of the accelerometer
range: 0,1,2 or 3 corresponding to +-2,+-4,+-8,+-16
```


```python hl_lines="1"
def MPU6050_kalman_set(value)
Enable a moving average to reduce noise level of the sensor.
Useful to reject high frequency oscillations.
fetches 50 values, and activates a Kalman filter. To ignore an activated Kalman Filter, an optional False value can be supplied to `MPU6050_all`

value: kalman averaging coefficient. Float.
```


```python hl_lines="1"
def MPU6050_all()
fetch values from the sensor
return: list of 7 16-bit integers
```

Example with MPU6050

```python
from kuttyPy import *
MPU6050_init() #Initialize the sensor
x = MPU6050_all() #Fetch readings
if x is not None:
	print('Ax = %d, Ay = %d, Az = %d'%(x[0],x[1],x[2]))
	print('Gx = %d, Gy = %d, Gz = %d'%(x[4],x[5],x[6]))

```

### TSL2561 Luminosity sensor
The TSL2561  is a light sensor which has a
linear response across most of the visible spectrum. It has two photodiodes
with corrresponding ADCs, and a very wide range of operation. Ideal for optics experiments


```python hl_lines="1"
def TSL2561_init()
initialize the TSL2561 sensor(address=0x39).
```

```python hl_lines="1"
def TSL2561_gain(gain)
set the gain
gain: 0 => 1x , 1 => 16x
```

```python hl_lines="1"
def TSL2561_timing(timing)
set the integration time : 3mS , 101mS, 403mS
timing: 0 => 3mS , 1 => 101mS, 2 => 403mS
```

```python hl_lines="1"
def TSL2561_all()
fetch values from the sensor
return: list of 3 integers.  Total light, IR luminous intensity
```

Example with TSL2561

```python
from kuttyPy import *
TSL2561_init() #Initialize the sensor
x = TSL2561_all() #Fetch readings
if x is not None:
	print('Total Light = %d, Infrared = %d'%(x[0],x[1]))

```


### BMP280 Pressure and temperature sensor
BMP280 is an absolute barometric pressure sensor developed by Bosch Sensortec.
The sensor module is housed in an extremely compact package, and is very handy to
demonstrate physics concepts to high school students.

```python tab="BMP280_init" hl_lines="1"
def BMP280_init()
initialize the BMP280 sensor(address=118).
```

```python tab="BMP280_all" hl_lines="1"
def BMP280_all()
fetch values from the sensor
return: list of 2 integers.  Pressure(mBar), Temperature(C)
```

```python tab="Example"
from kuttyPy import *
BMP280_init() #Initialize the sensor
x = BMP280_all() #Fetch readings
if x is not None:
	print('Pressure = %.2f, Temperature = %.2f'%(x[0],x[1]))
```


### MS5611 Pressure and temperature sensor
MS5611 is a high resolution altimeter developed by MEAS.
It has better resolution than the BMP280, and about 15cm height difference can be resolved.

```python tab="MS5611_init" hl_lines="1"
def MS5611_init()
initialize the MS5611 sensor(address=119).
```

```python tab="MS5611_all" hl_lines="1"
def MS5611_all()
fetch values from the sensor
return: list of 2 integers.  Pressure(mBar), Temperature(C)
```

```python tab="Example"
from kuttyPy import *
MS5611_init() #Initialize the sensor
x = MS5611_all() #Fetch readings
if x is not None:
	print('Pressure = %.2f, Temperature = %.2f'%(x[0],x[1]))
```

### TCS34725 RGB color sensor

```python tab="TCS34725_init" hl_lines="1"
def TCS34725_init()
initialize the TCS34725 sensor(address=41).
```

```python tab="TCS34725_all" hl_lines="1"
def TCS34725_all()
fetch values from the sensor
return: list of 3 integers.  [Red, Green, Blue]
```

```python tab="TCS34725_gain" hl_lines="1"
def TCS34725_gain(gain)
set the gain of the sensor
gain: 0,1,2,3 => 1x,4x,16x,60x
```

```python tab="Example"
from kuttyPy import *
TCS34725_init() #Initialize the sensor
x = TCS34725_all() #Fetch readings
if x is not None:
	print(x)
```


### MLX90614 passive IR
The MLX90614 is an infrared thermometer for non-contact temperature measurements made by Melexis
Both the IR sensitive thermopile detector chip and the signal conditioning ASIC are
integrated in the same TO-39 can.

```python tab="MLX90614_init" hl_lines="1"
def MLX90614_init()
initialize the sensor(address=0x5A).
```

```python tab="MLX90614_all" hl_lines="1"
def MLX90614_all()
fetch values from the sensor
return: [Temperature] in degree celcius
```


```python tab="Example"
from kuttyPy import *
MLX90614_init() #Initialize the sensor
x = MLX90614_all() #Fetch readings
if x is not None:
	print(x[0])
```


## Output devices with I2C

### MCP4725 DAC
MCP4725 is a single-channel 12-bit Digital to Analog converter from Microchip Technology.

```python tab="MCP4725_init" hl_lines="1"
def MCP4725_init()
initialize the MCP4725 DAC(address=0x60).
```

```python tab="MCP4725_set" hl_lines="1"
def MCP4725_all(value)
write a 12 bit number to the DAC
value: 0 - 4095
```

```python tab="Example"
from kuttyPy import *
MCP4725_init() #Initialize the DAC
MCP4725_set(1024) #Write
```

### PCA9685 PWM generator
PCA9685 is a 16-channel PWM generator. It can be used to adjust brightness of LEDs via high frequency output,
or for controlling servo motors in a low-frequency mode. The emphasis is currently on driving SG-90 servos

```python tab="PCA9685_init" hl_lines="1"
def PCA9685_init()
initialize the PCA9685 (address = 64).
```

```python tab="PCA9685_set" hl_lines="1"
def PCA9685_set(channel, angle)
channel: 1-16 . Channel number for configuring
angle: 0 - 180
```

```python tab="Example"
from kuttyPy import *
PCA9685_init() #Initialize the DAC
PCA9685_set(1,90) #Servo using PWM signal from channel 1 will be set to 90 degrees
PCA9685_set(2,90) #Servo using PWM signal from channel 2 will be set to 90 degrees
```

