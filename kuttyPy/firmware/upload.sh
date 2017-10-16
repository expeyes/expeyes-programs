echo "Uploading  $1.hex to ATmega32 on microHOPE via /dev/ttyUSB0"
avrdude -b 19200 -P /dev/ttyACM0 -pm32 -c stk500v1 -U flash:w:$1.hex

