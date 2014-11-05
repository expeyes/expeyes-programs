/*  
EYES for Young Engineers & Scientists (EYES  1.0)
Program : eyes.c, running on AtMega32 micro-controller
Listens on the RS232 port for commands fom the PC, by eyes.py, and acts accordingly.
Author  : Ajith Kumar B.P, ( bpajith at gmail.com )
License : GNU GPL version 3
First Edit on 1-Sep-2010
Last Edit 23-Dec-2010 : added CAPTURE_M32
Last Edit 27-Jan-2011 : added ECHO
Last Edit 13-Oct-2011 : added IRSEND
*/

#include <avr/io.h>
#include <avr/pgmspace.h>
#include <avr/eeprom.h>

#define	GROUPSIZE	40	// Up to 40 commands in each group

// commands without any arguments (1 to 40)
#define GETVERSION	1	// Get the Eyes firmware version
#define DIGIN		2	// Digital Input (4 bits)
#define USOUND		3	// Send a pulse on OD1 and look for echo on ID2

// Commands with One byte argument (41 to 80) 
#define SETSAMTIME	41	// MCP3208 sampling duration
#define SETADCSIZE	42	// ADC data size (1 or 2)
#define READADC		43	// Read the specified ADC channel
#define R2FTIME		44	// Rise to Fall of signal on input pins
#define R2RTIME		45	// Rise to Fall of signal on input pins
#define F2RTIME		46	// Fall to Rise of signal on input pins
#define F2FTIME		47	// Fall to Rise of signal on input pins
#define SET2RTIME	48	// Setting of bit to rising edge
#define SET2FTIME	49	// to falling time
#define CLR2RTIME	50	// Setting of bit to rising edge
#define CLR2FTIME	51	// to falling time
#define PULSE2RTIME	52	// Pulse to rising edge
#define PULSE2FTIME	53	// Pulse to rising edge
#define SETPULSEWID	54	// width for PULSE2 functions (0 to 250)
#define SETPULSEPOL	55	// PULSE polarity (0 for HIGH true)
#define	DIGOUT 		56	// Digital output (4 bits)
#define ADC2CMP		57	// Route ADC input to ACOMP-
#define SETPWM		58	// Set 488 Hz PWM wave on TC0
#define SETPWMDAC	59	// Set 31.25 kHz PWM wave on TC0
#define GETPORT		60	// PINX data from port X
#define IRSEND		61  // IR transmission using SQR1 output

// Commands with Two bytes argument (81 to 120)
#define	SETPWM0		81	// PWM on on OSC0
#define	SETCOUNTER0	82	// Square wave on OSC2
#define	SETCOUNTER2	83	// Square wave on OSC2
#define	SETACTION	84	// Capture Actions of SET/CLR/PULSE & WAIT type
#define MULTIR2R	85	// Rising edge to a rising edge after N cycles
#define ADCTRIGS	86	// Trigger levels for read_block functions
#define SETWAVEFORM	87	// ISR Wavegen. OCR0 and which DAC from the caller
#define PULSE_D0D1	88	// Interrupt driven square wave on D0 and D1
#define SETDDR		90	// DDRX = dirmask (arg1 = X, arg2 = mask)
#define SETPORT		91	// PORTX = DATA (arg1 = X, arg2 = DATA)

// Commands with Three bytes argument (121 to 160)
#define SETDAC		121	// Serial DAC: send ch, dlo & dhi
#define	QCAPTURE01	122	// 2 bytes N, 1 byte dt. captures channel 0 and 1
#define WREEPROM	123	// Write EEPROM , 2 byte addr & 1 byte data
#define RDEEPROM	124	// Read EEPROM , 2 byte addr , 1 byte number of bytes 

// Commands with Four bytes argument (161 to 200)
#define	CAPTURE01	161	// 2 bytes N, 2 bytes dt. Capture channel 0 and 1
#define	QCAPTURE	162	// Ch, 2 byte N, 1 byte dt. 

// Commands with Five bytes argument (201 to 220)
#define	CAPTURE		201		// Ch, 2 byte N, 2 byte dt. Capture single channel MCP3208
#define CAPTURE_M32	202     // Ch, 2 byte N, 2 byte dt. Capture from, uC internal ADC

// Reply from ATmega8 to the PC
#define DONE		'D'	// Command executed successfully
#define	INVCMD		'C'	// Invalid Command
#define INVARG		'A'	// Invalid input data
#define INVBUFSIZE	'B'	// Resulting data exceeds buffersize
#define TIMEOUT		'T'	// Time measurement timed out

#define TRUE	1
#define FALSE	0
#define TIMERSIZE	50000	// count for 50 ms before clearing
#define TIMEOUTVAL	40		// 50 ms x 40 = 2 seconds
#define MAXTG		1000	// Maximum timegap for CAPTURE, usec
#define MAXTGQ		100		// Same for qcapture
#define MINTG		20		// Minimum timegap for CAPTURE, usec
#define MINTGQ		10		// Same for qcapture
#define	DEADTIME	5		// for PULSE2 calls

typedef uint16_t  u16;
typedef uint8_t  u8, *u8ptr;
typedef u8 boolean;

const char version[] PROGMEM = "ey1.0";


u16 tmp16;					// Gloabal temporary variable

#define	BUFSIZE		1800		// 1800 for atmega32
//----------------------- Global variables -----------------------------
u8 	dbuffer[2 + BUFSIZE];	// status + adc_size info + Databytes
u16 buf_index;
u8  adc_size = 1;
u8	sampling_time = 200;
u8	HTM;					// third byte of timer
u8 	pulse_width = 13;		// Used by PULSE2*time functions
u8	pulse_pol = 0;
u8	action;					// SET/CLR/PULSE and WAIT actions
u8	actionmask;				// Digital I/O bits for action
u8	triglo = 125;			// Trigger around the ADC mid range
u8	trighi = 131;


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

u8  hi;		// hi MUST be global to meet timing !!!. Need some assembly code ??
u8 lo;

//---------------------Capture using ATmega32 Internal ADC. Having some trouble !!! -------------------
void capture_m32(u8 ch, u16 np, u16 timegap)  // sqr1 = ch7, sqr2 = ch6, SENSOR = ch5
{
	ADCSRA = (1 << ADEN)  | (1<<ADSC) | 1;	// start a dummy conversion
    if(timegap < 20) lo = (1<<ADEN) | (1<<ADSC) | 1;
    else if(timegap < 40) lo = (1<<ADEN) | (1<<ADSC) | 2;
    else if(timegap < 80) lo = (1<<ADEN) | (1<<ADSC) | 3;
    else if(timegap < 160)lo = (1<<ADEN) | (1<<ADSC) | 4;
    else if(timegap < 320)lo = (1<<ADEN) | (1<<ADSC) | 5;
    else lo = (1<<ADEN) | (1<<ADSC) | 6;
	
	TCCR1B = (1<<CS11);		// Counter1 Normal mode, 1 MHz
      
    ADMUX = (1<<REFS0) |(1 << ADLAR) | ch; // MUX
    timegap -= 1;
	PORTC |= 128;
    while ( !(ADCSRA & (1<<ADIF)) ) ;	// wait for ADC conversion
    ADCSRA |= ADIF;						// reset ADC flag

    for(tmp16=0; tmp16 < np; ++tmp16)	// Sample in timed loop
       {
	   TCNT1 = 0;
       ADCSRA = lo;
       while ( !(ADCSRA & (1<<ADIF)) ) ;	// wait for ADC conversion
       dbuffer[buf_index++] = ADCH;
       ADCSRA |= ADIF;						// reset ADC flag
	   while(TCNT1L < timegap) ;			// Wait on counter
       }
    ADCSRA = 0;								// Disable ADC 	
	PORTC &= 127;
}

