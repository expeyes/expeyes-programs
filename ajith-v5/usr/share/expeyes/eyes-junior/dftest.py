import expeyes.eyesj, time
p=expeyes.eyesj.open()

p.set_state(10,1)

for m in range(1000):
	sum = 0.0
	for k in range(1):
		t = p.srfechotime(9,0)
		#print t
		sum += t
		time.sleep(.1)
	print sum/1 * 0.0175 -6.083
	time.sleep(0)
	#raw_input()
