#! /bin/sh
cd /usr/share/microhope/firmware
avrdude -c dapa -patmega32 -U flash:w:Bootloader_atmega32.hex
avrdude -c dapa -patmega32 -U lfuse:w:0xff:m -U hfuse:w:0xda:m
avrdude -b 19200 -P /dev/ttyUSB0 -pm32 -c stk500v1 -n


