#!/bin/sh    Batch file to program ATMega32 using the USBASP programmer  
avrdude -B10 -c usbasp -patmega32 -U flash:w:ATmegaBOOT_168_atmega32.hex  # upload hex file
avrdude -B10 -c usbasp -patmega32 -U lfuse:w:0xff:m -U hfuse:w:0xda:m     # set fuse to 0xDA


