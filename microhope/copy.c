#include <avr/io.h>

int main (void)
  {
  DDRA = 0;		// Data Direction Register
  PORTA = 1;		// Enable pullup on PORTA, bit 0
  DDRB = 1;
  
  for(;;)
    PORTB = PINA;
}
