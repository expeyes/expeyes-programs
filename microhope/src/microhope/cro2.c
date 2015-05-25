/* 
Program : cro.c
author  : Ajith Kumar (ajith@iuac.res.in)
License : GNU GPL version 3 or above
Receives a 1 byte command, number of samples (NS, 2 bytes) Time gap (2 bytes) from the PC.
Reads ADC channel 0 NS times, returns a 'D' followed by NS bytes of data
No error checking implemented.
*/

#include <avr/io.h>

#define	READBLOCK	 1	//  code for readblock is 1
#define BUFSIZE		1800	// ATmega32 with 2K RAM

uint8_t		tmp8, dbuffer[BUFSIZE+1];	   // 1 status byte
uint16_t	tmp16, buf_index, nsamples, timegap;	


void processcommand()
{       
   TCCR1B = (1 << CS11);	// Timer Counter1 in Normal mode, 8 MHz/8, 1 usec per count
   nsamples = dbuffer[1] | (dbuffer[2] << 8);
   timegap  = dbuffer[3] | (dbuffer[4] << 8);
   ADMUX = (1 << REFS0) |(1 << ADLAR) | 0; 		// 8 bit mode, AVCC as reference, channel 0
   ADCSRA |= ADIF;						    	// reset ADC DONE flag
   buf_index = 0;
   for(tmp16 = 0; tmp16 < nsamples; ++tmp16)         			// Digitize nsamples times
        {
	    TCNT1 = 1;
        ADCSRA |= (1 << ADSC) | 1;          // Start AD conversion, ADC clock divider is 1
        while ( !(ADCSRA & (1<<ADIF)) ) ;	// wait for conversion to complete
        dbuffer[tmp16] = ADCH;				// Collect Data and store it
        ADCSRA |= ADIF;						// reset ADC DONE flag
	    while(TCNT1L < timegap) ;			// Wait on counter for the specified time gap
        }
// Why we are NOT sending data inside the above loop. Think about it. 
        
    while( !(UCSRA & (1 <<UDRE) ) );         // Wait for transmit buffer empty flag
    UDR = 'D';								 // Send the response byte in all cases
    for(tmp16=0; tmp16 < nsamples; ++tmp16)	 // Send the collected data to the PC
    	{
    	while( !(UCSRA & (1 <<UDRE) ) );
    	UDR = dbuffer[tmp16];
		}
}

int main (void)
{
  // Initialize the RS232 communication link to the PC 38400, 8, 1, N
  UCSRB = (1 << RXEN) | (1 << TXEN);
  UBRRH = 0;
  UBRRL = 12;	// At 8MHz clock (12 =>38400 baudrate)
  UCSRC = (1 <<URSEL) | (1 << UCSZ1) | (1 << UCSZ0); // 8,1,N

  ADCSRA = (1 << ADEN);		// Enable the ADC

  buf_index = 0;
  for(;;)				// Infinite loop waiting for commands from PC
    {
    while ( !(UCSRA & (1<<RXC)) ) ;		// wait for data from PC
    dbuffer[buf_index++] = UDR;			// Store the received byte 
    if(buf_index > 4)					// Start Processing after receiving required arguments
      {
      if(dbuffer[0] == READBLOCK) processcommand();
      buf_index = 0;
      }
    }
}