//------------------------------ Reading External ADC MCP3208 -------------------------------
void qcapture_min(u8 ch, u16 np, u8 timer)	// only for 10 microseconds spacing
{
	u8 d0 = ((ch & 1)<<1) | 1;	// Channel D0
	u8 d1 = (ch & 2) | 1;		// Channel D1
	u8 d2 = ((ch & 4)>>1) | 1;	// Channel D2
	timer -= 2;					// 2 usec forloop overhead
	TCCR1B = (1<<CS11);		// Counter1 Normal mode, 1 MHz
	PORTC |= 128;

	for(tmp16=0; tmp16 < np; ++tmp16)
		{
		TCNT1L = 0;
		SPIWR = OUTHI;		// start bit
		SPICTL = ADCKLO;	// 1st clock	
		SPICTL = ADCKHI;  
				// DATA remains HI, for SGL mode
		SPICTL = ADCKLO;	// 2nd clock
		SPICTL = ADCKHI;
	
		SPIWR = d2;			// Channel # D2
		SPICTL = ADCKLO;  	// 3rd clock
		SPICTL = ADCKHI;

		SPIWR = d1;			// Channel # D1
		SPICTL = ADCKLO; 	// 4th clock
		SPICTL = ADCKHI;

		SPIWR = d0;			// Channel # D0
		SPICTL = ADCKLO;	// 5th clock
		SPICTL = ADCKHI; SPICTL = ADCKHI; 		//samplimg start

		SPICTL = ADCKLO; SPICTL = ADCKLO;  		// 6th clock
		SPICTL = ADCKHI; 						// sampling end
		SPICTL = ADCKLO;	// 7th clock, Null bit
		SPICTL = ADCKHI;  

		SPICTL = ADCKLO;	// 8th clock, B11
		SPICTL = ADCKHI;
		hi = SPIRD & 1;

		SPICTL = ADCKLO;	// 9th clock, B10
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);

		SPICTL = ADCKLO;	// 10th clock, B9
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);
 
		SPICTL = ADCKLO;	// 11th clock, B8
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);

		SPICTL = ADCKLO;	// 12th clock, B7
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);
	
		SPICTL = ADCKLO;	// 13th clock, B6
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);

		SPICTL = ADCKLO;	// 14th clock, B5
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);

		SPICTL = ADCKLO;	// 15th clock, B4
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);

		SPICTL = CSHI;
		while(TCNT1L < timer) ;		// Wait on counter
		dbuffer[buf_index++] = hi;	// store data
		}
	PORTC &= 127;
}

void qcapture(u8 ch, u16 np, u8 timer)
{
	u8 d0 = ((ch & 1)<<1) | 1;	// Channel D0
	u8 d1 = (ch & 2) | 1;		// Channel D1
	u8 d2 = ((ch & 4)>>1) | 1;	// Channel D2
	timer -= 2;					// 2 usec forloop overhead
	TCCR1B = (1<<CS11);		// Counter1 Normal mode, 1 MHz
	PORTC |= 128;

	for(tmp16=0; tmp16 < np; ++tmp16)
		{
		TCNT1L = 0;
		SPIWR = OUTHI;		// start bit
		SPICTL = ADCKLO;	// 1st clock	
		SPICTL = ADCKHI;  
				// DATA remains HI, for SGL mode
		SPICTL = ADCKLO;	// 2nd clock
		SPICTL = ADCKHI;
	
		SPIWR = d2;			// Channel # D2
		SPICTL = ADCKLO;  	// 3rd clock
		SPICTL = ADCKHI;

		SPIWR = d1;			// Channel # D1
		SPICTL = ADCKLO; 	// 4th clock
		SPICTL = ADCKHI;

		SPIWR = d0;			// Channel # D0
		SPICTL = ADCKLO;	// 5th clock
		SPICTL = ADCKHI; SPICTL = ADCKHI; 		//samplimg start

		SPICTL = ADCKLO; SPICTL = ADCKLO;  		// 6th clock
		SPICTL = ADCKHI; 						// sampling end
		SPICTL = ADCKLO;	// 7th clock, Null bit
		SPICTL = ADCKHI;  

		SPICTL = ADCKLO;	// 8th clock, B11
		SPICTL = ADCKHI;
		hi = SPIRD & 1;

		SPICTL = ADCKLO;	// 9th clock, B10
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);

		SPICTL = ADCKLO;	// 10th clock, B9
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);
 
		SPICTL = ADCKLO;	// 11th clock, B8
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);

		SPICTL = ADCKLO;	// 12th clock, B7
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);
	
		SPICTL = ADCKLO;	// 13th clock, B6
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);

		SPICTL = ADCKLO;	// 14th clock, B5
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);

		SPICTL = ADCKLO;	// 15th clock, B4
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);

		SPICTL = CSHI;
		//asm("nop");
		while(TCNT1L < timer) ;		// Wait on counter
		asm("nop"); asm("nop"); asm("nop");
		dbuffer[buf_index++] = hi;	// store data
		}
	PORTC &= 127;
}

