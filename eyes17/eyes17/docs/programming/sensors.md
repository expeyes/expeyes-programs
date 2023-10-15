# Monitor I2C Sensors

- List of I2C sensors supported thus far (Minimal data logging. Configuration options via the graphical utility might be incomplete)
	- MPU6050 3 Axis Accelerometer, 3 axis Angular velocity (Gyro)
	- MPU9250 9-DOF sensor
	- MS5611 : 24 bit pressure and temperature sensor. Can resolve 15cm height variations
	- TSL2561 Luminosity measurements
	- BMP280 Pressure and Temperature sensor
	- MCP4725 Single channel DAC
	- PCA9685 PWM controller
	- MLX90614 Passive IR

## Luminosity sensor(TSL2561) Example

A light sensor is being monitored with the flash of the camera enabled. As the camera approaches the sensor, the readings go up. Not a very clever example. TODO.

[Project Example with TSL2561 light sensor: Malus Law](../malus)
