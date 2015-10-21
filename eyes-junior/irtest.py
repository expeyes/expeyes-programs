from __future__ import print_function
import expeyes.eyesj,time

p=expeyes.eyesj.open()

p.set_state(10,1)
x=0
while 1:
	#n = input('Enter number(0 to 255) :')
	p.irsend1(x)
	time.sleep(.5)
	print (x)
	x+=1
