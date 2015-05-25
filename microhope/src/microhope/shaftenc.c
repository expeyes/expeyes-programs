#include <avr/io.h>
#include <avr/interrupt.h>
#include "mh-lcd.c"


volatile uint16_t counter = 0;
volatile uint8_t  level = 0;

ISR(INT0_vect)	// INT0
{
level = PIND & 8;

if ( level)
	++counter;
else 
	{
	--counter;
	}

PORTB = counter >> 8;
PORTA = counter & 255;
lcd_clear();
lcd_put_int(counter);
}


main()
{
DDRB = 255;
DDRA = 255;
PORTB = 1;
PORTD = 6;  // enable pullup on PD2 and PD3
lcd_init();

MCUCR  = (1 << ISC01) | (1 << ISC00);
GICR |= (1 << INT0);

sei();
while(1)
	{
	}
}
