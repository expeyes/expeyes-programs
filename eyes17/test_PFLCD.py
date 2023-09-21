import eyes17.eyes
import time
from eyes17.SENSORS import PCF_LCD
dev = eyes17.eyes.open()
while 1:
	print(dev.I2C.scan())
	p = PCF_LCD.lcd(dev.I2C, 63)
	p.lcd_display_string("HUH",1)
	time.sleep(0.1)
