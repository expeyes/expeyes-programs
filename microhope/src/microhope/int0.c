#include <avr/io.h>
#include <avr/interrupt.h>

volatile uint8_t i=0;

ISR(INT0_vect)
{
PORTB = ++i;
}
int main (void)
  {
  DDRB = 255;
  PORTD = 15;
  GICR |= (1 << INT0);
  sei();
  for(;;);
}
