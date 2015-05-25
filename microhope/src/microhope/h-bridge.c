#include <avr/io.h>

int main (void)
  {
  DDRA = 15;		// Data Direction Register for port A
  PORTD = 4 +8 ;             // pullup on PD2 and PD3

  for(;;)
       {
       if ( (PIND & 12) == 4)               //  PD3 is grounded
	       PORTA = 1;                            // makes output A high and B low
       else  if ( (PIND & 12) == 8)    //   PD2 is grounded
              PORTA = 2;                           // makes output B high and A low
	else
	      PORTA = 0;
  }
}
