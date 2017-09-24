from __future__ import print_function

import sys,inspect

from expeyes import eyes17
p = eyes17.open()


functionList = {}
for a in dir(p):
	attr = getattr(p, a)
	if inspect.ismethod(attr) and a!='__init__':
		functionList[a] = attr


code = '''
from pylab import *

set_state(OD1=0)			# This line gives error -> set_state() takes no keyword arguments

t,v = capture_action('A1', 300, 10, 'SET_HIGH')
plot(t,v)
show()
'''

def printer(*args):
	print  ('here', args)

functionList['print']= printer
submitted = compile(code.encode(), '<string>', mode='exec')
try:
	exec(submitted, functionList)
except Exception as e:
	print(str(e))


