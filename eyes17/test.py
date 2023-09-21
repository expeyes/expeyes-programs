from layouts.advancedLoggerTools import inputs
import eyes17.eyes
import time
dev = eyes17.eyes.open()

print('clear')
dev.set_state(OD1=0)
time.sleep(1)
print('measure')
print(dev.set2ftime('OD1','SEN'))
