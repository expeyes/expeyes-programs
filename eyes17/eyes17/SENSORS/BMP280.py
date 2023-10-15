from __future__ import print_function
from numpy import int16
import time, struct


def connect(route, **args):
    return BMP280(route, **args)


class BMP280:
    ####### BMP280 ###################
    # https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf
    ## Partly from https://github.com/farmerkeith/BMP280-library/blob/master/farmerkeith_BMP280.cpp
    BMP280_ADDRESS = 118
    BMP280_REG_CONTROL = 0xF4
    BMP280_REG_RESULT = 0xF6
    BMP280_HUMIDITY_ENABLED = False
    _BMP280_humidity_calib = [0] * 6
    BMP280_oversampling = 0
    _BMP280_PRESSURE_MIN_HPA = 0
    _BMP280_PRESSURE_MAX_HPA = 1600
    _BMP280_sea_level_pressure = 1013.25  # for calibration.. from circuitpython library

    def __init__(self, I2C):
        self.I2CWriteBulk = I2C.writeBulk
        self.I2CReadBulk = I2C.readBulk

        b = self.I2CWriteBulk(self.BMP280_ADDRESS, [0xE0, 0xB6])  # reset
        time.sleep(0.1)
        self.BMP280_HUMIDITY_ENABLED = False
        b = self.I2CReadBulk(self.BMP280_ADDRESS, 0xD0, 1)
        print(b)
        if b is None:
            return
        b = b[0]
        if b in [0x58, 0x56, 0x57]:
            print('BMP280. ID:', b)
        elif b == 0x60:
            self.BMP280_HUMIDITY_ENABLED = True
            print('BME280 . includes humidity')
        else:
            print('ID unknown', b)
        # get calibration data
        b = self.I2CReadBulk(self.BMP280_ADDRESS, 0x88, 24)  # 24 bytes containing calibration data
        coeff = list(struct.unpack('<HhhHhhhhhhhh', bytes(b)))
        coeff = [float(i) for i in coeff]
        self._BMP280_temp_calib = coeff[:3]
        self._BMP280_pressure_calib = coeff[3:]
        self._BMP280_t_fine = 0.

        if self.BMP280_HUMIDITY_ENABLED:
            self.I2CWriteBulk(self.BMP280_ADDRESS, [0xF2, 0b101])  # ctrl_hum. oversampling x 16
            # humidity calibration read
            self._BMP280_humidity_calib = [0] * 6
            self._BMP280_humidity_calib[0] = self.I2CReadBulk(self.BMP280_ADDRESS, 0xA1, 1)[0]  # H1
            coeff = self.I2CReadBulk(self.BMP280_ADDRESS, 0xE1, 7)
            coeff = list(struct.unpack('<hBbBbb', bytes(coeff)))
            self._BMP280_humidity_calib[1] = float(coeff[0])
            self._BMP280_humidity_calib[2] = float(coeff[1])
            self._BMP280_humidity_calib[3] = float((coeff[2] << 4) | (coeff[3] & 0xF))
            self._BMP280_humidity_calib[4] = float((coeff[4] << 4) | (coeff[3] >> 4))
            self._BMP280_humidity_calib[5] = float(coeff[5])

        self.I2CWriteBulk(self.BMP280_ADDRESS, [0xF4, 0xFF])  # ctrl_meas (oversampling of pressure, temperature)

    def _BMP280_calcTemperature(self, adc_t):
        v1 = (adc_t / 16384.0 - self._BMP280_temp_calib[0] / 1024.0) * self._BMP280_temp_calib[1]
        v2 = ((adc_t / 131072.0 - self._BMP280_temp_calib[0] / 8192.0) * (
                adc_t / 131072.0 - self._BMP280_temp_calib[0] / 8192.0)) * self._BMP280_temp_calib[2]
        self._BMP280_t_fine = int(v1 + v2)
        return (v1 + v2) / 5120.0  # actual temperature.

    def _BMP280_calcPressure(self, adc_p, adc_t):
        self._BMP280_calcTemperature(adc_t)  # t_fine has been set now.
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
            return self._BMP280_PRESSURE_MIN_HPA
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

    def _BMP280_calcHumidity(self, adc_h, adc_t):
        self._BMP280_calcTemperature(adc_t)  # t fine set.
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

    def getVals(self):
        if self.BMP280_HUMIDITY_ENABLED:
            data = self.I2CReadBulk(self.BMP280_ADDRESS, 0xF7, 8)
        else:
            data = self.I2CReadBulk(self.BMP280_ADDRESS, 0xF7, 6)
        if data is None: return None
        if None not in data:
            # Convert pressure and temperature data to 19-bits
            adc_p = (((data[0] & 0xFF) * 65536.) + ((data[1] & 0xFF) * 256.) + (data[2] & 0xF0)) / 16.
            adc_t = (((data[3] & 0xFF) * 65536.) + ((data[4] & 0xFF) * 256.) + (data[5] & 0xF0)) / 16.
            if self.BMP280_HUMIDITY_ENABLED:
                adc_h = (data[6] * 256.) + data[7]
                return [self._BMP280_calcPressure(adc_p, adc_t), self._BMP280_calcTemperature(adc_t),
                        self._BMP280_calcHumidity(adc_h, adc_t)]
            else:
                return [self._BMP280_calcPressure(adc_p, adc_t), self._BMP280_calcTemperature(adc_t), 0]

        return None

    def readPressure(self):
        x = self.getVals()
        if x:
            return x[0]

    def readTemperature(self):
        x = self.getVals()
        if x:
            return x[1]

    def readHumidity(self):
        x = self.getVals()
        if x:
            return x[2]

    def altitude(self):
        # baseline pressure needs to be provided
        return (44330.0 * (1 - pow(self.P / self.baseline, 1 / 5.255)))

    def sealevel(self, P, A):
        '''
		given a calculated pressure and altitude, return the sealevel
		'''
        return (P / pow(1 - (A / 44330.0), 5.255))
