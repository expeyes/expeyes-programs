/* 
Program : pymicro.c
author  : Ajith Kumar (ajith@iuac.res.in)
License : GNU GPL version 3 or above
A program to read/write the microcontroller registers from Python running on PC
*/

#include <avr/io.h>
//#include "mh-lcd.c"

#define READB  1
#define WRITEB 2


int main (void)
{
uint8_t cmd, data;
uint16_t *port;

  // Initialize the RS232 communication link to the PC 38400, 8, 1, N
  UCSRB = (1 << RXEN) | (1 << TXEN);
  UBRRH = 0;
  UBRRL = 12;	// At 8MHz clock (12 =>38400 baudrate)
  UCSRC = (1 <<URSEL) | (1 << UCSZ1) | (1 << UCSZ0); // 8,1,N

//lcd_init();

  for(;;)				// Infinite loop waiting for commands from PC
    {
    while ( !(UCSRA & (1<<RXC)) ) ;		// wait for command from PC
    cmd = UDR;							// Store the received byte 
    if(cmd == READB)
    	{
    	while ( !(UCSRA & (1<<RXC)) ) ;		// wait for serial data
		port =  UDR;						// get the port address to read		
		UDR = *port;
		}
	else if(cmd == WRITEB)
		{
		while ( !(UCSRA & (1<<RXC)) ) ;		// wait for serial data
		port = UDR;							// get the port address to read		
		while ( !(UCSRA & (1<<RXC)) ) ;		// wait for serial data
		data = UDR;
		*port = data;						// write it to the port address
//		lcd_clear(); lcd_put_int(port); lcd_put_char(':'); lcd_put_byte(data);
		}
	// Invalid commands are ignored silently
    }
}