void qcapture01(u16 np, u8 timer)	// CH0 & CH1, only for 10 microseconds spacing
{
	TCCR1B = (1<<CS11);		// Counter1 Normal mode, 1 MHz
	timer = timer*2 -2;		// 2 channels, 2 usec forloop overhead
	PORTC |= 128;

	for(tmp16=0; tmp16 < np; ++tmp16)
		{
		TCNT1L = 0;
		SPIWR = OUTHI;		// start bit
		SPICTL = ADCKLO;	// 1st clock	
		SPICTL = ADCKHI;  
				// DATA remains HI, for SGL mode
		SPICTL = ADCKLO;	// 2nd clock
		SPICTL = ADCKHI;
	
		SPIWR = OUTLO;			// Channel # D2
		SPICTL = ADCKLO;  	// 3rd clock
		SPICTL = ADCKHI;

				// D1 also is LO
		SPICTL = ADCKLO; 	// 4th clock
		SPICTL = ADCKHI;

				//	D0 is also LO
		SPICTL = ADCKLO;	// 5th clock
		SPICTL = ADCKHI; SPICTL = ADCKHI; 		//samplimg start

		SPICTL = ADCKLO; SPICTL = ADCKLO;  		// 6th clock
		SPICTL = ADCKHI; 						// sampling end
		SPICTL = ADCKLO;	// 7th clock, Null bit
		SPICTL = ADCKHI;  

		SPICTL = ADCKLO;	// 8th clock, B11
		SPICTL = ADCKHI;
		hi = SPIRD & 1;

		SPICTL = ADCKLO;	// 9th clock, B10
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);

		SPICTL = ADCKLO;	// 10th clock, B9
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);
 
		SPICTL = ADCKLO;	// 11th clock, B8
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);

		SPICTL = ADCKLO;	// 12th clock, B7
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);
	
		SPICTL = ADCKLO;	// 13th clock, B6
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);

		SPICTL = ADCKLO;	// 14th clock, B5
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);

		SPICTL = ADCKLO;	// 15th clock, B4
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);
		SPICTL = CSHI;
		dbuffer[buf_index++] = hi;	// store data

		// Read Channel #1 now
		SPIWR = OUTHI;		// start bit
		SPICTL = ADCKLO;	// 1st clock	
		SPICTL = ADCKHI;  
				// DATA remains HI, for SGL mode
		SPICTL = ADCKLO;	// 2nd clock
		SPICTL = ADCKHI;
	
		SPIWR = OUTLO;		// Channel # D2
		SPICTL = ADCKLO;  	// 3rd clock
		SPICTL = ADCKHI;

				//	D1 is also LO
		SPICTL = ADCKLO; 	// 4th clock
		SPICTL = ADCKHI;

		SPIWR = OUTHI;		// D0 is HI
		SPICTL = ADCKLO;	// 5th clock
		SPICTL = ADCKHI; SPICTL = ADCKHI; 		//samplimg start

		SPICTL = ADCKLO; SPICTL = ADCKLO;  		// 6th clock
		SPICTL = ADCKHI; 						// sampling end
		SPICTL = ADCKLO;	// 7th clock, Null bit
		SPICTL = ADCKHI;  

		SPICTL = ADCKLO;	// 8th clock, B11
		SPICTL = ADCKHI;
		hi = SPIRD & 1;

		SPICTL = ADCKLO;	// 9th clock, B10
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);

		SPICTL = ADCKLO;	// 10th clock, B9
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);
 
		SPICTL = ADCKLO;	// 11th clock, B8
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);

		SPICTL = ADCKLO;	// 12th clock, B7
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);
	
		SPICTL = ADCKLO;	// 13th clock, B6
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);

		SPICTL = ADCKLO;	// 14th clock, B5
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);

		SPICTL = ADCKLO;	// 15th clock, B4
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);
		SPICTL = CSHI;

		while(TCNT1L < timer) ;		// Wait on counter
		dbuffer[buf_index++] = hi;	// store data
		asm("nop"); asm("nop");
		}
	PORTC &= 127;
}



void capture(u8 ch, u16 np, u16 timer)
{
	u8 d0 = ((ch & 1)<<1) | 1;	// Channel D0
	u8 d1 = (ch & 2) | 1;		// Channel D1
	u8 d2 = ((ch & 4)>>1) | 1;	// Channel D2
	timer -= 2;					// 2 usec forloop overhead
	TCCR1B = (1<<CS11);		// Counter1 Normal mode, 1 MHz
	PORTC |= 128;

	for(tmp16=0; tmp16 < np; ++tmp16)
		{
		TCNT1 = 0;
		SPIWR = OUTHI;						// start bit
		SPICTL = ADCKLO; SPICTL = ADCKLO;	// 1st clock	
		SPICTL = ADCKHI; SPICTL = ADCKHI;
								// DATA remains HI, for SGL mode
		SPICTL = ADCKLO; SPICTL = ADCKLO;	// 2nd clock
		SPICTL = ADCKHI;

		SPIWR = d2;							//channel bit D2
		SPICTL = ADCKLO;SPICTL = ADCKLO;	// 3rd clock
		SPICTL = ADCKHI;

		SPIWR = d1;							//channel bit D1
		SPICTL = ADCKLO;SPICTL = ADCKLO;	// 4th clock
		SPICTL = ADCKHI;

		SPIWR = d0;							//channel bit D0
		SPICTL = ADCKLO; SPICTL = ADCKLO;	// 5th clock

		//SPICTL = ADCKHI;
		SPICTL = ADCKHI; SPICTL = ADCKHI;
		SPICTL = ADCKHI; SPICTL = ADCKHI;
		SPICTL = ADCKHI; SPICTL = ADCKHI;
		SPICTL = ADCKLO; SPICTL = ADCKLO;;  // 6th clock
		SPICTL = ADCKHI; SPICTL = ADCKHI;
		SPICTL = ADCKHI; SPICTL = ADCKHI;
		SPICTL = ADCKHI; SPICTL = ADCKHI;
		//SPICTL = ADCKHI;

		SPICTL = ADCKLO; SPICTL = ADCKLO;	// 7th clock, Null bit
		SPICTL = ADCKHI;  SPICTL = ADCKHI;
		
		SPICTL = ADCKLO;SPICTL = ADCKLO;	// 8th clock, B11
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
		hi = (hi << 1) | (SPIRD & 1);
	
		SPICTL = ADCKLO; SPICTL = ADCKLO;	// 13th clock, B6
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);

		SPICTL = ADCKLO; SPICTL = ADCKLO;	// 14th clock, B5
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);

		SPICTL = ADCKLO; SPICTL = ADCKLO;	// 15th clock, B4
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);

		SPICTL = ADCKLO; SPICTL = ADCKLO;	// 16th clock, B3
		SPICTL = ADCKHI;
		lo = (SPIRD & 1);

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

		if(adc_size > 1) 
			dbuffer[buf_index++] = lo << 4;
		dbuffer[buf_index++] = hi;

	    while(TCNT1 < timer) ;			// Wait on TCNT1	
		asm("nop");	asm("nop");	asm("nop");
		//asm("nop");	asm("nop");	asm("nop");
	    }
	PORTC &= 127;
}

