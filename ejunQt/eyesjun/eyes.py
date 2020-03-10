# -*- coding: utf-8 -*-
'''
EYES for Young Engineers and Scientists -Junior (EYES Junior 1.0)
Python library to communicate to the PIC24FV32KA302 uC running 'eyesj.c'
Author  : Ajith Kumar B.P, bpajith@gmail.com, ajith@iuac.res.in
License : GNU GPL version 3
Started on 25-Mar-2012
Last edit : 25-Oct-2012, added storing calibration to EEPROM
*
The micro-controller pins used are mapped into 13 I/O channels (numbered 0 to 12)
and act like a kind of logical channels.  The Python function calls refer to them
using the corresponding number, ie 0 => A0. 

 * 0 : A0, Analog Comaparator(A5) output.
 * 1 : A1, -5V to +5V range Analog Input 
 * 2 : A2, -5V to +5V range Analog Input 
 * 3 : IN1 , Can function as Digital or 0 to 5V Analog Input
 * 4 : IN2, Can function as Digital or 0 to 5V Analog Input
 * 5 : SEN, Simial to A3 & A4, but has a 5K external pullup resistor (Comp input)
 * 6 : SQR1-read, Input wired to SQR1 output
 * 7 : SQR2-read,  Input wired to SQR2 output
 * 8 : SQR1 control, 0 to 5V programmable Squarewave. Setting Freq = 0 means 5V, Freq = -1 means 0V
 * 9 : SQR2 control, 0 to 5V programmable Squarewave
 * 10: Digital output OD1, 
 * 11: CCS, Controls the 1mA constant current source. 
 * A12: Analog Input  AN0 / RA0  (dummy entry for RA0), special case
'''

import serial, struct, numpy, time, subprocess, sys, os, os.path

fileOpen=open

# allows to pack numeric values into byte strings
Byte =     struct.Struct("B") # size 1
ShortInt = struct.Struct("H") # size 2
Integer=   struct.Struct("I") # size 4

#Commands with One byte argument (41 to 80) 
GETVERSION  =   Byte.pack(1)
READCMP     =   Byte.pack(2)       # Status of comparator output 
READTEMP    =   Byte.pack(3)       # IC Temperature
GETPORTB    =   Byte.pack(4)

#Commands with One byte argument (41 to 80)
READADC        =    Byte.pack(41)  # Read the ADC channel
GETSTATE    =   Byte.pack(42)      # Digital Input Status
NANODELAY   =   Byte.pack(43)      # from IN2 to SEN, using CTMU, send current range
SETADCREF   =   Byte.pack(44)      # non-zero value selects external +Vref option
READADCSM   =    Byte.pack(45)     # Read the ADC channel, in Sleep Mode
IRSEND1     =   Byte.pack(46)      # Sends one byte over IR on SQR1
RDEEPROM    =   Byte.pack(47)      # Read nwords starting from addr

# Commands with Two bytes argument (81 to 120)
R2RTIME     =   Byte.pack(81)  # Time from rising edge to rising edge,arguments pin1 & pin2
R2FTIME     =   Byte.pack(82)      
F2RTIME     =   Byte.pack(83)      
F2FTIME     =   Byte.pack(84)      
MULTIR2R    =   Byte.pack(85)  # Time between rising edges, arguments pin & skipcycles    
SET2RTIME   =   Byte.pack(86)  # From a Dout transition to the Din transition
SET2FTIME   =   Byte.pack(87)  #
CLR2RTIME   =   Byte.pack(88)  #   
CLR2FTIME   =   Byte.pack(89)  #    
HTPUL2RTIME =   Byte.pack(90)  # High True Pulse to HIGH
HTPUL2FTIME =   Byte.pack(91)  # High True Pulse to LOW
LTPUL2RTIME =   Byte.pack(92)  #
LTPUL2FTIME =   Byte.pack(93)  #
SETPULWIDTH =   Byte.pack(94)  # Width setting for PULSE2* functions    
SETSTATE    =   Byte.pack(95)  # SQR1, SQR2, OD & CCS only
SETDAC      =   Byte.pack(96)  # 12 bit DAC setting
SETCURRENT  =   Byte.pack(97)  # ADC channel, CTMU Irange
SETACTION   =   Byte.pack(98)  # capture modifiers, action, target pin
SETTRIGVAL  =   Byte.pack(99)  # Analog trigger level, 2 bytes
SRFECHOTIME =   Byte.pack(100) # Trigger to Echo time for SRF0x modules

# Commands with Three bytes argument (121 to 160)    
SETSQR1     =  Byte.pack(121)  # Square wave on OSC2
SETSQR2     =  Byte.pack(122)  # Square wave on OSC3
WREEPROM    =  Byte.pack(123)  # write 1 word to the address

#Commands with Four bytes argument (161 to 200)
MEASURECV   = Byte.pack(163)    # ch, irange, duration
SETPWM1     = Byte.pack(164)    # PWM on SQR1 output. Send ocxrx and ocx
SETPWM2     = Byte.pack(165)    # PWM on SQR1 output.
IRSEND4     = Byte.pack(166)    # 4 byte  IR

#Commands with Five bytes argument (201 to 240)
CAPTURE     = Byte.pack(201)    # Ch, 2 byte NS, 2 byte TG 
CAPTURE_HR  = Byte.pack(202)    # Ch, 2 byte NS, 2 byte TG
SETSQRS     = Byte.pack(203)    # Set both square waves, with specified phase difference. scale, ocr, diff

#Commands with Six bytes argument (241 to 255)
CAPTURE2     = Byte.pack(241)   # ch1, ch2, NS, TG (1, 1, 2, 2)bytes
CAPTURE2_HR  = Byte.pack(242)   # ch1, ch2, NS, TG (1, 1, 2, 2)bytes
CAPTURE3     = Byte.pack(243)   # ch1&ch2, ch3, ns , tg
CAPTURE4     = Byte.pack(244)   # ch1&ch2, ch3&ch4, ns , tg

# Actions before capturing waveforms
AANATRIG     = Byte.pack(0)     # Trigger on analog input level, set by SETRIGVAL
AWAITHI      = Byte.pack(1)
AWAITLO      = Byte.pack(2)
AWAITRISE    = Byte.pack(3)
AWAITFALL    = Byte.pack(4)
ASET         = Byte.pack(5)
ACLR         = Byte.pack(6)
APULSEHT     = Byte.pack(7)
APULSELT     = Byte.pack(8)

BUFSIZE      = 1800       # status + adcinfo + 1800 data

#Serial devices to search for EYES hardware.  
linux_list = ['/dev/ttyACM0','/dev/ttyACM1','/dev/ttyACM2', '/dev/ttyACM3', '/dev/ttyAMA0']  

def warningWithResult(warn, res):
    return warn + str(res, encoding="utf-8")

def open(dev = None):
    '''
    If EYES hardware in found, returns an instance of 'Eyes', else returns None.
    '''
    obj = Eyesjun()
    if obj.fd != None:
        obj.disable_actions()     # Disable capture modifiers
        obj.load_calibration()
        return obj
    print (('Could not find EYES Junior hardware'))
    print (('Check the connections.'))

BAUDRATE = 115200                 # Serial communication

