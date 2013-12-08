avrdude -c usbasp -patmega32 -U flash:w:ATmegaBOOT_168_atmega32.hex          # upload hex file
avrdude -c usbasp -patmega32 -U lfuse:w:0xff:m -U hfuse:w:0xda:m             # set fuse to 0xDA
avrdude -b 19200 -P /dev/ttyUSB0 -pm32 -c stk500v1 -n                        # verify the device on /dev/ttyUSB0