void capture01(u16 np, u16 timer)
{
	timer = timer*2-2;				// 2 reads,2 usec forloop overhead
	TCCR1B = (1<<CS11);		// Counter1 Normal mode, 1 MHz
	PORTC |= 128;

	for(tmp16=0; tmp16 < np; ++tmp16)
		{
		TCNT1 = 0;
		SPIWR = OUTHI;						// start bit
		SPICTL = ADCKLO; SPICTL = ADCKLO;	// 1st clock	
		SPICTL = ADCKHI; SPICTL = ADCKHI;
								// DATA remains HI, for SGL mode
		SPICTL = ADCKLO; SPICTL = ADCKLO;	// 2nd clock
		SPICTL = ADCKHI;

		SPIWR = OUTLO;						//channel bit D2
		SPICTL = ADCKLO;SPICTL = ADCKLO;	// 3rd clock
		SPICTL = ADCKHI;

		SPIWR = OUTLO;							//channel bit D1
		SPICTL = ADCKLO;SPICTL = ADCKLO;	// 4th clock
		SPICTL = ADCKHI;

		SPIWR = OUTLO;							//channel bit D0
		SPICTL = ADCKLO; SPICTL = ADCKLO;	// 5th clock

		//SPICTL = ADCKHI;
		SPICTL = ADCKHI; SPICTL = ADCKHI;
		SPICTL = ADCKHI; SPICTL = ADCKHI;
		SPICTL = ADCKHI; SPICTL = ADCKHI;
		SPICTL = ADCKLO; SPICTL = ADCKLO;;  // 6th clock
		SPICTL = ADCKHI; SPICTL = ADCKHI;
		SPICTL = ADCKHI; SPICTL = ADCKHI;
		SPICTL = ADCKHI; SPICTL = ADCKHI;
		//SPICTL = ADCKHI;

		SPICTL = ADCKLO; SPICTL = ADCKLO;	// 7th clock, Null bit
		SPICTL = ADCKHI;  SPICTL = ADCKHI;
		
		SPICTL = ADCKLO;SPICTL = ADCKLO;	// 8th clock, B11
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
		hi = (hi << 1) | (SPIRD & 1);
	
		SPICTL = ADCKLO; SPICTL = ADCKLO;	// 13th clock, B6
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);

		SPICTL = ADCKLO; SPICTL = ADCKLO;	// 14th clock, B5
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);

		SPICTL = ADCKLO; SPICTL = ADCKLO;	// 15th clock, B4
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);

		SPICTL = ADCKLO; SPICTL = ADCKLO;	// 16th clock, B3
		SPICTL = ADCKHI;
		lo = (SPIRD & 1);

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

		if(adc_size > 1) 
			dbuffer[buf_index++] = lo << 4;
		dbuffer[buf_index++] = hi;
		
		// Read Channel #1
		SPIWR = OUTHI;						// start bit
		SPICTL = ADCKLO; SPICTL = ADCKLO;	// 1st clock	
		SPICTL = ADCKHI; SPICTL = ADCKHI;
								// DATA remains HI, for SGL mode
		SPICTL = ADCKLO; SPICTL = ADCKLO;	// 2nd clock
		SPICTL = ADCKHI;

		SPIWR = OUTLO;						//channel bit D2
		SPICTL = ADCKLO;SPICTL = ADCKLO;	// 3rd clock
		SPICTL = ADCKHI;

		SPIWR = OUTLO;							//channel bit D1
		SPICTL = ADCKLO;SPICTL = ADCKLO;	// 4th clock
		SPICTL = ADCKHI;

		SPIWR = OUTHI;							//channel bit D0
		SPICTL = ADCKLO; SPICTL = ADCKLO;	// 5th clock

		//SPICTL = ADCKHI;
		SPICTL = ADCKHI; SPICTL = ADCKHI;
		SPICTL = ADCKHI; SPICTL = ADCKHI;
		SPICTL = ADCKHI; SPICTL = ADCKHI;
		SPICTL = ADCKLO; SPICTL = ADCKLO;;  // 6th clock
		SPICTL = ADCKHI; SPICTL = ADCKHI;
		SPICTL = ADCKHI; SPICTL = ADCKHI;
		SPICTL = ADCKHI; SPICTL = ADCKHI;
		//SPICTL = ADCKHI;

		SPICTL = ADCKLO; SPICTL = ADCKLO;	// 7th clock, Null bit
		SPICTL = ADCKHI;  SPICTL = ADCKHI;
		
		SPICTL = ADCKLO;SPICTL = ADCKLO;	// 8th clock, B11
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
		hi = (hi << 1) | (SPIRD & 1);
	
		SPICTL = ADCKLO; SPICTL = ADCKLO;	// 13th clock, B6
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);

		SPICTL = ADCKLO; SPICTL = ADCKLO;	// 14th clock, B5
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);

		SPICTL = ADCKLO; SPICTL = ADCKLO;	// 15th clock, B4
		SPICTL = ADCKHI;
		hi = (hi << 1) | (SPIRD & 1);

		SPICTL = ADCKLO; SPICTL = ADCKLO;	// 16th clock, B3
		SPICTL = ADCKHI;
		lo = (SPIRD & 1);

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

		if(adc_size > 1) 
			dbuffer[buf_index++] = lo << 4;
		dbuffer[buf_index++] = hi;

	    while(TCNT1 < timer) ;		// Wait on TCNT1	
		asm("nop");	asm("nop");	asm("nop");
	    }
	PORTC &= 127;
}

u16 read_sadc(u8 ch)
{
	SPIWR = OUTHI;					   	// MCP3208 start bit
	SPICTL = ADCKLO; SPICTL = ADCKLO;	// 1st clock	
	SPICTL = ADCKHI; SPICTL = ADCKHI;

	//if(diffmode) SPIWR = OUTLO;			// DATA remains HI, for SGL mode

	SPICTL = ADCKLO;	SPICTL = ADCKLO;// 2nd clock
	SPICTL = ADCKHI;

	if(ch & 4) 							// D2 bit of channel
		SPIWR = OUTHI;		
	else
		SPIWR = OUTLO;		
	SPICTL = ADCKLO;SPICTL = ADCKLO;	// 3rd clock
	SPICTL = ADCKHI;

	if(ch & 2) 							// D1 bit of channel
		SPIWR = OUTHI;		
	else
		SPIWR = OUTLO;		
	SPICTL = ADCKLO;SPICTL = ADCKLO;	// 4th clock
	SPICTL = ADCKHI;

	if(ch & 1) 							// D0 bit of channel
		SPIWR = OUTHI;		
	else
		SPIWR = OUTLO;		
	SPICTL = ADCKLO;SPICTL = ADCKLO;	// 5th clock
	SPICTL = ADCKHI; 

	SPICTL = ADCKLO;					// 6th clock

	TCCR1B = (1<<CS11);				// Counter1 Normal mode, 1 MHz
	TCNT1 = 0;
	while(TCNT1L < sampling_time) ;		// Wait for sampling
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

	return (hi << 8) | lo;
}


void  fast_read_sadc(u8 ch)	// data saved in hi. Used by trigger routine only
{
	u8 d0 = ((ch & 1)<<1) | 1;	// Channel D0
	u8 d1 = (ch & 2) | 1;		// Channel D1
	u8 d2 = ((ch & 4)>>1) | 1;	// Channel D2

	SPIWR = OUTHI;		// start bit
	SPICTL = ADCKLO;	// 1st clock	
	SPICTL = ADCKHI;  
			// DATA remains HI, for SGL mode
	SPICTL = ADCKLO;	// 2nd clock
	SPICTL = ADCKHI;
	
	SPIWR = d2;			// Channel # D2
	SPICTL = ADCKLO;  	// 3rd clock
	SPICTL = ADCKHI;

	SPIWR = d1;			// Channel # D1
	SPICTL = ADCKLO; 	// 4th clock
	SPICTL = ADCKHI;

	SPIWR = d0;			// Channel # D0
	SPICTL = ADCKLO;	// 5th clock
	SPICTL = ADCKHI; SPICTL = ADCKHI; 		//samplimg start

	SPICTL = ADCKLO; SPICTL = ADCKLO;  		// 6th clock
	SPICTL = ADCKHI; 						// sampling end
	SPICTL = ADCKLO;	// 7th clock, Null bit
	SPICTL = ADCKHI;  

	SPICTL = ADCKLO;	// 8th clock, B11
	SPICTL = ADCKHI;
	hi = SPIRD & 1;

	SPICTL = ADCKLO;	// 9th clock, B10
	SPICTL = ADCKHI;
	hi = (hi << 1) | (SPIRD & 1);

	SPICTL = ADCKLO;	// 10th clock, B9
	SPICTL = ADCKHI;
	hi = (hi << 1) | (SPIRD & 1);
 
	SPICTL = ADCKLO;	// 11th clock, B8
	SPICTL = ADCKHI;
	hi = (hi << 1) | (SPIRD & 1);

	SPICTL = ADCKLO;	// 12th clock, B7
	SPICTL = ADCKHI;
	hi = (hi << 1) | (SPIRD & 1);
	
	SPICTL = ADCKLO;	// 13th clock, B6
	SPICTL = ADCKHI;
	hi = (hi << 1) | (SPIRD & 1);

	SPICTL = ADCKLO;	// 14th clock, B5
	SPICTL = ADCKHI;
	hi = (hi << 1) | (SPIRD & 1);
	SPICTL = ADCKLO;	// 15th clock, B4
	SPICTL = ADCKHI;
	hi = (hi << 1) | (SPIRD & 1);
	SPICTL = CSHI;
}


