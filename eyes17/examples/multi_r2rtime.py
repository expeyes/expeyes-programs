'''
multi_r2rtime(input, ncycles) returns the microseconds elapsed between two rising edges.
ncycles is the number of cycles to be measured.
'''

from __future__ import print_function
import eyes17.eyes
p = eyes17.eyes.open()

p.set_sqr1(1000)               # set 1kHz on  SQR1
t = p.multi_r2rtime('IN2')    # 6 is the readback of SQR1. Time of 10 cycles

print (t, 'Frequency = ', (1.0/t))
