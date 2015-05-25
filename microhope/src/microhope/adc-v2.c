#include <avr/io.h>
#include "mh-lcd.c"

// convert channel 0, set pre-scaler to 7
main()
{
uint16_t data;
lcd_init();

ADCSRA = (1 << ADEN) |  7;   // Enable ADC, set clock pre-scaler
ADMUX =  (1 << REFS0);			     // AVCC reference, channel 0 	

ADCSRA |=  (1 <<ADSC);             // Start ADC
while ( !(ADCSRA & (1<<ADIF)) ) ;	 // wait for ADC conversion

data = (ADCH << 8) | ADCL;    // 10 bit data from ADCL and ADCH
lcd_put_int(data);
}