void set_dac(u8 ch, u16 val)		// channel number & data
{
	SPICTL = DACKLO;						// DAC CS and CLK goes LO
	SPIWR = (ch << 1) | 1;					// channel select bit and PB0 pullup
	SPICTL = DACKLO;	SPICTL = DACKLO;	// 1st clock	
	SPICTL = DACKHI;    SPICTL = DACKHI;
	
	SPIWR = OUTHI;			// Buffer enable
	SPICTL = DACKLO;	SPICTL = DACKLO;	// 2st clock	
	SPICTL = DACKHI;    SPICTL = DACKHI;

	SPIWR = OUTHI;			// gain = 1
	SPICTL = DACKLO;	SPICTL = DACKLO;	// 3rd clock	
	SPICTL = DACKHI;    SPICTL = DACKHI;

	SPIWR = OUTHI;			// power down bit
	SPICTL = DACKLO;	SPICTL = DACKLO;	// 4th clock	
	SPICTL = DACKHI;    SPICTL = DACKHI;

	tmp16 = 0x800;
	for(hi=0; hi<12; ++hi)
		{
		if(tmp16 & val)
			SPIWR = OUTHI;			// data bit PB1 + pullup PB0
		else
			SPIWR = OUTLO;
		SPICTL = DACKLO;	SPICTL = DACKLO;	// send clock	
		SPICTL = DACKHI;    SPICTL = DACKHI;
		tmp16 >>= 1;
		}
	SPICTL = CSHI;
}


//------------------ Time Interval Measurements ----------------------
boolean wait_for_high(u8 mask)	// Wait until the Input is HIGH
{
/*Returns TRUE if any of the Digital Input Socket specified in the 
'mask' goes HIGH. If mask is zero, waits for a rising edge on CMP
input socket. Timeout after '50 * TIMEOUTVAL' milliseconds.
*/
for(;;)
    {
    if(mask)			// Check on Digins
       {
       if(PINC & mask)		// Digital Input specified by mask is HIGH ?
         break;
       }
    else			// Mask = 0 means ACMP input
      if(~ACSR & (1<< ACO))	// When AIN- goes above 1.23V, ACO goes LOW
        break;
       
    if(TCNT1 > TIMERSIZE)
       {
       TCNT1 = 0;
       if(++HTM > TIMEOUTVAL)
         {
         dbuffer[0] = TIMEOUT;		// Timeout error
         return FALSE;
         }
       }
    }
return TRUE;
}

boolean wait_for_low(u8 mask)	// Wait until the Input is LOW
{
for(;;)
    {
    if(mask)			// Check on Digins
       {
       if(~PINC & mask)		// Digital Input specified by mask is LOW ?
         break;
       }
    else			// Mask = 0 means ACMP input
      if(ACSR & (1<< ACO))	// When AIN- goes below 1.23V, ACO goes HIGH
        break;
       
    if(TCNT1 > TIMERSIZE)
       {
       TCNT1 = 0;
       if(++HTM > TIMEOUTVAL)
         {
         dbuffer[0] = TIMEOUT;		// Timeout error
         return FALSE;
         }
       }
    }
return TRUE;
}


boolean clear_on_rise(u8 mask)	// Clear counters on rising edge
{
/* Clears the TCNT1 register and variable HTM and returns TRUE if any of the 
Digital Input (sockets) specified in the 'mask'goes HIGH. 
If mask is zero, waits for a rising edge on analog comparator
input socket.
*/
HTM = 0;
for(;;)
    {
    if(mask)			// Check on Digins
       {
       if(PINC & mask)		// Digital Input specified by mask
         break;
       }
    else			// Mask = 0 means ACMP input
      if(~ACSR & (1<< ACO))	// When AIN- goes above 1.23V, ACO goes LOW
        break;
       
    if(TCNT1 > TIMERSIZE)
       {
       TCNT1 = 0;
       if(++HTM > TIMEOUTVAL)
         {
         dbuffer[0] = TIMEOUT;		// Timeout error
         return FALSE;
         }
       }
    }
TCNT1 = 0; 
HTM = 0;
return TRUE;
}

boolean clear_on_fall(u8 mask)	// Clear counters on falling edge
{
HTM = 0;
for(;;)
    {
    if(mask)			
       {
       if(~PINC & mask)		// Digital Input specified by mask
         break;
       }
    else			// Mask = 0 means ACMP input
      if(ACSR & (1<< ACO))	// When AIN- goes below 1.23V, ACO goes HIGH
        break;

    if(TCNT1 > TIMERSIZE)
       {
       TCNT1 = 0;
       if(++HTM > TIMEOUTVAL)
         {
         dbuffer[0] = TIMEOUT;		// Timeout error
         return FALSE;
         }
       }
    }
TCNT1 = 0;    
HTM = 0;
return TRUE;
}

boolean mark_on_rise(u8 mask)	// Save the 24 bit counter to dbuffer
{
/* Saves the current value of TCNT1 register to variable 'tmp16' when the
Digital Input (sockets) specified in the 'mask' goes HIGH. If mask is zero,
save on the rising edge of analog comparator input socket.
TCNT1 is cleared every time it touches 'TIMESIZE' and variable 'HTM' is incremeted.
8 bit HTM and 16 bit TCNT1 together stores a 24 bit size time interval
that is send to the PC.
*/
for(;;)		
    {
    if(mask)			
       {
       if(PINC & mask)		// Digital Input specified by mask
         break;
       }
    else			// Mask = 0 means ACMP input
      if(~ACSR & (1<< ACO))	// When AIN- goes above 1.23V, ACO goes LOW
        break;

    if(TCNT1 > TIMERSIZE)
       {
       TCNT1 = 0;
       if(++HTM > TIMEOUTVAL)
         {
         dbuffer[0] = TIMEOUT;		// Timeout error
         return FALSE;
         }
       }
    }
dbuffer[buf_index++] = TCNT1L;
dbuffer[buf_index++] = TCNT1H;
dbuffer[buf_index++] = HTM;
return TRUE;
}

