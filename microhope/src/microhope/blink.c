#include "mh-utils.c"


int main (void)
  {
  DDRB = 255;		// Data Direction Register for port B

  for(;;)
    {
    PORTB = 255;	
    delay_ms(50);
    PORTB = 0;
    delay_ms(50);
  }
return 0;
}
