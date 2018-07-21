'''
Connect OD1 to A1
'''

from __future__ import print_function
import eyes17.eyes
p = eyes17.eyes.open()

#connect OD1 to A1
p.set_state(OD1 = 1 )        # set OD1 to HIGH
print (p.get_voltage('A1'))

p.set_state(OD1 = 0 )        # set OD1 to HIGH
print (p.get_voltage('A1'))
