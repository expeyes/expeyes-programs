/*
Stepper motor coils are connected to the collectors of 4 transistors
whose bases are connected to PA0 to PA3.
*/

#include <avr/io.h>


void delay (uint16_t k)  // Delay is (k * 2) usec
    {
    volatile uint16_t x = k;
    while (x)  --x;
    }


void rotateMotor (int nsteps, int dir)
{
  static uint8_t pos = 0, seq[4] = { 12, 6, 3, 9 };
  int i;

  for (i = 0; i < nsteps; ++i)
    {
      if (dir)
	if (pos == 3)
	  pos = 0;
	else
	  ++pos;
      else if (pos == 0)
	pos = 3;
      else
	--pos;

      PORTA = seq[pos];
      delay (3000);
    }
}

int main (void)
  {
  DDRA = 15;		// Data Direction Register for PORT A

  for(;;) { rotateMotor(100,0); rotateMotor(100,1);}
  
  return 0;
}
