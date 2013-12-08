#include "mh-utils.c"


int main (void)
  {
  DDRB = 1;		// Data Direction Register for port B

  for(;;)
    {
    PORTB = 1;	
    delay_ms(500);
    PORTB = 0;
    delay_ms(500);
  }
}
