#include "mh-lcd.c"
#include <avr/eeprom.h>

int main()
{
uint8_t x, i, *p;

p = 10;   // selected EEPROM location 

lcd_init();
for(i = 0; i < 5; ++i) eeprom_write_byte (p+i, i*2);   // write to eeprom
for(i = 0; i < 5; ++i)
	{
	x = eeprom_read_byte (p+i);    // read from eeprom
	lcd_put_int(x);
	lcd_put_char(' ');
	}
}
