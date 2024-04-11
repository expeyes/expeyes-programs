from __future__ import print_function
from numpy import int16
import time, struct


def connect(route, **args):
    return VL53L01X(route, **args)

def makeuint16(lsb, msb):
	return ((msb & 0xFF) << 8)  | (lsb & 0xFF)


class VL53L01X:
    VL53L0X_REG_IDENTIFICATION_MODEL_ID = 0x00c0
    VL53L0X_REG_IDENTIFICATION_REVISION_ID = 0x00c2
    VL53L0X_REG_PRE_RANGE_CONFIG_VCSEL_PERIOD = 0x0050
    VL53L0X_REG_FINAL_RANGE_CONFIG_VCSEL_PERIOD = 0x0070
    VL53L0X_REG_SYSRANGE_START = 0x000

    VL53L0X_REG_RESULT_INTERRUPT_STATUS = 0x0013
    VL53L0X_REG_RESULT_RANGE_STATUS = 0x0014

    VL53L0X_address = 0x29  # 41

    def __init__(self, I2C):
        self.I2CWriteBulk = I2C.writeBulk
        self.I2CReadBulk = I2C.readBulk
        val1 = self.I2CReadBulk(self.VL53L0X_address, self.VL53L0X_REG_IDENTIFICATION_REVISION_ID, 1)[0]
        print ("Revision ID: " + hex(val1))
        val1 = self.I2CReadBulk(self.VL53L0X_address, self.VL53L0X_REG_IDENTIFICATION_MODEL_ID, 1)[0]
        print ("Device ID: " + hex(val1))
        val1 = self.I2CReadBulk(self.VL53L0X_address, self.VL53L0X_REG_PRE_RANGE_CONFIG_VCSEL_PERIOD, 1)[0]
        print ("PRE_RANGE_CONFIG_VCSEL_PERIOD=" + hex(val1) + " decode: " + str(self.VL53L0X_decode_vcsel_period(val1)))
        val1 = self.I2CReadBulk(self.VL53L0X_address, self.VL53L0X_REG_FINAL_RANGE_CONFIG_VCSEL_PERIOD, 1)[0]

        # print ("FINAL_RANGE_CONFIG_VCSEL_PERIOD=" + hex(val1) + " decode: " + str(self.VL53L0X_decode_vcsel_period(val1)))

    def VL53L0X_decode_vcsel_period(self, vcsel_period_reg):
        vcsel_period_pclks = (vcsel_period_reg + 1) << 1;
        return vcsel_period_pclks

    def getRaw(self):
        return self.getVals()

    def getVals(self):
        val1 = self.I2CWriteBulk(self.VL53L0X_address, [self.VL53L0X_REG_SYSRANGE_START, 0x01])
        cnt = 0
        while (cnt < 100):  # 1 second waiting time max
            time.sleep(0.010)
            val = self.I2CReadBulk(self.VL53L0X_address, self.VL53L0X_REG_RESULT_RANGE_STATUS, 1)[0]
            if (val & 0x01):
                break
            cnt += 1
        if (cnt == 100):  # timeout
            return None
        if not (val & 0x01):  # Not ready.
            return None

        #	Status = VL53L0X_ReadMulti(Dev, 0x14, localBuffer, 12);
        data = self.I2CReadBulk(self.VL53L0X_address, 0x14, 12)
        # print ("ambient count " + str(makeuint16(data[7], data[6])))
        # print ("signal count " + str(makeuint16(data[9], data[8])))
        d = makeuint16(data[11], data[10])

        DeviceRangeStatusInternal = ((data[0] & 0x78) >> 3)
        # print (DeviceRangeStatusInternal)

        return [d]
