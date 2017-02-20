import expeyes.eyes, time
p=expeyes.eyes.open()

good = False
for k in range(5):
	res = p.read_inputs()
	if res != None:
		print 'EYES communication Okey'
		good = True
		break
if good == False:
		print 'EYES Communication failed. Something Wrong !!!'
