#include <avr/io.h>

void delay (uint16_t k)
    /* generates delay by decrementing a number until it reaches zero.
    roughly 2 usec per loop at 8 MHz system clock
    */
    {
    volatile uint16_t x = k;
    while (x)  --x;
    }

int main (void)
  {
  DDRB = 1;		// Data Direction Register for port B

  for(;;)
    {
    PORTB = 1;	
    delay(30000);
    PORTB = 0;
    delay(30000);
  }
}
