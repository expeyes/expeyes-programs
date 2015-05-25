#include "mh-utils.c"


int main (void)
  {
  DDRB = 255;		// Data Direction Register for port B
uint16_t k;

while(1)
	{
              k = 0;
              while(k < 256) PORTB = k++;
		--k;
              while(k >0) PORTB = k--;
        	//for(k = 0;  k <= 255; ++k) PORTB = k;
        //        PORTB = 0;
        	//for(k = 255;  k >=0; --k)   PORTB = k; 
        }
}
