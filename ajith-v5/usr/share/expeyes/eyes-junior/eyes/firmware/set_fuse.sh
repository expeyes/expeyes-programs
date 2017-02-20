echo "Setting fuses for ATmega32: 8Mhz External Crystal, disable JTAG"
uisp -dprog=dapa -dpart=atmega32 -dlpt=0x378 --erase
uisp -dprog=dapa -dpart=atmega32 -dlpt=0x378 --wr_fuse_l=0xef
uisp -dprog=dapa -dpart=atmega32 -dlpt=0x378 --wr_fuse_h=0xd1
uisp -dprog=dapa -dpart=atmega32 -dlpt=0x378 --rd_fuses 
