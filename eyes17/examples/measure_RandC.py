'''
Measures capacitance in the range of pico Farads
'''

from __future__ import print_function
import eyes17.eyes
p = eyes17.eyes.open()

#connect Capacitor from IN1 to GND
print (p.get_capacitance())

#connect an LDR  from SEN to GND
print (p.get_resistance())