class Eyesjun:
    fd = None                     # init should fill this
    connected = False
    calibrated = False
    refval = 5.000                # regulator output, nominal value
    DACMAX = refval               # DAC upper limit
    DACM = 4095.0/refval
    tgap =  0.004                 # 0.004 ms shift between two channels of capture2
    m12 = [refval/4095] + [2*refval/4095]*2 + [refval/4095]*10
    m8 =  [refval/255]  + [2*refval/255] *2 + [refval/255] *10
    c = [0.0] + [-refval]*2 + [0.0]*10
    sen_pullup = 5100.0
    cap_calib = 1.0               # Default values, to be loaded from file.
    socket_cap = 30.0             # Set by calibrate.py
    msg = ''

    def __init__(self, dev = None):
        """
        Searches for EYES hardware on USB-to-Serial adapters. Presence of the
        device is done by reading the version string. Timeout set to 4 sec
        TODO : Supporting more than one EYES on a PC to be done. The question is how to find out 
        whether a port is already open or not, without doing any transactions to it.
        """
        if os.name == 'nt':       # for Windows machines, search COM1 to COM255
            device_list = []
            for k in range(1,255):
                s = 'COM%d'%k
                device_list.append(s)
                for k in range(1,11):
                    device_list.append(k)
        else:
            device_list = []      # Gather unused devices from linux_list
            for dev in linux_list:
                cmd='lsof -t {0} 2>&1; true'.format(dev)
                res = subprocess.check_output(cmd, shell=True)
                if len(res)==0:
                    device_list.append(dev)

        for dev in device_list:
            try:
                handle = serial.Serial(dev, BAUDRATE, stopbits=1, timeout = 0.3) #8,1,no parity
            except:
                continue
            
            print('Port %s is existing '%dev)
            if handle.isOpen() != True:
                print ('but could not open')
                continue
            print('and opened. ')
            handle.flush()
            time.sleep(.5)
            while handle.inWaiting() > 0 :
                handle.flushInput()
            handle.write(GETVERSION)
            res = handle.read(1)
            ver = handle.read(5)        # 5 character version number
            if ver[:2] == b'ej':
                self.device = dev
                self.fd = handle
                self.version = ver
                handle.timeout = 4.0    # r2rtime on .7 Hz require this
                print('Connected to ',ver.decode())
                self.connected = True
                return                  # Successful return
            else:                       # If it is not our device close the file
                handle.close()
            print ('No EYES Junior hardware detected')
            self.fd = None
        return
    #---------------------------------------------------------------------------
    def sendByte(self, bval):
        """
        sends one byte to the interface
        @parameter bval : a bytes of lenght 1
        """
        self.fd.write(bval)
        time.sleep(0.005) # This delay is for MCP2200 + uC
        return
    
    def sendInt(self,ival):
        """
        send on integer to the inteface
        @parameter ival an integer lesser than 65536
        """
        delay=0.005       # This delay is for MCP2200 + uC
        self.fd.write(Byte.pack(ival & 255))
        time.sleep(delay)
        self.fd.write(Byte.pack(ival >> 8))
        time.sleep(delay)
        return
    
    def get_version(self):
        """
        reads the version number from the device
        @return a str
        """
        self.sendByte(GETVERSION)
        res = self.fd.read(1)
        if res != b'D':
            self.msg = warningWithResult('GETVERSION ERROR', ver)
            return
        ver = self.fd.read(5)
        if sys.version_info.major == 3:
            ver=ver.decode("utf-8")
        return ver

    """------------------------EEPROM---------------------"""
    def eeprom_write(self, addr, data):
        """
        writes a few bytes to the EEPROM
        @param addr a small integer
        @param byte an integer (16 bits)
        @return 1 (number of written words)
        """
        self.sendByte(WREEPROM)
        self.sendByte(Byte.pack(addr))
        self.sendInt(data)
        res = self.fd.read(1)
        if res != b'D':
            self.msg =  warningWithResult('WREEPROM ERROR ', res)
            print (warningWithResult('WREEPROM ERROR', res))
            return None
        return 1

    def eeprom_read(self, addr):
        """
        read data from the EEPROM
        @param addr a small integer (8bit)
        @return an integer value (16 bits)
        """
        self.sendByte(RDEEPROM)
        self.sendByte(Byte.pack(addr))
        res = self.fd.read(1)
        if res != b'D':
            self.msg = warningWithResult('RDEEPROM ERROR ', res)
            return None
        res = self.fd.read(2)
        if sys.version_info.major == 3:
            return res[0] | (res[1] << 8)
        else:
            return ord(res[0]) | (ord(res[1]) << 8)

    def store_float(self, addr, data): # store a floating point number to EEPROM
        ss = struct.pack('f', data)
        if sys.version_info.major == 3:
            lo = ss[0] | (ss[1] << 8)
            hi  = ss[2] | (ss[3] << 8)
        else:
            lo = ord(ss[0]) | (ord(ss[1]) << 8)
            hi  = ord(ss[2]) | (ord(ss[3]) << 8)
        if self.eeprom_write(addr, lo) == None:
            return None
        if self.eeprom_write(addr+1, hi) == None:
            return None
        return 1

    def restore_float(self, addr): # restore a floating point number from EEPROM
        lo = self.eeprom_read(addr)
        hi = self.eeprom_read(addr+1)
        data = (hi << 16) | lo
        ss = struct.pack('I', data)
        res = struct.unpack('f', ss)
        return res[0]              # return the float

    AM1  = 0      # EEPROM location of the parameters, y = mx + c, for A1 and A2
    AC1  = 2
    AM2  = 4
    AC2  = 6
    ASOC = 8      # Socket cap IN1
    ACCF = 10     # Capacitance error factor
    ARP  = 12     # Pullup Resistance 

    def storeCF_a1a2(self, m1,c1,m2,c2): # slope & intercept for A1 and A2
        if self.store_float(self.AM1, m1) == None:
            return None
        self.store_float(self.AC1, c1)
        self.store_float(self.AM2, m2)
        self.store_float(self.AC2, c2)
        return 4                         # Number of items written

    def storeCF_cap(self, soc, ccf):     #Socket capacitance and error factor
        if self.store_float(self.ASOC, soc) == None:
            return None
        self.store_float(self.ACCF, ccf)
        return 2

    def storeCF_sen(self, r):            # pullup resistor value
        if self.store_float(self.ARP, r) == None:
            return None
        return 1

    def load_calibration(self):
        ca = cb = cc = False
        try:
            m1 = self.restore_float(self.AM1)
            c1 = self.restore_float(self.AC1)
            m2 = self.restore_float(self.AM2)
            c2 = self.restore_float(self.AC2)
            m = 10.0/4095
            c = -5.0
            dm = m * 0.02            # maximum 2% deviation
            dc = 5 * 0.02
            # print (m1,c1,m2,c2, dm, dc)
            if abs(m1-m) < dm and abs(m2-m) < dm and abs(c1-c) < dc and abs(c2-c) < dc:
                self.m12[1] = m1
                self.c[1] = c1
                self.m12[2] = m2
                self.c[2] = c2
                self.m8[1] = m1 * 4095./255    # Scale factors for 8 bit read
                self.m8[2] = m2 * 4095./255
                ca = True
                # print ('Calibration Factors :', m1,c1,m2,c2)
            else:
                print ('Invalid Calibration factors for A1,A2', m1,c1,m2,c2)
        except:
            print ('Could not load A1 & A2 Calibration')

        try:
            soc = self.restore_float(self.ASOC)
            ccf = self.restore_float(self.ACCF)
            if (.8 < ccf < 1.2) and (20 < soc < 50):
                self.cap_calib = ccf
                self.socket_cap = soc
                cb = True
                #print ('IN1 Calibration :', ccf, soc)
            else:
                print (('Invalid Calibration factors for IN1'), soc, ccf)
        except:
            print (('Could not load IN1 Capacitor Calibration'))

        try:
            r = self.restore_float(self.ARP)
            if 4950 < r < 5250:
                self.sen_pullup = r
                cc = True
                #print (('SEN Pullup :'), r)
            else:
                print (('Invalid Pullup resistor value'), r)
        except:
            print (('Could not load SEN Pullup calibration'))
        
        if ca and cb and cc == True:
            self.calibrated = True
    
    #------------------------- Infrared comm. ----------------
    def irsend1(self, d1):
        """
        send one byte by IR
        @param d1 a small integer (8bit)
        """
        self.sendByte(IRSEND1)
        self.sendByte(Byte.pack(d1))
        res = self.fd.read(1)
        if res != b'D':
            self.msg = warningWithResult(('IRSEND1 ERROR '), res)
            print (warningWithResult(('IRSEND1 ERROR '), res))
            return
        return 1

    def irsend4(self, d1,d2,d3,d4):
        """
        send four bytes by IR
        @param d1 a small integer (8bit)
        @param d2 a small integer (8bit)
        @param d3 a small integer (8bit)
        @param d4 a small integer (8bit)
        """
        self.sendByte(IRSEND4)
        self.sendByte(Byte.pack(d1))
        self.sendByte(Byte.pack(d2))
        self.sendByte(Byte.pack(d3))
        self.sendByte(Byte.pack(d4))
        res = self.fd.read(1)
        if res != b'D':
            self.msg = warningWithResult(('IRSEND4 ERROR '), res)
            print (warningWithResult(('IRSEND4 ERROR '), res))
            return
        return 1

    #--------------------------------------CTMU -------------
    ctmui = [550, 0.55, 5.5, 55.0]
    def nano_delay(self, i):
        '''
        Using the CTMU of PIC, measure r2r from IN2 or SEN. uses cap of IN1. Incomplete
        ch = 3
        self.sendByte(NANODELAY)
        self.sendByte(self.rval[i])
        res = self.fd.read(1)
        if res != b'D':
           print (('MEASUREDELAY ERROR'), res)
           return
        res = self.fd.read(2)
        iv = ord(res[0]) | (ord(res[1]) << 8)
        print (iv)
        v = self.m12[ch] * iv + self.c[ch]
        return v
        '''        
        return

    def measure_cv(self, ch, ctime, i = 5.5):  
        '''
        Using the CTMU of PIC, charges a capacitor connected to IN1, IN2 or SEN,
        for 'ctime' microseconds and then mesures the voltage across it.
        The value of current can be set to .55uA, 5.5 uA, 55uA or 550 uA
        @param ch channel number
        @param ctime duration in microseconds
        @param i value of the current (defaults to 5.5 uA)
        '''
        if i > 500:        # 550 uA
            irange = 0
        elif i > 50:       #55 uA
            irange = 3
        elif i > 5:        #5.5 uA,  default value
            irange = 2
        else:              # 0.55 uA
            irange = 1
            
        if ch not in [3,4]:
            self.msg = ('Current to be set only on IN1(3) or IN2(4)')
            print (('Current to be set only on IN1 or IN2'))
            return
        self.sendByte(MEASURECV)
        self.sendByte(Byte.pack(ch))
        self.sendByte(Byte.pack(irange))
        self.sendInt(ctime)
        res = self.fd.read(1)
        if res != b'D':
            self.msg = warningWithResult(('MEASURECV ERROR '), res)
            print (warningWithResult(('MEASURECV ERROR '), res))
            return 
        res = self.fd.read(2)
        if sys.version_info.major == 3:
            iv = res[0] | (res[1] << 8)
        else:
            iv = ord(res[0]) | (ord(res[1]) << 8)
        v = self.m12[ch] * iv + self.c[ch]
        return v

    def measure_cap_raw(self, ctmin = 10):
        '''
        Measures the capacitance connected between IN1 and GND. Stray
        capacitance should be subtracted from the measured
        value. Measurement is done by charging the capacitor with 5.5 uA
        for a given time interval. Any error in the value of current
        is corrected by calibrating.
        '''
        for ctime in range(ctmin, 1000, 10):
            v = self.measure_cv(3, ctime, 5.5)   # 5.5 uA range is chosen
            if v > 2.0: break
            if (v > 4) or (v == 0):
                self.msg = ('Error measuring capacitance %5.3f') %v
                print (('Error measuring capacitance'), v)
                return None
        return 5.5 * ctime / v                   # returns value in pF 

    def measure_cap(self, ctmin = 10):
        '''
        Measures the capacitance connected between IN1 and GND.
        Returns the value after applying corrections.
        '''
        cap = self.measure_cap_raw()
        if cap != None:
            return (cap - self.socket_cap) * self.cap_calib
        else:
            return None

    def measure_res(self):
        '''
        Measures the resistance connected between SEN and GND.
        '''
        v = self.get_voltage(5)
        if .1 < v < 4.9:
            return 1.0 * self.sen_pullup * v /(5-v)
        else:
            self.msg = ('Resistance NOT in 100 Ohm to 100 kOhm range')
            return 

    def set_current(self, ch, i): # channel 3 or 4, 0 means stop CTMU
        '''
        Sets CTMU current 'i' on a channel 'ch' and returns the voltage measured
        across the load. Allowed values of current are .55, 5.5, 55 and
        550 uAmps.
        @param ch channel number
        @param i value of the current
        '''
        if i > 500:            # 550 uA
            irange = 0
        elif i > 50:           #55 uA
            irange = 3
        elif i > 5:            #5.5 uA,  default value
            irange = 2
        else:                  # 0.55 uA
            irange = 1
        if i == 0 :            # indication to stop CTMU
            ch = 0 
        if ch not in [0,3,4]:  # 0 means stopping CTMU
            self.msg = ('Current to be set only on IN1 or IN2')
            print (('Current to be set only on IN1 or IN2'))
            return
        self.sendByte(SETCURRENT)
        self.sendByte(Byte.pack(ch))
        self.sendByte(irange)
        res = self.fd.read(1)
        if res != b'D':
            self.msg = warningWithResult(('SETCURRENT ERROR'), res)
            print (warningWithResult(('SETCURRENT ERROR'), res))
            return 
        res = self.fd.read(2)
        if sys.version_info.major == 3:
            iv = res[0] | (res[1] << 8)
        else:
            iv = ord(res[0]) | (ord(res[1]) << 8)
        v = self.m12[ch] * iv + self.c[ch]
        return v

    def read_temp(self):
        '''
        Reads the temperature of uC, currently of no use. Have to see
        whether this can be used for correcting the drift of the 5V
        regulator with temperature.
        '''
        self.sendByte(READTEMP)
        res = self.fd.read(1)
        if res != b'D':
            print (('READTEMP error '), res)
            self.msg = warningWithResult(('READTEMP error'),res)
            return
        res = self.fd.read(2)
        if sys.version_info.major == 3:
            iv = res[0] | (res[1] << 8)
        else:
            iv = ord(res[0]) | (ord(res[1]) << 8)
        return iv

    #---------- Time Interval Measurements ----------------------

    def tim_helper(self, cmd, src, dst):
        '''
        Helper function for all Time measurement calls. Command,
        Source and destination pins are imputs.  Returns time in
        microseconds, -1 on error.
        @param cmd a bytes of length 1
        @param src a channel number for the source
        @param dst a channel number for the destination
        '''
        if cmd == MULTIR2R:
            if src not in [0,3,4,5,6,7]:
                print (('Pin should be digital input capable: 0,3,4,5,6 or 7'))
                self.msg = ('Pin should be digital input capable: 0,3,4,5,6 or 7')
                return -1
            if dst > 249:
                self.msg = ('skip exceeded 249 edges')
                print (('skip exceeded 249 edges'))
                return -1
        if cmd in [R2RTIME, R2FTIME, F2RTIME, F2FTIME]:
            if src not in [0,3,4,5,6,7] or dst not in [0,3,4,5,6,7]:
                    self.msg = ('Both pins should be digital input capable: 0,3,4,5,6 or 7')
                    print (('Both pins should be digital input capable: 0,3,4,5,6 or 7'))
                    return -1
        if cmd in [SET2RTIME, SET2FTIME, CLR2RTIME, CLR2FTIME, HTPUL2RTIME, HTPUL2FTIME, LTPUL2RTIME, LTPUL2FTIME]:
            if src not in [8,9,10,11]:
                    self.msg = ('Starting pin should be digital output capable: 8,9,10 or 11')
                    print (('Starting pin should be digital output capable: 8,9,10 or 11'))
                    return -1
            if dst not in [0,3,4,5,6,7]:
                self.msg = ('Destination pin should be digital input capable: 0,3,4,5,6 or 7')
                print (('Destination pin should be digital input capable: 0,3,4,5,6 or 7'))
                return -1
        self.sendByte(cmd)    
        self.sendByte(Byte.pack(src))    
        self.sendByte(Byte.pack(dst))    
        res = self.fd.read(1)
        if res != b'D':
            self.msg = ('Time measurement command error')
            print (('Time measurement command %d error ') %ord(cmd), res)
            return -1.0
        res = self.fd.read(1)
        data = self.fd.read(4)
        raw = struct.unpack('I'* 1, data)  # 32 bit data from T4/T5 counter, 0.125us cycles
        ncycle = raw[0] + 0                # .25 usec correction
        return round(float(ncycle)*0.125)      # returns in microseconds

    """-------------- Passive Time Interval Measurements --------------------"""
    def r2rtime(self, pin1, pin2):
        '''
        Time between two rising edges. The pins must be distinct. For same pin, use multi_r2rtime
        '''
        return self.tim_helper(R2RTIME, pin1, pin2)

    def f2ftime(self, pin1, pin2):
        '''
        Time between two falling edges. The pins must be distinct. For same pin, use multi_r2rtime
        '''
        return self.tim_helper(F2FTIME, pin1, pin2)

    def r2ftime(self, pin1, pin2):
        '''
        Time between a rising edge to a falling edge. The pins could be same or distinct.
        '''
        print('r2r:', pin1, pin2)
        return self.tim_helper(R2FTIME, pin1, pin2)

    def f2rtime(self, pin1, pin2):
        '''
        Time between a falling edge to a rising edge. The pins could be same or distinct.
        '''
        return self.tim_helper(F2RTIME, pin1, pin2)

    def multi_r2rtime(self, pin, skip=0):
        '''
        Time between rising edges, could skip desired number of edges in between. (pin, 9) will give time required for
        10 cycles of a squarewave, increases resolution.
        '''
        return self.tim_helper(MULTIR2R, pin, skip)

    def get_frequency(self, pin):
        '''
        This function measures the frequency of an external 0 to 5V PULSE on digital inputs, by calling multi_r2rtime().
        '''
        t = self.multi_r2rtime(pin)
        if t < 0:
            return t
        if 0 < t < 10000:
            t = self.multi_r2rtime(pin,9)
            return 1.0e7/t
        return 1.0e6 / t

    """---------- Active time interval measurements ------------"""
    def set2rtime(self, pin1, pin2):
        '''
        Time from setting pin1 to a rising edge on pin2.
        '''
        return self.tim_helper(SET2RTIME, pin1, pin2)

    def set2ftime(self, pin1, pin2):
        '''
        Time from setting pin1 to a falling edge on pin2.
        '''
        return self.tim_helper(SET2FTIME, pin1, pin2)

    def clr2rtime(self, pin1, pin2):
        '''
        Time from clearin pin1 to a rising edge on pin2.
        '''
        return self.tim_helper(CLR2RTIME, pin1, pin2)

    def clr2ftime(self, pin1, pin2):
        '''
        Time from clearing pin1 to a falling edge on pin2.
        '''
        return self.tim_helper(CLR2FTIME, pin1, pin2)

    def htpulse2rtime(self, pin1, pin2):
        '''
        Time from a HIGH True pulse on pin1 to a rising edge on pin2.
        '''
        return self.tim_helper(HTPUL2RTIME, pin1, pin2)

    def htpulse2ftime(self, pin1, pin2):
        '''
        Time from HIGH True pulse on pin1 to a falling edge on pin2.
        '''
        return self.tim_helper(HTPUL2FTIME, pin1, pin2)

    def ltpulse2rtime(self, pin1, pin2):
        '''
        Time from a LOW True pulse on pin1 to a rising edge on pin2.
        '''
        return self.tim_helper(LTPUL2RTIME, pin1, pin2)

    def ltpulse2ftime(self, pin1, pin2):
        '''
        Time from LOW True pulse on pin1 to a falling edge on pin2.
        '''
        return self.tim_helper(LTPUL2FTIME, pin1, pin2)

    def srfechotime(self, pin1, pin2):
        '''
        Time from Trigger on Echo for SRF0x module. Trig on pin1 and Echo on pin2.
        '''
        return self.tim_helper(SRFECHOTIME, pin1, pin2)

    """------------------------- Digital I/O-----------------------------"""
    def set_state(self, pin, state):
        '''
        Sets the status of Digital outputs SQR1, SQR2, OD1 or CCS. It
        will work on SQR1 & SQR2 only if the frequency is set to zero.
        @param pin pin number
        @param state a value 0 or 1
        '''
        self.sendByte(SETSTATE)    
        self.sendByte(Byte.pack(pin))    
        self.sendByte(Byte.pack(state))    
        res = self.fd.read(1)
        if res != b'D':
            self.msg = ('SETSTATE error ')
            print (('SETSTATE error '), res)
            return
        return state

    def get_state(self, pin):
        '''
        gets the status of the digital input pin. IN1, IN2 & SEN are
        set to digital mode before sensing input level.
        @param pin a pin number
        @return the state of the pin as a small integer
        '''
        self.sendByte(GETSTATE)    
        self.sendByte(Byte.pack(pin))    
        res = self.fd.read(1)
        if res != b'D':
            self.msg = ('GETSTATE error ')
            print (('GETSTATE error '), res)
            return 
        res = self.fd.read(1)
        return ord(res)

    def get_portb(self):
        '''
        Reads portB, returns 16 bits of data.
        '''
        self.sendByte(GETPORTB)    
        res = self.fd.read(1)
        if res != b'D':
            self.msg = ('GETPORTB error ')
            print (('GETPORTB error '), res)
            return 
        res = self.fd.read(2)
        raw = struct.unpack('H', res)          # 16 bit data in byte array
        print('%x'%raw)
        return raw[0]

    """------- Square Wave Generation & Measuring the Frequency ----------"""
    def set_pwm(self, osc, ds, resol=14):      # osc and duty cycle, resolution 14 bits byn default
        '''
        Sets PWM on SQR1 / SQR2. The frequency is decided by the resolution in bits.
        '''
        if resol < 4 or resol > 16 or ds < 0 or ds > 100:
            return
        ocxrs = 2**resol
        ocx = int(0.01 * ds * ocxrs + 0.5)
        #print(ocxrs, ocx)
        
        if osc == 0:
            self.sendByte(SETPWM1)
        else:
            self.sendByte(SETPWM2)
        self.sendInt(ocxrs-1)                    # ocxrs
        self.sendInt(ocx)                        # ocx
        res = self.fd.read(1)
        if res != b'D':
            self.msg = ('SETPWM error ')
            print(('SETPWM error '), res)
            return 
        return ds

    def set_sqr1_pwm(self, dc, resol=14):        # Duty cycle, resolution 14 bits (f = 488Hz) by default
        '''
        Sets 488 Hz PWM on SQR1. Duty cycle is specified in percentage. The third argument, PWM resolution, is 
        14 bits by default. Decreasing this by one doubles the frequency.
        '''
        return self.set_pwm(0,dc,resol)

    def set_sqr2_pwm(self, dc, resol = 14):    
        '''
        Sets 488 Hz PWM on SQR2. Duty cycle is specified in percentage. The third argument, PWM resolution, is 
        14 bits by default. Decreasing this by one doubles the frequency.
        '''
        return self.set_pwm(1,dc,resol)

    def set_sqr1_dc(self, volt):            
        '''
        PWM DAC on SQR1. Resolution is 10 bits (f = 7.8 kHz) by default. External Filter is required to get the DC
        The voltage can be set from 0 to 5 volts.
        '''
        return 1.0*self.set_pwm(0, volt * 20.0, 10)/20  # 100% means 5 volts., 10 bit resolution, 8kHz 

    def set_sqr2_dc(self, volt):    
        '''
        PWM DAC on SQR2. Resolution is 10 bits (f = 7.8 kHz) by default. External Filter is required to get the DC
        The voltage can be set from 0 to 5 volts.
        '''
        return 1.0*self.set_pwm(1, volt * 20.0, 10)/20   #5V correspods to 100%

    def set_osc(self, chan, freq):        # Freq in Hertz, osc 1 or 2
        '''
        Sets the output frequency of the SQR1 (chan=8) or SQR2 (chan = 9). The function returns actual freqency set.
        '''
        if chan != 8 and chan != 9:
            self.msg = ('Invalid channel number')
            print(('Invalid Channel'))
            return 
        OCRS = 0
        TCKPS = 0
        if freq < 0:    # Disable Timer and Set Output LOW
            TCKPS = 254
        elif freq == 0:
            TCKPS = 255
        else:
            T = 0.125e-6                   # Fosc = 16MHz
            mtvals = [T, T*8, T*64, T*256] # Possible Timer period values
            per = 1.0/freq                 # T requested
            for k in range(4):             # Find the optimum scaling, OCR value
                if per < mtvals[k]*50000:
                    TCKPS = k
                    OCRS = 1.0*per/mtvals[k]
                    OCRS = int(OCRS+0.5)
                    freq = 1./(mtvals[k]*OCRS)
                    #print(freq,'--', k, OCRS, 1./(mtvals[k]*OCRS), TCKPS)
                    break
        if TCKPS < 4 and OCRS == 0:
            print(('Invalid Freqency'))
            return 
        if chan == 8:
            self.sendByte(SETSQR1)
        elif chan == 9:
            self.sendByte(SETSQR2)
        self.sendByte(Byte.pack(TCKPS))    # prescaling for timer
        self.sendInt(OCRS)           # OCRS value
        res = self.fd.read(1)
        if res != b'D':
            print(('SETSQR error '), res)
            return 'Error: '+res
        return freq

    def set_sqr1(self, freq):
        '''
        Sets the frequency of SQR1 (between .7Hz and 200kHz). All intermediate values are not possible.
        Returns the actual value set.
        '''
        res = self.set_osc(8, freq)
        if freq == 0:
            return 0
        else:
            return res
			
    def set_sqr2(self, freq):
        '''
        Sets the frequency of SQR2 (between .7Hz and 200kHz). All intermediate values are not possible.
        Returns the actual value set.
        '''
        res = self.set_osc(9, freq)
        if freq == 0:
            return 0
        else:
            return res

    def set_sqrs(self, freq, diff=0):        # Freq in Hertz, phase difference in % of T
        '''
        Sets the output frequency of both SQR1 & SQR2. The function returns actual value set. The second argument is the
        phase difference between them  in percentage.
        '''
        if freq == 0:         # Disable both Square waves
            self.set_sqr1(0)
            self.set_sqr2(0)
            return 0
        elif freq < 0:        # Disable both Square waves
            self.set_sqr1(-1)
            self.set_sqr2(-1)
            return 0
        if diff < 0 or diff >= 100.0:
            self.msg = ('Invalid phase difference')
            print(('Invalid phase difference'))
            return
        OCRS = 0
        TCKPS = 0
        T = 0.125e-6                      # Fosc = 16MHz
        mtvals = [T, T*8, T*64, T*256]    # Possible Timer period values
        per = 1.0/freq                    # T requested
        for k in range(4):                # Find the optimum scaling, OCR value
            if per < mtvals[k]*50000:
                TCKPS = k
                OCRS = 1.0*per/mtvals[k]
                OCRS = int(OCRS+0.5)
                freq = 1./(mtvals[k]*OCRS)
                #print(freq,'--', k, OCRS, 1./(mtvals[k]*OCRS))
                break
        if TCKPS < 4 and OCRS == 0:
            self.msg = ('Invalid Freqency')
            print(('Invalid Freqency'))
            return 
        TG = int(1.0*diff*OCRS/100 +0.5)
        if TG == 0: TG = 1        # Need to examine this
        #print('TCKPS ', TCKPS, 'ocrs ', OCRS, TG)

        self.sendByte(SETSQRS)
        self.sendByte(Byte.pack(TCKPS))           # prescaling for timer
        self.sendInt(OCRS)                  # OCRS value
        self.sendInt(TG)                    # time difference
        res = self.fd.read(1)
        if res != b'D':
            self.msg = ('SETSQRS error ')
            print(('SETSQRS error '), res)
            return 
        return freq

    """---------------------- ADC & DAC -------------------"""

    def write_dac(self, iv):
        '''
        Writes the 12 bit I2C DAC to the desired value.
        @param iv a value (integer between 0 and 4095)
        '''
        if iv < 0: iv = 0            # Force within limits
        if iv > 4095: iv = 4095

        self.sendByte(SETDAC)
        self.sendInt(iv)
        res = self.fd.read(1)
        if res != b'D':
            self.msg = ('SETDAC error ')
            print(('SETDAC error '), res)
            return

    def read_adc(self, ch):   # Sleep mode conversion
        '''
        Reads the specified ADC channel, Low level routine.
        @param ch channel number
        @return a value between 0 ans 4095
        '''
        if ch < 0 or ch > 31:
            print(('Argument error'))
            return
        self.sendByte(READADCSM)
        self.sendByte(Byte.pack(ch))
        res = self.fd.read(1)
        if res != b'D':
            self.msg = ('READADC error ')
            print(('READADC error '), res)
            return 
        res = self.fd.read(2)
        if sys.version_info.major == 3:
            iv = res[0] | (res[1] << 8)
        else:
            iv = ord(res[0]) | (ord(res[1]) << 8)
        return iv

    def set_voltage(self, v):
        '''
        Sets the PVS output. range is from -5 to + 5 volts. Reads the actual value to apply correction. 
        Returns the voltage readback of the voltage at PVS.
        '''
        if v < 0 or v > 5.0:
            self.msg = ('invalid voltage')
            print(('invalid voltage'))
            return
        goal = int(v * self.DACM + 0.5)
        iv = goal
        for k in range(10):
            self.write_dac(iv)
            isv = self.read_adc(12)            # actual value
            err = goal - isv
            #print('iv & isv err', iv, isv, err    , k)
            if abs(err) <= 1: break
            iv = iv + int(err/2)                # Even if it exceeds 4095, write_dac() will fix it
        sv = self.get_voltage(12)               # The voltage actually set
        return sv

    def set_adcref(self, option):
        '''
        Sets the ADC reference option. Vdd ot external +Vref
        @param option 0 means Vdd, else means external +Vref
        @return option's value
        '''
        self.sendByte(SETADCREF)
        self.sendByte(Byte.pack(option))
        res = self.fd.read(1)
        if res != b'D':
            self.msg = ('SETADCREF error ')
            print(('SETADCREF error '), res)
            return 
        return option

    def read_adcNS(self, ch):   # No Sleep mode conversion
        '''
        Reads the specified ADC channel, Low level routine.
        @param ch channel number
        @return a value from 0 to 4095.
        '''
        if ch < 0 or ch > 31:
            self.msg = ('READADC: Argument error')
            print(('Argument error'))
            return
        self.sendByte(READADC)
        self.sendByte(Byte.pack(ch))
        res = self.fd.read(1)
        if res != b'D':
            self.msg = ('READADC error')
            print(('READADC error'), res)
            return 
        res = self.fd.read(2)
        if sys.version_info.major == 3:
            iv = res[0] | (res[1] << 8)
        else:
            iv = ord(res[0]) | (ord(res[1]) << 8)
        return iv

    def get_voltage(self, ch):  # Sleep mode
        '''
        Reads the specified channel of the ADC. Returns -5V to 5V for channels 0 and 1
        0V to 5V for other channels.
        '''
        if (ch > 31):
            self.msg = ('get_voltage: Argument error')
            print(('Argument error'))
            return
        iv = self.read_adc(ch)
        #print('get_v: iv = ', iv)
        v = self.m12[ch] * iv + self.c[ch]
        return v

    def get_voltageNS(self, ch):   # No Sleep Mode
        '''
        Reads the specified channel of the ADC. Returns -5V to 5V for channels 0 and 1
        0V to 5V for other channels.
        '''
        if (ch > 31):
            self.msg = ('get_voltageNS: Argument error')
            print(('Argument error'))
            return
        iv = self.read_adcNS(ch)
        #print('get_v: iv = ', iv)
        v = self.m12[ch] * iv + self.c[ch]
        return v

    def get_voltage_within(self, ch, vmax):        # Channel and the expected maximum value, < 5V
        '''
        Sets the DAC to vmax and uses it as external +Vref, to increase resolution
        '''
        if ch > 31 or vmax > 5.0:
            self.msg = ('Argument error')
            print(('Argument error'))
            return
        VM = self.set_voltage(vmax)
        self.set_adcref(1)            # External +Vref, from DAC
        res = self.get_voltage(ch)
        self.set_adcref(0)            # Back to Vref+ = Vdd
        return res * VM/5.0

    def get_voltage_time(self, ch):
        '''
        Reads the specified channel of the ADC. Returns -5V to 5V for channels 0 and 1
        0V to 5V for other channels. Adds the PC time info
        '''
        if (ch > 31):
            self.msg = ('get_voltage_time: Argument error')
            print(('Argument error'))
            return
        return (time.time(), self.get_voltage(ch))

    def get_voltageNS_time(self, ch):  # No Sleep mode conversion
        '''
        Reads the specified channel of the ADC. Returns -5V to 5V for channels 0 and 1
        0V to 5V for other channels. Adds the PC time info
        '''
        if (ch > 31):
            self.msg = ('Argument error')
            print(('Argument error'))
            return ('Error ')
        return (time.time(), self.get_voltageNS(ch))


    def capture(self, ch, ns, tg):
        '''
        makes a capture of data from the ADC with 8 bits precision.
        @param ch channel number,
        @param ns number of samples
        @param tg time gap between samples.
        @return a vector of ns timesstamps and another of ns values from the ADC
        '''
        if tg < 4:                  # Minimum time required
            self.msg = ('Minimum Timegap is 4 us')
            tg = 4
        ns=int(ns)
        self.sendByte(CAPTURE)
        self.sendByte(Byte.pack(ch))
        self.sendInt(ns)
        self.sendInt(tg)
        res = self.fd.read(1)
        if res != b'D':
            self.msg = ('CAPTURE error')
            print(('CAPTURE error '), res)
            return
        res = self.fd.read(1)        # adc_size info from other end, ignored
        data = self.fd.read(ns)
        dl = len(data)
        if dl != ns:
            self.msg = ('CAPTURE: size mismatch %d %d') %(ns,dl)
            print(('CAPTURE: size mismatch '), ns, dl)
            return 
        
        #ta = []
        #va = []
        raw = struct.unpack('B'* ns, data)   # 1 byte words in the structure
        
        ta = numpy.zeros(ns)
        va = numpy.zeros(ns)
        for i in range(ns):
            ta[i] = 0.001 * i * tg        # microseconds to milliseconds
            va[i] = raw[i] * self.m8[ch] + self.c[ch]
        return ta,va

    def capture_hr(self, ch, ns, tg):
        '''
        Captures data in high resolution (2 bytes, with 12 significant bits)
        @param ch channel number
        @param ns number of samples
        @param tg time gap between two samples
        @return a vector of ns timesstamps and another of ns values from the ADC
        '''
        if tg < 4:
            self.msg = ('Minimum Timegap is 4 us')
            tg = 4
        ns=int(ns)
        self.sendByte(CAPTURE_HR)
        self.sendByte(Byte.pack(ch))
        self.sendInt(ns)
        self.sendInt(tg)
        res = self.fd.read(1)
        if res != b'D':
            self.msg =  ('CAPTURE error ')
            print(('CAPTURE error '), res)
            return
        res = self.fd.read(1)        # adc_size info from other end, ignored
        data = self.fd.read(ns*2)
        dl = len(data)
        if dl != ns*2:
            self.msg = ('CAPTURE: size mismatch %d %d') %(ns, dl)
            print(('CAPTURE: size mismatch '), ns, dl)
            return
        
        raw = struct.unpack('H'* ns, data)   # 1 byte words in the structure
        ta = numpy.zeros(ns)
        va = numpy.zeros(ns)
        for i in range(ns):
            ta[i] = 0.001 * i * tg        # microseconds to milliseconds
            va[i] = raw[i] * self.m12[ch] + self.c[ch]
        return ta,va


    def capture2(self, cha, chb, ns, tg):
        '''
        Captures from 2 channels, data precision is 8 bits
        @param cha first channel
        @param chb second channel
        @param ns number of samples
        @param tg time gap between samples
        @return 4 vectors of data: time, voltage, time, voltage
        '''
        if tg < 8:
            self.msg = ('Minimum Timegap is (4*number of channels)usec')
            tg = 8
        ns=int(ns)
        self.sendByte(CAPTURE2)
        self.sendByte(Byte.pack(cha))
        self.sendByte(Byte.pack(chb))
        self.sendInt(ns)
        self.sendInt(tg)
        res = self.fd.read(1)
        if res != b'D':
            self.msg =('CAPTURE2 error ')
            print(('CAPTURE2 error '), res)
            return
        res = self.fd.read(1)        # adc_size info from other end, ignored
        data = self.fd.read(ns*2)
        dl = len(data)
        if dl != ns*2:
            self.msg = ('CAPTURE2: size mismatch')
            print(('CAPTURE2: size mismatch'), ns*2, dl)
            return

        raw = struct.unpack('B'* 2*ns, data)  # 8 bit data in byte array
        taa = numpy.zeros(ns)
        vaa = numpy.zeros(ns)
        tba = numpy.zeros(ns)
        vba = numpy.zeros(ns)
        for i in range(ns):
            taa[i] = (0.001 * i * tg)
            vaa[i] = (raw[2*i] * self.m8[cha] + self.c[cha])
            tba[i] = (0.001 * i * tg + self.tgap)
            vba[i] = (raw[2*i +1] * self.m8[chb] + self.c[chb])
        return taa,vaa,tba,vba

    def capture2_hr(self, cha, chb, ns, tg):
        '''
        Captures from 2 channels, data precision is 12 bits
        @param cha first channel
        @param chb second channel
        @param ns number of samples
        @param tg time gap between samples
        @return 4 vectors of data: time, voltage, time, voltage
        '''
        if tg < 8:
            self.msg = ('Minimum Timegap is (4*number of channels)usec')
            tg = 8
        ns=int(ns)
        self.sendByte(CAPTURE2_HR)
        self.sendByte(Byte.pack(cha))
        self.sendByte(Byte.pack(chb))
        self.sendInt(ns)
        self.sendInt(tg)
        res = self.fd.read(1)
        if res != b'D':
            self.msg = ('CAPTURE2_HR error ')
            print(('CAPTURE2_HR error '), res)
            return
        res = self.fd.read(1)        # adc_size info from other end, ignored
        data = self.fd.read(ns*2*2)
        dl = len(data)
        if dl != ns*2*2:
            self.msg = ('CAPTURE2_HR: size mismatch')
            print(('CAPTURE2_HR: size mismatch'), ns*2*2, dl)
            return

        taa = numpy.zeros(ns)
        vaa = numpy.zeros(ns)
        tba = numpy.zeros(ns)
        vba = numpy.zeros(ns)
        raw = struct.unpack('H'* 2*ns, data)  # 16 bit data in byte array
        for i in range(ns):
            taa[i] = (0.001 * i * tg)
            vaa[i] = (raw[2*i] * self.m12[cha] + self.c[cha])
            tba[i] = (0.001 * i * tg + self.tgap)
            vba[i] = (raw[2*i +1] * self.m12[chb] + self.c[chb])
        return taa,vaa,tba,vba

    def capture3(self, ch1, ch2, ch3, ns, tg):
        '''
        Captures from 2 channels, data precision is 12 bits
        @param ch1 first channel
        @param ch2 second channel
        @param ch3 third channel
        @param ns number of samples
        @param tg time gap between samples
        @return 6 vectors of data: 3 x (time, voltage)
        '''
        if tg < 12:
            self.msg = ('Minimum Timegap is (4*number of channels)usec')
            tg = 12
        ch12 = (ch2 << 4) | ch1      # first two channels packed in 1 byte
        ns=int(ns)
        self.sendByte(CAPTURE3)
        self.sendByte(Byte.pack(ch12))
        self.sendByte(Byte.pack(ch3))
        self.sendInt(ns)
        self.sendInt(tg)
        res = self.fd.read(1)
        if res != b'D':
            self.msg = ('CAPTURE3 error ')
            print(('CAPTURE3 error '), res)
            return
        res = self.fd.read(1)        # adc_size info from other end, ignored
        data = self.fd.read(ns*3)
        dl = len(data)
        if dl != ns*3:
            self.msg = ('CAPTURE3: size mismatch ')
            print(('CAPTURE3: size mismatch '), ns*3, dl)
            return
        taa = numpy.zeros(ns)
        vaa = numpy.zeros(ns)
        tba = numpy.zeros(ns)
        vba = numpy.zeros(ns)
        tca = numpy.zeros(ns)
        vca = numpy.zeros(ns)
        raw = struct.unpack('B'* 3*ns, data)  # 8 bit data in byte array
        for i in range(ns):
            taa[i] = (0.001 * i * tg)
            vaa[i] = (raw[3*i] * self.m8[ch1] + self.c[ch1])
            tba[i] = (0.001 * i * tg + self.tgap)
            vba[i] = (raw[3*i +1] * self.m8[ch2] + self.c[ch2])
            tca[i] = (0.001 * i * tg + 2*self.tgap)
            vca[i] = (raw[3*i +2] * self.m8[ch3] + self.c[ch3])
        return taa,vaa, tba,vba, tca,vca


    def capture4(self, ch1, ch2, ch3, ch4, ns, tg):
        '''
        Captures from 2 channels, data precision is 12 bits
        @param ch1 first channel
        @param ch2 second channel
        @param ch3 third channel
        @param ch4 fourth channel
        @param ns number of samples
        @param tg time gap between samples
        @return 8 vectors of data: 4 x (time, voltage)
        '''
        if tg < 16:
            self.msg = ('Minimum Timegap is (4*number of channels)usec')
            tg = 16
        ch12 = (ch2 << 4) | ch1        # first two channels packed in 1 byte
        ch34 = (ch4 << 4) | ch3        # other two channels packed in 1 byte
        ns=int(ns)
        self.sendByte(CAPTURE4)
        self.sendByte(Byte.pack(ch12))
        self.sendByte(Byte.pack(ch34))
        self.sendInt(ns)
        self.sendInt(tg)
        res = self.fd.read(1)
        if res != b'D':
            self.msg = ('CAPTURE4 error =')
            print(('CAPTURE4 error ='), ord(res))
            return
        res = self.fd.read(1)        # adc_size info from other end, ignored
        data = self.fd.read(ns*4)
        dl = len(data)
        if dl != ns*4:
            self.msg = ('CAPTURE4: size mismatch ')
            print(('CAPTURE4: size mismatch '), ns*4, dl)
            return
        taa = numpy.zeros(ns)
        vaa = numpy.zeros(ns)
        tba = numpy.zeros(ns)
        vba = numpy.zeros(ns)
        tca = numpy.zeros(ns)
        vca = numpy.zeros(ns)
        tda = numpy.zeros(ns)
        vda = numpy.zeros(ns)
        raw = struct.unpack('B'* 4*ns, data)  # 8 bit data in byte array
        #print(raw)
        for i in range(ns):
            taa[i] = (0.001 * i * tg)
            vaa[i] = (raw[4*i] * self.m8[ch1] + self.c[ch1])
            tba[i] = (0.001 * i * tg + self.tgap)
            vba[i] = (raw[4*i +1] * self.m8[ch2] + self.c[ch2])
            tca[i] = (0.001 * i * tg + 2*self.tgap)
            vca[i] = (raw[4*i +2] * self.m8[ch3] + self.c[ch3])
            tda[i] = (0.001 * i * tg + 3*self.tgap)
            vda[i] = (raw[4*i +3] * self.m8[ch4] + self.c[ch4])
        return taa,vaa, tba,vba, tca,vca, tda, vda

    def capture01(self, np, tg):
        '''
        captures channels A0 and A1 simultaneously, with 8 bit resolution
        '''
        return self.capture2(1,2,np,tg)

    def capture01_hr(self, np, tg):
        '''
        captures channels A0 and A1 simultaneously, with 12 bit resolution
        '''
        return self.capture2_hr(1,2,np,tg)

    def set_trigger(self, tval):
        self.sendByte(SETTRIGVAL)
        self.sendInt(tval)
        res = self.fd.read(1)
        if res != b'D':
            self.msg = ('SETTRIGVAL error ')
            print(('SETTRIGVAL error '), res)
            return
        return tval

    """----------------- Modifiers for Capture ----------------------------"""
    def disable_actions(self):
        '''
        Disable all modifiers to the capture call. The capture calls will be set to 
        do analog triggering on the first channel captured.
        '''
        self.sendByte(SETACTION)
        self.sendByte(AANATRIG)
        self.sendByte(Byte.pack(0))        # Self trigger on channel zero means the first channel captured
        res = self.fd.read(1)
        if res != b'D':
            self.msg = ('ERROR: SETACTION')
            print(('ERROR: SETACTION'), res)
            return
        return 0

    def enable_action(self, action, ch):
        """
        Enables some action
        @param action a bytes of length 1
        @param ch a channel number
        @return action's value
        """
        actions=(AANATRIG, AWAITHI, AWAITLO, AWAITRISE, AWAITFALL, ASET,
                 ACLR, APULSEHT, APULSELT)
        if  action not in actions or ch < 1  or ch > 11:    
            self.msg = 'Invalid actions or source specified'
            return
        self.sendByte(SETACTION)
        self.sendByte(action)
        self.sendByte(Byte.pack(ch))
        res = self.fd.read(1)
        if res != b'D':
            self.msg = ('SETACTION ERR')
            return
        return action
        
    def set_trig_source(self, ch):
        '''
        Analog Trigger of the desired channel
        '''
        return self.enable_action(AANATRIG, ch)
        
    def enable_wait_high(self, ch):
        '''
        Wait for a HIGH on the specified 'pin' just before every Capture.
        '''      
        return self.enable_action(AWAITHI, ch)

    def enable_wait_low(self, ch):
        '''
        Wait for a LOW on the specified 'pin' just before every Capture.
        '''
        return self.enable_action(AWAITLO, ch)

    def enable_wait_rising(self, ch):
        '''
        Wait for a rising EDGE on the specified 'pin' just before every Capture.
        '''
        return self.enable_action(AWAITRISE, ch)

    def enable_wait_falling(self, ch):
        '''
        Wait for a falling EDGE on the specified 'pin' just before every Capture.
        '''
        return self.enable_action(AWAITFALL, ch)
    
    def enable_set_high(self, ch):
        '''
        Sets the specified 'pin' HIGH, just before every Capture.
        '''
        return self.enable_action(ASET, ch)

    def enable_set_low(self, ch):
        '''
        Sets the specified 'pin' LOW, just before every Capture.
        '''
        return self.enable_action(ACLR, ch)

    def enable_pulse_high(self, ch):
        '''
        Generate a HIGH TRUE Pulse on the specified 'pin', just before every Capture.
        width is specified by the set_pulsewidth() function.
        '''
        return self.enable_action(APULSEHT, ch)

    def enable_pulse_low(self, ch):
        '''
        Generate a LOW TRUE Pulse on the specified 'pin', just before every Capture.
        '''
        return self.enable_action(APULSELT, ch)

    def set_pulsewidth(self, width):
        '''
        Sets the 'pulse_width' parameter for pulse2rtime() command. 
        Also used by usound_time() and the elable_pulse_high/low() functions
        @param width an integer value (microseconds
        @return the value of width
        '''
        if width < 1 or width > 500:
            self.msg = ('Invalid pulse width')
            return
        self.sendByte(SETPULWIDTH)
        self.sendInt(width)
        res = self.fd.read(1)
        if res != b'D':
            self.msg = ('ERROR: SETPULWIDTH')
            print(('ERROR: SETPULWIDTH'), res)
            return
        return width

    """-----------DIRECT PORT ACCESS FUNCTIONS-----------"""
    """-----------(Use only if you know what you are doing)---------"""
    def set_ddr(self, port, direc):
        self.dwrite(SETDDR)           
        self.dwrite(Byte.pack(port))     # 0 to 3 for A,B,C and D
        self.dwrite(Byte.pack(direc))
        self.fd.read(1)
        return

    def set_port(self, port, val):
        self.dwrite(SETPORT)           
        self.dwrite(Byte.pack(port))     # 0 to 3 for A,B,C and D
        self.dwrite(Byte.pack(val))
        self.fd.read(1)
        return

    def get_port(self, port):
        self.dwrite(SETPORT)           
        self.dwrite(Byte.pack(port))     # 0 to 3 for A,B,C and D
        self.fd.read(1)
        data = self.fd.read(1)     # get the status byte only
        return ord(data)

    """---------------------- may go to eyeutils.py --------------------"""
    def minimum(self,va):
        vmin = 1.0e10        # need to change
        for v in va:
            if v < vmin:
                vmin = v
        return vmin

    def maximum(self,va):
        vmax = 1.0e-10        # need to change
        for v in va:
            if v > vmax:
                vmax = v
        return vmax

    def rms(self,va):
        vsum = 0.0
        for v in va:
            vsum += v**2
        v = 1.0*vsum / len(va)
        return math.sqrt(v)

    def mean(self,va):
        vsum = 0.0
        for v in va:
            vsum += v
        v = 1.0*vsum / len(va)
        return v

    def save(self, data, filename = 'plot.dat'):
        '''
        Input data is of the form, [ [x1,y1], [x2,y2],....] where x and y are vectors
        '''
        if data == None: return
        if type(filename) == tuple:
            filename = filename[0]
   
        if filename:
            f = fileOpen(filename,'w')
            for xy in data:
               for k in range(len(xy[0])):
                   f.write('%5.3f  %5.3f\n'%(xy[0][k], xy[1][k]))
               f.write('\n')
        f.close()
        

    def grace(self, data, xlab = '', ylab = '', title = ''):
        '''
        Input data is of the form, [ [x1,y1], [x2,y2],....] where x and y are vectors
        '''
        from expeyes.eyeplot import ExtPlotter
        ep=ExtPlotter()
        status=ep.plot(data, xLabel=xlab, yLabel=ylab, title=title)
        return status


# Local Variables:
# python-indent: 4
# End:

