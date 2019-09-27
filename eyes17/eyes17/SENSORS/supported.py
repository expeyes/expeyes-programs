# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
import inspect

from . import HMC5883L,MPU6050,MLX90614,BMP180,TSL2561,SHT21,BH1750,SSD1306,ADS1115

supported={
0x68:MPU6050,  #3-axis gyro,3-axis accel,temperature
0x1E:HMC5883L, #3-axis magnetometer
0x5A:MLX90614, #Passive IR temperature sensor
0x77:BMP180,   #Pressure, Temperature, altitude
0x39:TSL2561,  #Luminosity
0x40:SHT21,    #Temperature, Humidity
0x48:ADS1115,   #16-bit ADC
0x23:BH1750,    #Luminosity
#0x3C:SSD1306,    #OLED display
}


#auto generated map of names to classes
nameMap = {}
for a in supported:
		nameMap[supported[a].__name__.split('.')[-1]]=(supported[a])