boolean mark_on_fall(u8 mask)	// Save counter to dbuffer 
{
for(;;)
    {
    if(mask)	
       {
       if(~PINC & mask)		// Digital Input specified by mask
         break;
       }
    else			// Mask = 0 means ACMP input
      if(ACSR & (1<< ACO))	// When AIN- goes below 1.23V, ACO goes HIGH
        break;
 
    if(TCNT1 > TIMERSIZE)
       {
       TCNT1 = 0;
       if(++HTM > TIMEOUTVAL)
         {
         dbuffer[0] = TIMEOUT;		// Timeout error
         return FALSE;
         }
       }
    }
dbuffer[buf_index++] = TCNT1L;
dbuffer[buf_index++] = TCNT1H;
dbuffer[buf_index++] = HTM;
return TRUE;
}


//------------------ Actions before capturing waveforms ------------------
#define	ASET 		1
#define	ACLR		2
#define	APULSEHI	3
#define	APULSELO	4
#define	AWAITHI		5
#define	AWAITLO		6
#define	AWAITRISE	7
#define	AWAITFALL	8

void triggers(u8 ch, u16 tg)
{
	TCNT1 =0;
	HTM = 0;
	switch(action)
		{
		case 0:
			for(tmp16 = 0; tmp16 < 200; ++ tmp16)	// NEED changes here
				{
				fast_read_sadc(ch);		// result stored in hi
				lo = hi;
				TCNT1 = 0;
				while(TCNT1 < 20) ;
				fast_read_sadc(ch);		// result stored in hi
				if( (lo < hi) && (hi >= triglo) && (hi <= trighi) ) break;
				}
			break;

		case ASET:
	        PORTC |= actionmask;			// Set the output bits as per mask
			break;

      	case ACLR:
	        PORTC &= ~actionmask;			// Clear the output bits as per mask
			break;

		case APULSEHI:
	        PORTC |= actionmask;			// Set the output bits as per mask
			TCNT1 = 0;
			while(TCNT1 < pulse_width) ;	// delay			
	        PORTC &= ~actionmask;			// Clear the output bits as per mask
			break;

        case APULSELO:
	        PORTC &= ~actionmask; 			// Clear the output bit as per mask
			TCNT1 = 0;
			while(TCNT1 < pulse_width) ;	// delay			
    	    PORTC |= actionmask;			// Set the output bits as per mask
			break;

		case AWAITHI:
			wait_for_high(actionmask); 		// Wait for HIGH
	        break;

		case AWAITLO:
	        wait_for_low(actionmask);  		// Wait for LOW
	        break;

		case AWAITRISE:
	        wait_for_low(actionmask);  		// Wait for LOW and then
			wait_for_high(actionmask); 		// Wait for HIGH
	        break;

		case AWAITFALL:
			wait_for_high(actionmask); 		// Wait for HIGH and then
	        wait_for_low(actionmask);  		// Wait for LOW
	        break;
        }
	dbuffer[0] = 'D';						// Action timeout NOT an error ???
}


