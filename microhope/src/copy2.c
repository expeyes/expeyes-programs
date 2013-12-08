#include "mh-digital.c"

int main (void)
  {
  uint8_t  val;
  DDRA = 0;		// PORTA as Input
  PORTA = 1;		// Enable pullup PA0
  DDRB = 1;		// configure PB0 as output

  for(;;)
     {
     val = GETBIT(PINA, 0);
     if (val != 0)
	    PORTB = 1; //SETBIT(PORTB, 0);
     else
	    PORTB = 0; //CLRBIT(PORTB, 0);
     }
}
