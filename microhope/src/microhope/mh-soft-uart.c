/*
mh-soft-uart.c  :  Soft Serial Communication functions for Atmega32 on MicroHOPE
Tx on PD3
Rx on PD2 (uses INT0)

Author  :  Ajith Kumar, Inter-University Accelerator Centre,   New Delhi 
Licence :  GNU General Public License  version 3 or above
Date :  5-Feb-2014
*/

#include <avr/io.h>
#include <avr/interrupt.h>

#define RXBIT  PD2
#define TXBIT  PD3

	//delay between bits for a given baudrate, valid only for 8MHz clock
void bit_delay (uint16_t  baudrate)   
{
  volatile uint16_t   x;
switch(baudrate) {
      case 38400:            // this is only to mark the first middle point
                 x=9; 
                 while (x--);
                 break;
      case 19200:
                 x=22; 
                 while (x--);
                 break;
      case 9600:                    // 104 usecs per bit
                 x=50; 
                 while (x--);
                 break;
      case 4800:
                 x=105; 
                 while (x--);
                 break;
      case 2400:
                 x=215; 
                 while (x--);
                 break;
      default:
                 break;
         }
}

#define    UBSIZE     128
uint16_t   baudrate  = 9600;
uint8_t     uart_buf[UBSIZE];                               // Rx buffer
volatile    uint8_t   ubrd, ubwrt, ubcount;   // read/write indices and count

SIGNAL (SIG_INTERRUPT0)		// interrupt triggered on a falling edge on PD2
{
uint8_t bit, val = 0;

if(ubcount == UBSIZE) return;	// Rx buffer is full

bit_delay(baudrate*2);       // wait till the middle of the start bit
if ( PIND & 4) return;      // False  trigger

for(bit =0;  bit <= 7;  ++bit)
	{
    bit_delay(baudrate);
    if (PIND & (1 << RXBIT))    val  |=  (1 << bit);
    }
bit_delay(baudrate);
if (PIND & (1 << RXBIT))     // stop bit high ?
	{
	if (ubwrt == UBSIZE) ubwrt = 0;
	if(ubcount++ < UBSIZE)
	        uart_buf[ubwrt++] = val;
	}
 }

void disable_uart(uint16_t baud)   // Only  2400, 4800, 9600 and 19200 are allowed
{
DDRD    &=  ~(1 << TXBIT);       // Transmit pin as input
GICR &= ~(1<<INT0);		 // Disable INT0
cli();   				                  //disable interrupt globally
}

void enable_uart(uint16_t baud)   // Only  2400, 4800, 9600 and 19200 are allowed
{
baudrate = baud;
ubrd = ubwrt = ubcount =0;
DDRD    |=  (1 << TXBIT);         // Transmit pin as output
PORTD  |=  (1 << TXBIT);        // and set it HIGH

PORTD = (1 <<  RXBIT);         // Enable  pullup on PD2 (INT0 pin) receive pin
MCUCR = (1<<ISC01);		  // Falling edge on INT0
GICR = (1<<INT0);		          // Enable INT0
sei();   				                  //enable interrupt globally
}

uint8_t  uart_read()            // Should be called only if ubcount > 0
{
if (!ubcount) return 0;
--ubcount;
if (ubrd == UBSIZE) ubrd = 0;
return uart_buf[ubrd++];
}

uint8_t  uart_rxdata()
{
return ubcount;
}

void uart_write(uint8_t ch)
{
uint8_t bit;

PORTD &= ~(1 << TXBIT);
bit_delay(baudrate);
for(bit=0; bit <= 7; ++bit)
	{
	if(ch & 1)
		PORTD |= (1 << TXBIT);
	else
		PORTD &= ~(1 << TXBIT);
	ch >>= 1;
	bit_delay(baudrate);
	}
PORTD |= (1 << TXBIT);	// stop bit
bit_delay(baudrate);
}