int main()
{
u8 cmd,ch;
u16 ns, tg;				// Number of samples and Time gap
DDRA = 31; 				// D0 to D4 are 555 capacitor switches. DDR will change.
PORTA = 0;				// no pullups
DDRB = 2+8;				// Serial OUT , OC0
DDRC = 0xF0;			// 4 MSBs are outputs
DDRD = 128+16+8+4;		// PWG, CSDAC, CSADC, CLOCK
PORTC= 3;				// Enable pullup resistors for PC0 and PC1


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
    while ( !(UCSRA & (1<<RXC)) ) ;			// wait for receiver data
    dbuffer[buf_index++] = UDR;		    	// Put the byte in the buffer.

    if(buf_index*GROUPSIZE > dbuffer[0])	// Process after required no. of arguments
      {
	  HTM = 0; TCNT1 = 0;		// Keep them in known state
	  cmd = dbuffer[0];
	  dbuffer[0] = 'D';			// Fill reply Assuming Success
	  buf_index = 1;			// Filling of return Data from second byte onwards
	  //PORTC |= 32; used for touble shooting
      switch(cmd)
		 {
		 case CAPTURE_M32:
			ch = dbuffer[1];					  // ATmega32 ADC channel
	  		ns = dbuffer[2] | (dbuffer[3] << 8);  // Number of samples
			tg = dbuffer[4] | (dbuffer[5] << 8) ; // Time gap
			capture_m32(ch, ns, tg);
			break;

	     case CAPTURE:
			ch = dbuffer[1];					  // ADC channel
	  		ns = dbuffer[2] | (dbuffer[3] << 8);  // Number of samples
			tg = dbuffer[4] | (dbuffer[5] << 8) ; // Time gap
			if( (ns*adc_size > BUFSIZE) || (tg < MINTG) || (tg > MAXTG))
				{
          		dbuffer[0] = INVARG;
          		break;
				}
			triggers(ch,tg);
			dbuffer[buf_index++] = adc_size;	 // adc_size to the caller
			capture(ch, ns, tg);    // dbuffer[1] is channel #		 
		    break;

	     case CAPTURE01:	// Captures ch0 & ch1
	  		ns = dbuffer[1] | (dbuffer[2] << 8);  // Number of samples
			tg = dbuffer[3] | (dbuffer[4] << 8);	 // Time gap
			if( (2*ns*adc_size > BUFSIZE) || (tg < MINTG) ||(tg > MAXTG))
				{
          		dbuffer[0] = INVARG;
          		break;
				}
			dbuffer[buf_index++] = adc_size;		 // adc_size to the caller
			triggers(0,tg);
			capture01(ns, tg); 		 
		    break;

         case QCAPTURE:
			ch = dbuffer[1];
	  		ns = dbuffer[2] | (dbuffer[3] << 8);  // Number of samples
			tg = dbuffer[4];
			if( (ns > BUFSIZE) || (tg < MINTGQ) || (tg > MAXTGQ))
				{
          		dbuffer[0] = INVARG;
          		break;
				}
			triggers(ch,tg);
			if(dbuffer[4] == 10)		// Special case Time gap
				qcapture_min(ch, ns, dbuffer[4]);
			else
				qcapture(ch, ns, dbuffer[4]);
			break;

	     case QCAPTURE01:	// Captures ch0 & ch1
	  		ns = dbuffer[1] | (dbuffer[2] << 8);   // Number of samples
			tg = dbuffer[3];
			if( (2*ns > BUFSIZE) || (tg < MINTGQ)|| (tg > MAXTGQ))
				{
          		dbuffer[0] = INVARG;
          		break;
				}
			triggers(0,tg);
			qcapture01(ns, dbuffer[3]); 	  // [3] is time gap
		    break;

 	     case SETADCSIZE:		// 12 bit ADC, set to 1 or 2 bytes
        	if(dbuffer[1] > 2)
          		{
          		dbuffer[0] = INVARG;
          		break;
          		}
	        adc_size = dbuffer[1];
    	    break;

 	     case SETSAMTIME:		// Serial ADC, sampling time, clock 6
        	if(dbuffer[1] > 250)
          		{
          		dbuffer[0] = INVARG;
          		break;
          		}
	        sampling_time = dbuffer[1];
    	    break;

	     case READADC:		// Reads the requested channel of MCP3208 ADC
			tmp16 = read_sadc(dbuffer[1]);
			tmp16 += read_sadc(dbuffer[1]);
			tmp16 += read_sadc(dbuffer[1]);
			tmp16 += read_sadc(dbuffer[1]);
			tmp16 /= 4;
			dbuffer[buf_index++] = tmp16 & 255;
			dbuffer[buf_index++] = tmp16 >> 8;
 	        break;

	     case SETDAC:			// Set the MCP4922 DAC
	  		set_dac(dbuffer[1], dbuffer[2] | (dbuffer[3] << 8));
      		break;

	     case SETACTION:
/* 
action 1 to 4 : SET/CLR/PULSE Digital Outputs just before capturing waveform.
action 5 to 8 : Waits on Levels/Edges on Digital Inputs.
actionmask MSBs keep the Digout Bits. LSBs keep the Digin Bits.
*/
			if(dbuffer[1] <= 4)
				{
				action = dbuffer[1];
				actionmask = dbuffer[2] << 4;	// keep in high nibble
				}
			else
			if(dbuffer[1] <= 8)
				{
				action = dbuffer[1];
				actionmask = dbuffer[2] & 15;	// Keep in low nibble
				}
			else
          		dbuffer[0] = INVARG;
	        break;

    	 case ADCTRIGS:
/* To get a stable display of periodic waveform, every time the digitization
should start roughly at the same position of the waveform. Two levels are
specified to allow rising and falling edge triggering.
*/    
	     	triglo = dbuffer[1];			// First Trigger level
		    trighi = dbuffer[2];			// Second Trigger Level
		    break;

		 case ADC2CMP:	// ch > 7 means disconnect routing
			if(dbuffer[1] <= 7)				
				{
		        ADMUX = dbuffer[1];		
      			SFIOR = (1 << ACME);	 	// Route ADC input to AIN-
		        ADCSRA = 0;					// Disable ADC
				}
			else
				SFIOR = 0;					// Disconnect AIN- from ADC inputs 
			break;			

// Timer Counter related functions start here.
	     case SETCOUNTER0:	// TC0 in CTC mode, caller sends CS bits & OCR0
	        TCCR0 = (1<<WGM01) | (1<<COM00) | (dbuffer[1] & 7);	
	        OCR0 = dbuffer[2];
		    break;

	     case SETCOUNTER2:	// TC2 in CTC mode, caller sends CS bits & OCR2
	        TCCR2 = (1<<WGM21) | (1<<COM20) | (dbuffer[1] & 7);	
	        OCR2 = dbuffer[2];
		    break;

	     case SETPWM:			// Set TC0 to 488 Hz PWM 
			if(dbuffer[1] == 0) 
				TCCR0 = 0;		// Switch off
			else
				{
	      		OCR0 = dbuffer[1];
    	  		TCCR0 = (1<<WGM01) | (1<<WGM00) | (1<<COM01) | (1<<CS01) | (1<<CS00); // Fast PWM mode
				}
      		break;

	     case SETPWMDAC:			// Set TC0 to 31.25 kHz PWM 
			if(dbuffer[1] == 0) 
				TCCR0 = 0;		// Switch off
			else
				{
	      		OCR0 = dbuffer[1];
    	  		TCCR0 = (1<<WGM01) | (1<<WGM00) | (1<<COM01) | (1<<CS00); // Fast PWM mode
				}
      		break;


	     case IRSEND:
			// Infrared communication vis SQR1 output
			// Sets TC2 in CTC mode, as per the byte to send
			#define SPACE 500
			OCR2 = 104;  										// f = 1e6/256/OCR2
			TCCR2 = (1<<WGM21) | (1<<COM20) | ( 1 << CS20);		// Counter2 CTC mode, pre-scale = 1
			TCNT1 = 0; while(TCNT1 < SPACE*5);		// beginning
			TCCR2 = 0;
			TCNT1 = 0; while(TCNT1 < SPACE);

			lo = dbuffer[1];			// byte to transmit
			for(hi=0; hi < 8; ++hi)
				{
				TCCR2 = (1<<WGM21) | (1<<COM20) | ( 1 << CS20);		// Counter2 CTC mode, pre-scale = 1
				TCNT1 = 0; while(TCNT1 < SPACE) ;
				TCCR2 = 0;
				TCNT1 = 0; while(TCNT1 < SPACE);
				if(lo & 128)
					{
					TCNT1 = 0; while(TCNT1 < SPACE);			
					}
				lo <<= 1;
				}
			TCCR2 = (1<<WGM21) | (1<<COM20) | ( 1 << CS20);		// Counter2 CTC mode, pre-scale = 1
			TCNT1 = 0; while(TCNT1 < SPACE) ;
			TCCR2 = 0;
			TCNT1 = 0; while(TCNT1 < SPACE) ;
		    break;

/*-------------------- Passive Time Interval Measurements.-----------------
 Time interval measurement functions using DIGITAL I/O and ACOMP Sockets.
The 16 bit Timer/Counter is used for time measurements. A 1 MHz clock is fed
to the counter and the variable HTM is incremented after when it reaches 50000.
Timeout is provided on all time measurements.
Measures the time interval between a Level Transition one Digital Input to 
another. The 8 bit input data specifies the Input Sockets to wait for.
The HIGH 4 bits contain the Sockets to look for the First Transition.
For example dbuffer[1] = 00100001, time between a transition on D1 to a 
transition on D0 is measured.
In fact it is possible to wait for more than one sockets at the same time and 
which ever come first can be taken. At the moment the Python function sets only 
a single bit in each half. The Start and Stop inputs could be same or different.

A special case arise when all the 4 bits are zero. In that case transition on
the Analog Comparator input Socket is waited for. Using the ADC2CMP function,
it is possible to route ADC input pins to Analog Comaparator Input.
*/ 
	     case R2RTIME:
			hi = dbuffer[1] >> 4;		// 4 MSBs start pins
     		lo = dbuffer[1] & 15;		// 4 LSBs end pins
      		if(wait_for_low(hi))		// Just make sure the level is LOW
        	  if(clear_on_rise(hi))		// Clear counter on rising edge src pin 
          		if(wait_for_low(lo))	// DST pin should be LOW
            	  mark_on_rise(lo);		// Store counters at rising edge dst pin
      		break;

	     case F2FTIME:
			hi = dbuffer[1] >> 4;		// 4 MSBs start pins
     		lo = dbuffer[1] & 15;		// 4 LSBs end pins
      		if(wait_for_high(hi))		// Just make sure the level is HIGH
        	  if(clear_on_fall(hi))		// Clear counter on falling edge src pin 
          		if(wait_for_high(lo))	// DST pin should be HIGH
            	  mark_on_fall(lo);		// Store counters at falling edge dst pin
      		break;

	     case R2FTIME:
			hi = dbuffer[1] >> 4;		// 4 MSBs start pins
     		lo = dbuffer[1] & 15;		// 4 LSBs end pins
      		if(wait_for_low(hi))		// Just make sure the level is LOW
        	  if(clear_on_rise(hi))		// Clear counter on rising edge src pin 
            	mark_on_fall(lo);		// Store counters at falling edge dst pin
      		break;

	     case F2RTIME:
			hi = dbuffer[1] >> 4;		// 4 MSBs start pins
     		lo = dbuffer[1] & 15;		// 4 LSBs end pins
      		if(wait_for_high(hi))		// Just make sure the level is HIGH
        	  if(clear_on_fall(hi))		// Clear counter on falling edge src pin 
            	mark_on_rise(lo);		// Store counters at rising edge dst pin
      		break;
		
	     case MULTIR2R:	
/* Measures the time interval between two rising edges on the same Input Socket.
The 4 LSBs of the first argument specifies the Input Socket to look for.
The second argument specifies the number of rising edges to be skipped in between
the two edges measured. For example dbuffer[2] = 9 returns the time taken
for 10 cycles. Averaging is useful for  better measurement accuracy.
*/    
	      	lo = dbuffer[1] & 15;		// pin number in 4 LSBs 
      		TCNT1 =0;
      		HTM = 0;
      		if(!wait_for_low(lo)) break;	// Make sure the level is LOW
      		if(!clear_on_rise(lo))break;	// Clear counter on rising edge src pin 
      		if(!wait_for_low(lo)) break;
     
      		while (dbuffer[2]--)
      			{
		        if(!wait_for_high(lo))break;
        		if(!wait_for_low(lo)) break;
        		}
			if(dbuffer[0] == TIMEOUT) break;
  			mark_on_rise(lo);				// Store counters at rising edge
		    break;

/*-------------------- Active Time Interval Measurements ----------------------
Sets the DIGITAL Output Sockets as per the 4 MSBs of the argument and measures 
the time from that to a Level Transition on the Input Socket specified by the 4 LSBs 
of the argument. 4 LSBs zero means Analog Comparator.
*/  
		 case SET2RTIME:
        	PORTC |= dbuffer[1] & 0xF0;		// SET as per 4 MSBs 
      		HTM = 0;
      		TCNT1 = 0;
      		mark_on_rise(dbuffer[1] & 15);	// Wait as per 4 LSBs
    		break;

		 case SET2FTIME:
        	PORTC |= dbuffer[1] & 0xF0;		// SET as per 4 MSBs 
      		HTM = 0;
      		TCNT1 = 0;
      		mark_on_fall(dbuffer[1] & 15);	// Wait as per 4 LSBs
    		break;

		 case CLR2RTIME:
        	PORTC &= ~(dbuffer[1] & 0xF0);	// CLR as per 4 MSBs 
      		HTM = 0;
      		TCNT1 = 0;
      		mark_on_rise(dbuffer[1] & 15);	// Wait as per 4 LSBs
    		break;

		 case CLR2FTIME:
        	PORTC &= ~(dbuffer[1] & 0xF0);	// CLR as per 4 MSBs 
      		HTM = 0;
      		TCNT1 = 0;
      		mark_on_fall(dbuffer[1] & 15);	// Wait as per 4 LSBs
    		break;

		 case SETPULSEWID:
			pulse_width = dbuffer[1];
		    break;

    	 case SETPULSEPOL:			// For the PULSE2* functions
	     	pulse_pol = dbuffer[1];
      		break;

		 case USOUND:					// Sends a Pulse of PC5, look on PC2	
       		PORTC |= (1 << PC4);			// set OD0
			TCNT1 = 0;
			while(TCNT1L < pulse_width) ;	//kill time
	        PORTC &= ~(1 << PC4);			// Clear OD0
		    HTM = 0;
			TCNT1 = 0;     
			while(TCNT1 < DEADTIME) ;		// Wait to settle noise
		    mark_on_rise(1<<PC2);			// Store counters at rising of PC2
			break;			

		 case PULSE2RTIME:	
		 case PULSE2FTIME:	
			hi = dbuffer[1] & 0xF0;		// 4 MSBs start pins
     		lo = dbuffer[1] & 15;		// 4 LSBs end pins
		    if(pulse_pol)				// HIGH TRUE pulse
        		{
        		PORTC |= hi;			// Set source bit
				TCNT1 = 0;
				while(TCNT1L < pulse_width) ;	//kill time
		        PORTC &= ~hi;			// Restore old value
        		}
     		else						// LOW TRUE pulse
        		{
	        	PORTC &= ~hi;			// Clear source bit
				TCNT1 = 0;
				while(TCNT1L < pulse_width) ;	//kill time
		        PORTC |= hi;			// Restore old value
        		}
		    HTM = 0;
			TCNT1 = 0;     
			while(TCNT1 < DEADTIME) ;	// Wait to settle noise
			if(cmd == PULSE2RTIME)
			    mark_on_rise(lo);		// Store counters at rising of dst
			else
			    mark_on_fall(lo);		// Store counters at falling of dst

		    break;

//-----------------------Digital I/O functions-------------------------
	     case DIGOUT:
     		PORTC = (dbuffer[1] << 4) | 3;   // Only PCO & PC1 need to be pulled up
		    break;

	     case DIGIN:			// 3 bits of PortC, 4th is analog comparator output
	        ADMUX = 5;					// SENSOR output is on ADC input 5		
   			SFIOR = (1 << ACME);	 	// Route ADC input to AIN-
	        ADCSRA = 0;					// Disable ADC
     		dbuffer[buf_index++] = (PINC & 7) | ((ACSR & (1<<ACO))>>2);
     		break;

	     case WREEPROM:
			tmp16 = dbuffer[2] << 8;	// 16 bit Internal SEEPROM address by
		    tmp16 |= dbuffer[1];		// combining low and high bytes
			eeprom_write_byte ( (u8ptr)tmp16, dbuffer[3]);
	        break;

	     case RDEEPROM:
			tmp16 = dbuffer[2] << 8;	// 16 bit Internal SEEPROM address by
		    tmp16 |= dbuffer[1];		// combining low and high bytes
			ch = dbuffer[3];
			for(lo=0; lo < ch; ++lo)
				dbuffer[buf_index++] = eeprom_read_byte ((u8ptr)(tmp16+lo));
	        break;

//----------------------- Low level PORT access functions----------------
	     case SETDDR:
      		if(dbuffer[1] == 0) DDRA = dbuffer[2];
      		else if(dbuffer[1] == 1) DDRB = dbuffer[2];
		    else if(dbuffer[1] == 2) DDRC = dbuffer[2];
      		else if(dbuffer[1] == 3) DDRD = dbuffer[2];
		    break;

	     case SETPORT:
      		if(dbuffer[1] == 0) PORTA = dbuffer[2];
      		else if(dbuffer[1] == 1) PORTB = dbuffer[2];
      		else if(dbuffer[1] == 2) PORTC = dbuffer[2];
      		else if(dbuffer[1] == 3) PORTD = dbuffer[2];
      		break;
	     
		 case GETPORT:
      		if(dbuffer[1] == 0) dbuffer[buf_index++] = PINA;
      		else if(dbuffer[1] == 1) dbuffer[buf_index++] = PINB;
      		else if(dbuffer[1] == 2) dbuffer[buf_index++] = PINC;
      		else if(dbuffer[1] == 3) dbuffer[buf_index++] = PIND;
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
