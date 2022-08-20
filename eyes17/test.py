from layouts.advancedLoggerTools import inputs
import eyes17.eyes
dev = eyes17.eyes.open()
inp = inputs(dev)
inp.init_ADS8691()
dev.SPI.set_parameters(1,1,0,0,1)
while 1:
	inp.ADS8691_range(3)
	inp.read_ADS8691()
