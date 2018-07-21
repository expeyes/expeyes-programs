'''
r2ftime(in1, in2) returns the microseconds elapsed from a rising edge on input1 to a falling edge of input2,
they could be the same
'''

from __future__ import print_function
import eyes17.eyes
p = eyes17.eyes.open()

p.set_sqr1(1000,30)        # set 1kHz squarewave, 30% duty cycle

print (p.r2ftime('IN2', 'IN2'))

p.set_sqr1(1000,60)        # set 1kHz squarewave, 60% duty cycle

print (p.r2ftime('IN2', 'IN2'))
