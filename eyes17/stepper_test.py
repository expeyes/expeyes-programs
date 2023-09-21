import eyes17.eyes
dev = eyes17.eyes.open()
for a in range(20):
	dev.stepper_move(200,1,0.02) #Reverse  
	dev.stepper_move(200,0, 0.02) #Forward  
