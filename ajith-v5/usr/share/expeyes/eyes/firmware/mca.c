/*  
EYES MCA
Program : mca.c, running on AtMega32 micro-controller
Listens on the RS232 port for commands fom the PC, by mcalib.py, and acts accordingly.
Author  : Ajith Kumar B.P, ( bpajith at gmail.com )
License : GNU GPL version 3
Last Edit on 20-Oct-2011
*/

#include <avr/io.h>
#include <avr/pgmspace.h>
#include <avr/eeprom.h>
#include <avr/interrupt.h>

#define	GROUPSIZE	40	// Up to 40 commands in each group

// commands without any arguments (1 to 40)
#define GETVERSION	1	// Get the Eyes firmware version
#define READCH0		2   // Reads ADC channel 0
#define STARTHIST	10	// Start histogramming
#define READHIST	11	// Send the histogram to PC, 2 x 256 bytes data
#define CLEARHIST	12	// Send the histogram to PC, 2 x 256 bytes data
#define STOPHIST	13	// Stop histogramming

// Reply from ATmega8 to the PC
#define DONE		'D'	// Command executed successfully
#define	INVCMD		'C'	// Invalid Command
#define INVARG		'A'	// Invalid input data
#define INVBUFSIZE	'B'	// Resulting data exceeds buffersize
#define TIMEOUT		'T'	// Time measurement timed out

#define TRUE	1
#define FALSE	0

typedef uint16_t  u16;
typedef uint8_t  u8, *u8ptr;
typedef u8 boolean;
const char version[] PROGMEM = "mc1.0";


#define	HISTSIZE		1024		// 2 x 511 , 9 bit MCA , 16 bit words

//----------------------- Global variables -----------------------------
u8 	dbuffer[2 + HISTSIZE];	// status + pad + Data
u16 buf_index;
u16 tmp16;					// Gloabal temporary variable

// -------------------------- Serial ADC & DAC -------------------------
#define   SPICTL	PORTD			// CK=PD2, ADCS = PD3, DACS = PD4
#define   CLK 		(1 << PD2)
#define   ADCS 		(1 << PD3)
#define   DACS 		(1 << PD4)
#define	  ADCKLO	DACS			// ADCS and CLK low
#define	  ADCKHI	DACS+CLK		// ADCS low and Clock hi
#define   CSHI		DACS+ADCS+CLK	// Both CS and Clock hi
#define	  DACKLO	ADCS			// DACS and CLK low
#define	  DACKHI	ADCS+CLK		// DACS low and Clock hi
#define   SPIWR		PORTB
#define   SPIRD	    PINB
#define	  OUTHI		2+1				// PB1 HI and pullup of PB0
#define	  OUTLO		1				// PB1 LO pullup of PB0

u8  	hi, lo, HTM;	
u16 	adval;


//------------------------------ Reading External ADC MCP3208 -------------------------------
#define	  SAMTIME	5
void read_ch0()
{
	SPIWR = OUTHI;					   	// MCP3208 start bit
	SPICTL = ADCKLO; SPICTL = ADCKLO;	// 1st clock	
	SPICTL = ADCKHI; SPICTL = ADCKHI;

	//if(diffmode) SPIWR = OUTLO;			// DATA remains HI, for SGL mode

	SPICTL = ADCKLO;	SPICTL = ADCKLO;// 2nd clock
	SPICTL = ADCKHI;

	SPIWR = OUTLO;				// for ch0, D2, D1 & D0 are low
	SPICTL = ADCKLO;SPICTL = ADCKLO;	// 3rd clock
	SPICTL = ADCKHI;

	SPIWR = OUTLO;				// D1 is low
	SPICTL = ADCKLO;SPICTL = ADCKLO;	// 4th clock
	SPICTL = ADCKHI;

	SPIWR = OUTLO;				// D0 is low
	SPICTL = ADCKLO;SPICTL = ADCKLO;	// 5th clock
	SPICTL = ADCKHI; 

	SPICTL = ADCKLO;					// 6th clock

	TCCR1B = (1<<CS11);			// Counter1 Normal mode, 1 MHz
	TCNT1 = 0;
	while(TCNT1L < SAMTIME);		// Wait for sampling
	SPICTL = ADCKHI; SPICTL = ADCKHI; 

	SPICTL = ADCKLO; SPICTL = ADCKLO;	// 7th clock, Null bit
	SPICTL = ADCKHI; SPICTL = ADCKHI;

	SPICTL = ADCKLO; SPICTL = ADCKLO;	// 8th clock, B11
	SPICTL = ADCKHI;
	hi = SPIRD & 1;

	SPICTL = ADCKLO; SPICTL = ADCKLO;	// 9th clock, B10
	SPICTL = ADCKHI;
	hi = (hi << 1) | (SPIRD & 1);

	SPICTL = ADCKLO; SPICTL = ADCKLO;	// 10th clock, B9
	SPICTL = ADCKHI;
	hi = (hi << 1) | (SPIRD & 1);
 
	SPICTL = ADCKLO; SPICTL = ADCKLO;	// 11th clock, B8
	SPICTL = ADCKHI;
	hi = (hi << 1) | (SPIRD & 1);

	SPICTL = ADCKLO; SPICTL = ADCKLO;	// 12th clock, B7
	SPICTL = ADCKHI;
	lo = (SPIRD & 1);

	SPICTL = ADCKLO; SPICTL = ADCKLO;	// 13th clock, B6
	SPICTL = ADCKHI;
	lo = (lo << 1) | (SPIRD & 1);

	SPICTL = ADCKLO; SPICTL = ADCKLO;	// 14th clock, B5
	SPICTL = ADCKHI;
	lo = (lo << 1) | (SPIRD & 1);

	SPICTL = ADCKLO; SPICTL = ADCKLO;	// 15th clock, B4
	SPICTL = ADCKHI;
	lo = (lo << 1) | (SPIRD & 1);

	SPICTL = ADCKLO; SPICTL = ADCKLO;	// 16th clock, B3
	SPICTL = ADCKHI;
	lo = (lo << 1) | (SPIRD & 1);

	SPICTL = ADCKLO; SPICTL = ADCKLO;	// 17th clock, B2
	SPICTL = ADCKHI;
	lo = (lo << 1) | (SPIRD & 1);

	SPICTL = ADCKLO; SPICTL = ADCKLO;	// 18th clock, B1
	SPICTL = ADCKHI;
	lo = (lo << 1) | (SPIRD & 1);

	SPICTL = ADCKLO; SPICTL = ADCKLO;	// 19th clock, B0
	SPICTL = ADCKHI;
	lo = (lo << 1) | (SPIRD & 1);
	SPICTL = CSHI;

	adval = (hi << 8) | lo;
}

