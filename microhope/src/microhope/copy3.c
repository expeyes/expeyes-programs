#include <avr/io.h>   // Include file for I/O operations

int main (void)
{
DDRA = 0;             // Port A as Input
PORTA = 1;          // Enable pullup on PA0
DDRB = 1;             // Configure PB0 as output  

for(;;)
   if(PINA & 1)        // If PA0 is set
       PORTB |= 1;     // Set PB0, by ORing with 00000001b
   else                // otherwise clear PB0
       PORTB &= ~1;    // by ANDing with 11111110b (~00000001b)
}
