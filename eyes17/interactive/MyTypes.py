from enum import Enum
import math
from decimal import Decimal


class DisplayTypes(Enum):
    TEXT = 0
    GAUGE = 1


class GraphTypes(Enum):
    LOGGER = 0
    XYLOGGER = 1
    SCOPE = 2


class IOClassification(Enum):
    MEASURE = 0
    SET = 1
    DERIVED = 2
    GRAPH = 3


class commandId(Enum):
    NULL = 0
    CAPTURE1 = 1
    CAPTURE2 = 2
    CAPTURE4 = 3
    FETCH = 4
    CAPTURE_ACTION = 5
    CAPTURE_SCAN = 6
    SCOPEPROGRESS = 7
    SCOPEPROGRESSANDFETCH = 8
    SET_PV1 = 9
    SET_PV2 = 10
    SET_PCS = 11
    SET_WG = 12
    SET_WG_AMP = 13
    SET_SQ1 = 14
    SET_SQ1_DC = 15
    SET_SQ2_DC = 16
    SET_SQ1_DC_ONLY = 17
    SET_SQ2_DC_ONLY = 18
    SET_SQ2 = 19
    SET_SQ12_PHASE = 20
    TRIGGER = 21
    GET_VOLTAGE = 22
    GET_ACSTATS = 23
    SET_AD9833 = 24
    SET_AD9833_1 = 25
    SET_AD9833_2 = 26
    SET_AD9833_PHASE = 27
    SET_DUAL_AD9833 = 28
    SET_TCA9548 = 29
    SET_PCA9685 = 30
    SET_PCA9685_1 = 31
    SET_PCA9685_2 = 32
    SET_PCA9685_3 = 33
    SET_PCA9685_4 = 34
    SELECT_RANGE_RAW = 35
    GET_FREQUENCY = 36
    SR04_DISTANCE = 37
    SR04_DISTANCE_PRECISE = 38
    PT1000 = 39
    INIT_SENSOR = 40
    INIT_SENSOR_WITH_ADDRESS = 41
    GET_SENSOR = 42
    RUNNING = 43
    SET_STATE = 44
    R2R_TIME = 45
    R2F_TIME = 46
    F2R_TIME = 47
    F2F_TIME = 48
    MULTI_R2R = 49
    DUTY_CYCLE = 50
    DUTY_CYCLE_SEN = 51
    DUTY_CYCLE_IN2 = 52
    SET_MULTIPLEXER = 53
    EDGES_ACTION = 54
    CONNECTION_STATUS = 55
    CAPACITANCE = 56
    RESISTANCE = 57


class IoTypes(Enum):
    VOLTMETER = 0
    ACVOLTMETER = 1
    VOLTAGESOURCE = 2
    CURRENTSOURCE = 3
    WAVEGEN = 4
    DERIVED = 5
    MISSING = 6
    I2CSENSOR = 7
    DIGITALINPUT = 8
    DIGITALOUTPUT = 9
    ANALYSIS = 10
    CAPTURE = 11
    RECORD = 12
    CAPACITANCE = 13
    EDITABLE = 14
    BUTTON = 15


class Measurement:
    prefixes = {
        0: '',
        3: 'k',
        6: 'M',
        9: 'G',
        12: 'T',
        -3: 'm',
        -6: 'u',
        -9: 'n',
        -12: 'p',
        -15: 'f'
    }

    def __init__(self, val, type):
        self.value = val
        self.mantissa = val
        self.type = type
        self.order = 0
        self.outOfRange = False
        self.text = ""

        if self.value == 0:
            self.text = "0 " + self.type
            return

        while abs(self.mantissa) > 1000.0 and self.order < 12:
            self.mantissa /= 1000.0
            self.order += 3

        while abs(self.mantissa) < 1.0 and self.order >= -9:
            self.mantissa *= 1000.0
            self.order -= 3

        self.text = f"{'%.5g' % (self.mantissa)} {self.prefixes.get(self.order, '')}{self.type}"

    def stepDownOrder(self):
        if self.order > -6:
            self.order -= 3

    def stepUpOrder(self):
        if self.order < 12:
            self.order += 3

    def getUnits(self):
        return f"{self.prefixes.get(self.order, '')}{self.type}"

    def format(self, val):
        fval = val / math.pow(10, self.order)
        if abs(fval) > 100:
            return '%.4g' % fval
        if abs(fval) > 10:
            return '%.3g' % fval
        else:
            return '%.5g' % fval

    def format3(self, val):
        fval = val / math.pow(10, self.order)
        if abs(fval) > 100:
            return str(int(fval))
        if abs(fval) > 10:
            return '%.5g' % fval
        else:
            return '%.4g' % fval

    def format1(self):
        return f"{'%.3g' % (self.mantissa)} {self.prefixes.get(self.order, '')}{self.type}"

    def format2(self):
        return f"{'%.4g' % (self.mantissa)} {self.prefixes.get(self.order, '')}{self.type}"

    def format3(self):
        return f"{'%.5g' % (self.mantissa)} {self.prefixes.get(self.order, '')}{self.type}"

    def format4(self, val):
        fval = val / math.pow(10, self.order)
        if abs(fval) > 1000:
            return str(int(fval))
        if abs(fval) > 100:
            return '%.3g' % fval
        if abs(fval) > 10:
            return '%.4g' % fval
        else:
            return '%.5g' % fval

    def formattedVoltage(self):
        if self.order == 0:
            if abs(self.value) < 5:
                return f"{'%.4g' % self.mantissa} {self.prefixes.get(self.order, '')}{self.type}"
            else:
                return f"{'%.2g' % self.mantissa} {self.prefixes.get(self.order, '')}{self.type}"
        elif self.order == -3:
            return f"{int(self.mantissa)} {self.prefixes.get(self.order, '')}{self.type}"
        elif self.order < -3:
            return f"0 {self.type}"
        else:
            return "Error"

    def formattedFrequency(self):
        if self.order == 3:  # kHz
            return f"{'%.4g' % self.mantissa} {self.prefixes.get(self.order, '')}{self.type}"
        else:  # Hz / mHz
            return f"{'%.4g' % self.mantissa} {self.prefixes.get(self.order, '')}{self.type}"
