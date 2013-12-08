#include <avr/io.h>

int main (void)
  {
  uint8_t  val;
  DDRA = 0;		// Data Direction Register
  DDRB = 1;
  
  for(;;)
    {
    val = PINA;
    PORTB = val;	
    }
}