volatile u8 done = 0; 

SIGNAL(SIG_COMPARATOR)	// HISTOGRAM
{
read_ch0();				// digitize A0, 12 bit result in adval
adval >>= 3;            // right shift to make it 9 bits

++*( (u16*)dbuffer + 1 + adval);

done = 1;
PORTC &= ~0x80;			// send a LOW TRUE pulse on PC7
PORTC |= 0x80;     
}


int main()
{
u8 cmd;
DDRB =  2;			// Serial OUT , OC0(PB3) will be made output when needed
DDRD = 128+16+8+4;		// PWG, CSDAC, CSADC, CLOCK
DDRC = 0x80;			// PC7 as output
PORTC= 0x80;				

// Initialize the RS232 communication link to the PC 38400, 8, 1, E
UCSRB = (1<<RXEN) | (1<<TXEN);
//UCSRA = (1 << U2X);
UBRRH = 0;
UBRRL = 12;		// At 8MHz (12 =>38400) (25 => 19200)
UCSRC = (1<<URSEL) | (1<<UPM1) | (1<<UCSZ1) | (1<<UCSZ0); // 8,1,E

ACSR = (1<<ACBG);		// AIN(+) connected to Vbg = 1.23V
TCCR1B = (1<<CS11);		// Counter1 Normal mode, 1 MHz

buf_index = 0;
for(;;)
    {
    while ( !(UCSRA & (1<<RXC)) )  ;	// wait for receiver data
/*		{
		if (done == 1)
			{
			done = 0;
			PORTC &= ~0x80;			// send a LOW TRUE pulse on PC7
			PORTC |= 0x80;     
			}
		}
*/		
    dbuffer[buf_index++] = UDR;		    	// Put the byte in the buffer.

    if(buf_index*GROUPSIZE > dbuffer[0])	// Process after required no. of arguments
      {
	  HTM = 0; TCNT1 = 0;		// Keep them in known state
	  cmd = dbuffer[0];
	  dbuffer[0] = 'D';			// Fill reply Assuming Success
	  buf_index = 1;			// Filling of return Data from second byte onwards
      switch(cmd)
		 {
	    case STARTHIST:
			DDRB &= ~8;						// Make PB3 an input pin
			SFIOR &= ~(1<<ACME);			// Disable the Mux input routing to ACMP
	    	ACSR = (1<<ACIS0) | (1<<ACIS1) | (1<<ACBG) | (1<<ACIE);	
					// F.edge, ATmega32 doc wrong ?
			PORTC &= ~0x80;			// send a LOW TRUE pulse on PC7
			PORTC |= 0x80;     
			sei();
			break;

    	case READHIST:
    		buf_index = HISTSIZE+2;		// 1 status + 1 pad + 1024 bytes data
      		break;

    	case CLEARHIST:
    	    for(tmp16 = 1; tmp16 <= (HISTSIZE+2); ++tmp16)	// Clear the buffer
    	    	dbuffer[tmp16] = 0;
      	    break;

    	case STOPHIST:
	        ACSR &= ~(1<<ACIE);		// disable AC interrupt
      		break;

	     case READCH0:		// Reads the ch0 of MCP3208 ADC
			read_ch0();
			dbuffer[buf_index++] = lo;
			dbuffer[buf_index++] = hi;
 	        break;

		 case GETVERSION:
      		memcpy_P(&dbuffer[1], version,5);
      		buf_index += 5;
      		break;

    	 default:
      		dbuffer[0] = INVCMD;		// Invalid Command
      		break;	
         }

   	  while( !(UCSRA & (1 <<UDRE) ) );
      UDR = dbuffer[0];					// Send the response byte in all cases
	  // If no error, send the data bytes to the PC. No handshake used.
	  if(dbuffer[0] == 'D')
	 	 for(tmp16=1; tmp16 < buf_index; ++tmp16)	
      		{
    		while( !(UCSRA & (1 <<UDRE) ) );
    		UDR = dbuffer[tmp16];
			}
      buf_index = 0;
	  //PORTC &= ~32;		used for trouble shooting only
      }
    }
return 0;
}

