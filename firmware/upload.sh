echo "Uploading  $1.c and Locking it"

uisp -dprog=dapa -dpart=atmega32 -dlpt=0x378 --erase

uisp --verify -dprog=dapa -dpart=atmega32 -dlpt=0x378 --upload if=$1.hex

uisp -dprog=dapa -dpart=atmega32 -dlpt=0x378 --wr_lock=0xfe
