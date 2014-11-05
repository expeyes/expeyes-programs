/* 
Last revised on 31-3-08. Added the macros BV, sbi and cbi
Revision started on 27-11-06. TC0 and ACOMP Interrupts are now used.
   1. Command ranges changed. Maximum 40 in each group
   2. High resolution AD/DA plug-in code added
   3. Timer set & get routines
   4. Arbitrary waveform generation using interrupts added (table in FLASH)
   5. Radiation detection system histogram routines added
   6. SEEPROM plug-in code added
   7. SMRB and PMRB routines finished.  8-Dec-06
Dynamic DDRx settings:

Last revision on 30-Nov-07 : readblock calls are changed
Note: This program is written for ATmega16 working at 8MHz clock speed. Changing
clock speed will require changes in the program.

Revision May-08 : 
rewriting SPI Interface  for top panel sockets

Revision 26-Jul-08: 
Version changed to 2.4
Added code for 24bit  AD7718  ADC.
Added conditional compilation for ATmega32 chip.

Edited on 14-May-2010 to correct the r2rtime() and f2ftime() functions

*/

#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>
#include <avr/sfr_defs.h>
#include <avr/io.h>
//#include <avr/signal.h>
#include <avr/interrupt.h>
#include <avr/sleep.h>
#include <avr/pgmspace.h>
#include <avr/eeprom.h>

#ifndef BV
  #define BV(bit)  (1 << (bit))
#endif

#ifndef cbi
	#define cbi(sfr, bit) (_SFR_BYTE(sfr) &= ~_BV(bit))
#endif
#ifndef sbi
  #define sbi(sfr, bit) (_SFR_BYTE(sfr) |= _BV(bit))
#endif

typedef uint8_t	 u8, *u8ptr;
typedef uint8_t	 boolean;
typedef	uint16_t u16;
typedef	uint32_t u32;

#include "lcd16.c"

#define	GROUPSIZE	40	// Up to 40 commands in each group
// commands with no arguments (1 to 40)
#define LCD_INIT	1	// Initialize LCD Display
#define DIGIN		2	// Digital Input (4 bits)
#define	READBLOCK	3	// Digitize from currently selected channel
#define	MULTIREADBLOCK	4	// Digitize from multiple channels (start=ch0)
#define ADCREAD		5	// Digitizes the current channel
#define GETCHANMASK	6	// Return the active channel info of MRB
#define COUNT		7	// Measure the frequency counter input
#define READACOMP	8	// Analog Comparator status. 0 if IN- > 1.23V
#define GETTIME 	9	// get the time is seconds since Epoch
#define STARTHIST	10	// Start histogramming
#define READHIST	11	// Send the histogram to PC, 2 x 256 bytes data
#define CLEARHIST	12	// Send the histogram to PC, 2 x 256 bytes data
#define STOPHIST	13	// Stop histogramming
#define STOPWAVE	14	// Disable interrupt based waveform generation
#define SMRB_START	15	// Initiate an interrupt driven multi read block
#define SMRB_STATUS	16	// Returns TC0 ISR status & number of bytes 
#define SMRB_GETDATA	17	// Sends the data collected by SMRB to PC
#define SMRB_STOP	18	// Stop SMRB and disable Timer interrupt
#define PMRB_RUNNING	19	// Returns the TC0 ISR status
#define PMRB_GETDATA	20	// Data collected in PROM by PMRB to PC
#define SPI_PULL	21	// Pull one byte from SPI
#define SPI_PULL_BAR	22	// Pull one byte from SPI (AD7718 like device)
#define CHIP_DISABLE	23	// Disable all SPI device (D3,D2 & D1 to HIGH)	
#define HR_ADCINIT	24	// Initialize SPI ADC
#define HRADCREAD	25	// Digitizes the plug-in ADC ,current channel
#define GETMCUSTAT	26	// Get several microcontroller registers
#define GETVERSION	27	// Get the phoenix firmware version

// Commands with One byte argument (41 to 80) 
#define	DIGOUT 		41	// Digital output (4 bits)
#define SETADCSIZE	42	// ADC data size (1 or 2)
#define SETCURCHAN	43	// Select Current ADC channel
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
#define SETPULSEWIDTH	54	// width for PULSE2 functions (0 to 250)
#define SETPULSEPOL	55	// PULSE polarity (0 for HIGH true)
#define	ADDCHAN		56	// Add to MRB list
#define	DELCHAN		57	// Remove from MRB list
#define SETDAC		58	// Sets the PWM DAC from 0 to 5V (0 to 255)
#define TPEND		59	// Penulum Period from light barrier
#define PULSEOUT	60	// Generates 1 pulse on D3 with given T 
#define AINPERIOD	61	// Connect ADC input to ACMP to measure freq.
#define LCD_PUTCHAR	62	// Print a character on LCD Display
#define CHIP_ENABLE	63	// Enable the specified SPI device	
#define CHIP_ENABLE_BAR	64	// Enable for devices like AD7718
#define SPI_PUSH	65	// Push one byte to SPI	
#define SPI_PUSH_BAR	66	// Push one byte to SPI	
#define HR_SETCHAN	67	// Select SPI ADC channel
#define HR_CALINT	68	// internal calibration of selected channel
#define HR_CALEXT	69	// External Zero / Full scale calibration
#define GETPORT		70	// PINX data from port X

// Commands with Two bytes argument (81 to 120)
#define	SETNUMSAMPLES	81	// Number of samples per channel 
#define	SETCOUNTER2	82	// Square wave on OSC2
#define	SETADCDELAY	83	// interval between ADC conversions,10 to 1000
#define	SETACTION	84	// MRB Actions of SET/CLR type
#define WAITACTION	85	// MRB Actions of wait type
#define MULTIR2R	86	// Rising edge to a rising edge after N cycles
#define ADCTRIGLEVELS	87	// Trigger levels for read_block functions
#define HRSETDAC 	88	// Write to 16 bit DAC plug-in
#define SETWAVEFORM	89	// ISR Wavegen. OCR0 and which DAC from the caller
#define PULSE_D0D1	90	// Interrupt driven square wave on D0 and D1
#define MULTI_EDGES	91	// Multiple edges timing
#define COPY_E2S	92	// copy 128 bytes from eeprom to seeprom
#define SETDDR		93	// DDRX = dirmask (arg1 = X, arg2 = mask)
#define SETPORT		94	// PORTX = DATA (arg1 = X, arg2 = DATA)

// Commands with Three bytes argument (121 to 150)
#define READSEEPROM	121	// Read data from Seeprom plug-in
#define TABLEDATA	122	// Write one byte of WAVETABLE to AVR EPROM

// Commands with Four bytes argument (151 to 180)
#define	SETTIME		161	// Set time in seconds from Epoch
#define PMRB_START	162	// PMRB, arg: delay in secs , numblocks to do

// Reply from ATmega8 to the PC
#define DONE		'D'	// Command executed successfully
#define	INVCMD		'C'	// Invalid Command
#define INVARG		'A'	// Invalid input data
#define INVBUFSIZE	'B'	// Resulting data exceeds buffersize
#define TIMEOUT		'T'	// Time measurement timed out
#define NOCLOCK		'N'	// Clock not set error, for PMRB

#define IDLE		0	// TC0 Interrupt is not enabled
#define	CLOCK		1	// Incrementing par.pctime every second
#define USERWAVE	2	// Wave Table from AVR EEPROM, loaded by user 
#define HRUSERWAVE	3	// Wave Table from AVR EEPROM, to plug-in HRDAC
#define	IN_SMRB		4	// SLOW MRB in progress
#define IN_PMRB		5	// PROM MRB in progress
#define IN_PULSE	6	// IRQ pulsing D0 and D1

#define	TABLESIZE	100	// Number of points in one waveform cycle

#define TRUE	1
#define FALSE	0
#define TIMERSIZE	50000	// count for 50 ms before clearing

#ifdef M32
  #define BUFSIZE		1800	// ATmega32 with 2K RAM
#else
  #define BUFSIZE		800	// ATmega16 with 1K RAM
#endif

#define MAXDELAY	3000	// Delay between ADC samples
#define SLOW_CONV_MASK	7	// ADCSRA mask for Clk = (8 MHz/ 64) = 125 KHz
#define PULSEDEADTIME	10	// To avoid false triggering in PULSE2x calls
#define PMRB_INDEX	(BUFSIZE - 256) // ISR driven PMRB uses part of par.buf
#define	LOWER		0		// PMRB buffer divided, 2 x 128 bytes
#define	UPPER		1		// UPPER and LOWER

#define AVREF		BV(REFS0)	// Use AVCC as ADC reference



// Temporary variables for normal & ISR routines
// Less function arguments or local variables. Not much RAM for stack
u8	tmp8, tmp8_1, isr_tmp8;
u8	HTM;			// Increment when TCNT1 crossing TIMERSIZE
u16	tmp16, isr_tmp16;	


struct data {				// All local data in one structure
  u32	pctime;				// Time in seconds (initialized from PC)
  u16	minor_ticks;			// Number of TIMER0 interrupts received
  u16   buf_index;			// Variable for indexing the buffer
  u16	adc_delay;			// Time between samples, for READBLOCKs
  u16	num_samples;			// Number of samples, for READBLOCKs
  
  u16	pmrb_delay;			// Interval between PMRB samples
  u16	pmrb_numblocks;			// Do this many blocks of 128bytes
  u8	pmrb_chlist[4];			// channel list for PMRB
  u8	pmrb_num_chan;			// Number of active PMRB channels
  u8	pmrb_bufpos;			// position on th 2 x 128 bytes buffer
  u8	filling_half;			// upper or lower 128 byte block 
    
  u8	irq_func;			// Function of the TC0 Interrupt routine
  u8	chlist[4], num_chan, chmask;	// data for MULTIREADBLOCK call
  u8	current_chan;			// Selected channel
  u8 	adc_size, adc_ctmask;		// ADC size and conversion time mask
  u8 	timeoutval;			// Timeout is TIMERSIZE*timeoutval usecs
  u8 	pulse_width, pulse_pol;		// Used by PULSE2*time functions
  u8	buf[BUFSIZE+2];			// 1 stat + 1 MRB info + upto 800 data
  u8	set, setmask, wait, waitmask;	// SET and WAIT actions, READBLOCKs
  u8	tr1, tr2;			// ADC trigger limits
}par;		


const char version[] PROGMEM = "ph2.4";


void initialize(void){
// Initialize the RS232 communication link to the PC 38400, 8, 1, E
  UCSRB = BV (RXEN) | BV (TXEN);
  UBRRH = 0;
  UBRRL = 12;	// At 8MHz (12 =>38400) (25 => 19200)
  UCSRC = BV (URSEL) | BV (UPM1) | BV (UCSZ1) | BV (UCSZ0); // 8,1,E

  DDRA = 0xF0;			// 4 bits ADC Input , rest for LCD Data
  DDRB = 0;			// Configure as input 
  PORTB= 255;			// Enable pullup resistors
  DDRC = 0xF0;			// Low nibble Input & High nibble output
  PORTC= 15;			// Enable pullup resistors (low 4)
  DDRD = 0xff;			// All outputs
  PORTD= 0;			// All lines to LOW
  ACSR = BV(ACBG);		// AIN(+) connected to Vbg = 1.23V
  TCCR1B = BV(CS11);		// Normal mode, Clock/8 
  ADCSRA = BV(ADEN);		// Enable the ADC

  par.adc_size = 1;
  par.num_samples = 100;
  par.adc_delay = 10;		// 10 miccrosec between samples
  par.pmrb_delay = 1;		// 1 second between samples
  par.adc_ctmask = 1;		
  par.current_chan = 0;
  par.pulse_width = 13;		// default for 40 KHz piezo
  par.pulse_pol = 0;		// HIGH true pulse is default
  par.timeoutval = 40;		// 40 * TIMERSIZE (50000) (2sec)timeout default

  par.num_chan = 1;		// Channel zero is enabled by default, MRB
  par.chlist[0] = 0;		// Channel zero is first in list, MRB
  par.chmask = 1;		// mask is 0001 binary =>channel zero enabled,MRB
  
  par.set = 0;			// No SET actions while starting
  par.setmask = 0;		// No SETMASK
  par.wait = 0;			// No wait action either
  par.waitmask = 0;		// No waitmask
  par.tr1 = 125;		// Trigger around the ADC mid range
  par.tr2 = 130;

  sei();			// Enable global interrupt flag
}

//--------------------------------------------------------------------

void d100us (uint16_t k)	 // 100 usecs for k = 1
{
  volatile uint16_t x = k * 47;
  while (x)  --x;
}

void delay_us(u16 x)		// Delay routine using 16 bit timer
{
if(x < 4) return;
x -= 3;  
TCNT1 = 0;
while(1)
  if (TCNT1 >= x) 
    return;
}


boolean wait_for_high(u8 mask)	// Wait until the Input is HIGH
{
/*Returns TRUE if any of the Digital Input Socket specified in the 
'mask' goes HIGH. If mask is zero, waits for a rising edge on CMP
input socket. Timeout after '50 * par.timeoutval' milliseconds.
*/
for(;;)
    {
    if(mask)			// Check on Digins
       {
       if(PINC & mask)		// Digital Input specified by mask is HIGH ?
         break;
       }
    else			// Mask = 0 means ACMP input
      if(~ACSR & BV(ACO))	// When AIN- goes above 1.23V, ACO goes LOW
        break;
       
    if(TCNT1 > TIMERSIZE)
       {
       TCNT1 = 0;
       if(++HTM > par.timeoutval)
         {
         par.buf[0] = TIMEOUT;		// Timeout error
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
      if(ACSR & BV(ACO))	// When AIN- goes below 1.23V, ACO goes HIGH
        break;
       
    if(TCNT1 > TIMERSIZE)
       {
       TCNT1 = 0;
       if(++HTM > par.timeoutval)
         {
         par.buf[0] = TIMEOUT;		// Timeout error
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
      if(~ACSR & BV(ACO))	// When AIN- goes above 1.23V, ACO goes LOW
        break;
       
    if(TCNT1 > TIMERSIZE)
       {
       TCNT1 = 0;
       if(++HTM > par.timeoutval)
         {
         par.buf[0] = TIMEOUT;		// Timeout error
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
      if(ACSR & BV(ACO))	// When AIN- goes below 1.23V, ACO goes HIGH
        break;

    if(TCNT1 > TIMERSIZE)
       {
       TCNT1 = 0;
       if(++HTM > par.timeoutval)
         {
         par.buf[0] = TIMEOUT;		// Timeout error
         return FALSE;
         }
       }
    }
TCNT1 = 0;    
HTM = 0;
return TRUE;
}

boolean mark_on_rise(u8 mask)	// Save the 24 bit counter to par.buf
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
      if(~ACSR & BV(ACO))	// When AIN- goes above 1.23V, ACO goes LOW
        break;

    if(TCNT1 > TIMERSIZE)
       {
       TCNT1 = 0;
       if(++HTM > par.timeoutval)
         {
         par.buf[0] = TIMEOUT;		// Timeout error
         return FALSE;
         }
       }
    }
par.buf[par.buf_index++] = TCNT1L;
par.buf[par.buf_index++] = TCNT1H;
par.buf[par.buf_index++] = HTM;
return TRUE;
}

boolean mark_on_fall(u8 mask)	// Save counter to par.buf 
{
for(;;)
    {
    if(mask)	
       {
       if(~PINC & mask)		// Digital Input specified by mask
         break;
       }
    else			// Mask = 0 means ACMP input
      if(ACSR & BV(ACO))	// When AIN- goes below 1.23V, ACO goes HIGH
        break;
 
    if(TCNT1 > TIMERSIZE)
       {
       TCNT1 = 0;
       if(++HTM > par.timeoutval)
         {
         par.buf[0] = TIMEOUT;		// Timeout error
         return FALSE;
         }
       }
    }
par.buf[par.buf_index++] = TCNT1L;
par.buf[par.buf_index++] = TCNT1H;
par.buf[par.buf_index++] = HTM;
return TRUE;
}
//--Time measurement routines end.

/* --------------------- Software SPI routines ------------------
PA3 (CH3) - SCLK
PA2 (CH2) - MOSI
PA2 (CH1) - MISO
The direction of PA3 and PA2 are set as output in the beginning of an SPI
transaction and set back as input after finishing the transaction.

PC7 (D3out), PC6(D2out) and PC5(D1out) are used as chip selects.

There are TWO kinds of SPI slave devices, depending on the State of the
CLOCK signal during CS is taken LOW.
The chip_enable_bar, spi_pull_bar and spi_push_bar routines MUST be used
for devices expecting a HIGH on the CLOCK during entry.
*/

#define 	CSADC		0	// Digital Output D3
#define 	CSDAC		1	// Digital Output D2
#define 	CSROM		2	// Digital Output D1

#define 	SPI_CLK		0x08	// Serial Clock OUT
#define 	SPI_DOUT	0x04	// Data Out ( IN for Slave)
#define 	SPI_DIN 	0x02	// Data IN  ( OUT for Slave)

void chip_enable(u8 dev)	// PORTC D7, D6 & D5 are CS pins
{
DDRA = 0xFC;				// PA3 & PA2 as outputs
PORTC |= 0xE0;				// Make all CS bits HIGH
PORTA &= ~SPI_CLK;		  	// CLK LOW before enabling CS
PORTC &= ~(1 << (7-dev)); 		// Make the Selected CS LOW
}

void chip_enable_bar(u8 dev)	// PORTC D7, D6 & D5 are CS pins
{
DDRA = 0xFC;				// PA3 & PA2 as outputs
PORTC |= 0xE0;				// Make all CS bits HIGH
PORTA |= SPI_CLK;		  	// CLK HIGH before enabling CS
PORTC &= ~(1 << (7-dev)); 		// Make the Selected CS LOW
}

void chip_disable(void)
{
PORTC |= 0xE0;
DDRA = 0xF0;				// DDRA back to normal state
}

void spi_push(u8 val)	// Should Enter with CS = LOW and SCLK = LOW
{
u8 i = 8;			// push 8 bits

while(i)
        {
        if(val & 0x80)			// Push MSB first
		PORTA |= SPI_DOUT;	// Set DOUT if Databit is '1'
        else
		PORTA &= ~SPI_DOUT;	// else clear DOUT 
	PORTA |= SPI_CLK;		// Set CLOCK to HIGH
	PORTA |= SPI_CLK;		// wait a bit
	val <<= 1;			// make next bit the new MSB
	i--;
	PORTA &= ~SPI_CLK;		// Take Clock LOW
	}
}

u8 spi_pull(void)	// Should Enter with CS = LOW and SCLK = LOW
{
u8 dat = 0;
u8 i = 8;			// pulll 8 bits
while(i)
        {
        PORTA |= SPI_CLK;	// Take Clock HIGH. Time set using CRO
        PORTA |= SPI_CLK;	// Take Clock HIGH
       	dat = dat << 1;		// First iteration has no effect
       	if(PINA & SPI_DIN)	// Read the DATA BIT
       	  dat |= 1;
        PORTA &= ~SPI_CLK;	// Take Clock LOW
        PORTA &= ~SPI_CLK;
	--i;
	}
return dat;
}	


void spi_push_bar(u8 val)	// Should Enter with CS = LOW and SCLK = HIGH
{
u8 i = 8;			// push 8 bits
while(i)
        {
        if(val & 0x80)			// Push MSB first
		PORTA |= SPI_DOUT;	// Set DOUT if Databit is '1'
        else
		PORTA &= ~SPI_DOUT;	// else clear DOUT 
	PORTA &= ~SPI_CLK;		// Take Clock LOW, Time set with CRO
	PORTA &= ~SPI_CLK;		// Take Clock LOW
	PORTA &= ~SPI_CLK;		// Take Clock LOW
	PORTA |= SPI_CLK;		// Set CLOCK to HIGH
	PORTA |= SPI_CLK;		// Set CLOCK to HIGH
	val <<= 1;			// make next bit the new MSB
	i--;
	}
}


u8 spi_pull_bar(void)	// Should Enter with CS = LOW and SCLK = HIGH
{
u8 dat = 0;
u8 i = 8;			// pulll 8 bits
while(i)
        {
        PORTA &= ~SPI_CLK;
        PORTA &= ~SPI_CLK;
       	dat = dat << 1;		// First iteration has no effect
       	if(PINA & SPI_DIN)
       	  dat |= 1;
        PORTA |= SPI_CLK;	// Take Clock HIGH
        PORTA |= SPI_CLK;	// Take Clock HIGH
	--i;
	}
return dat;
}	
//----------------------- End of SPI routines ---------------------


//-----Serial EEPROM on SPI----
#define		WEN		6	// AT25HP512 SEEPROM commands
#define		WRDAT		2
#define		RDDAT		3
#define		RDSR		5
#define 	WRSR		1	// write SR not used ?

u8 seeprom_status(void)	// Return The Status register of AT25HP seeprom
{
u8 stat;
chip_enable(CSROM);      
spi_push(RDSR);
stat = spi_pull();		// Read from the slave 
chip_disable();
return stat;
}

void seeprom_write_enable(void)	// Write enable the chip
{
chip_enable(CSROM);
spi_push(WEN);
chip_disable();
}

void seeprom_write_block(u16 addr, u8 *data)	// writes 128 bytes of data
{
u8 tmp8;
chip_enable(CSROM);
spi_push(WRDAT);
spi_push(addr >> 8);
spi_push(addr & 255);
for(tmp8=0; tmp8 < 128; ++tmp8) spi_push(data[tmp8]);      
chip_disable();
}

u8 seeprom_read_byte(u16 addr)
{
u8 dat;
chip_enable(CSROM);
spi_push(RDDAT);
      PORTC |= 1;
      PORTC &= ~1;
spi_push(addr >> 8);
spi_push(addr & 255);

dat = spi_pull();
chip_disable();
return dat;
}

//------------------------ MAX542 SPI DAC Routines------
void hr_set_dac(void)
{
   chip_enable(CSDAC);
   spi_push(par.buf[2]);		// Push Upper byte
   spi_push(par.buf[1]);		// Push Lower byte
   chip_disable();
}


//--------------------AD7718  SPI ADC --------
#define COMREG	0
#define STATREG 0
#define MODREG  1
#define CONREG  2	
#define FILREG	3
#define DATREG  4
#define OFFREG  5
#define GAINREG 6

#define RDY		128
#define ERR		8
#define CONVERT 	2
#define NOCHOP  	128
#define CALZERO 	4
#define CALFS		5
#define EXTCALZERO 	6
#define EXTCALFS	7
#define SF4		255	// Filter value
#define UB		8	// Unipolar coding selected

u8 readID(void)
  {
  u8 st;
  chip_enable_bar(CSADC);
  spi_push_bar(64+15);
  st = spi_pull_bar();
  chip_disable();
  return st;
  }

void hr_adc_init(void)	// Initialize
{
initDisplay(); writeByte(readID());

chip_enable_bar(CSADC);
spi_push_bar(FILREG);		// Write the Filter Register
spi_push_bar(SF4);
chip_disable();
}

void hr_adc_external_cal(u8 zchan)	// External Calibration
{
        // MSB of zchan decides Zero or Full scale calibration
chip_enable_bar(CSADC);
spi_push_bar(0 + CONREG);	 		// Select channel
spi_push_bar(UB + ( (zchan & 15) << 4) + 7);	// Range = 7 (2.56V)

spi_push_bar(0 + MODREG);
if(zchan & 128) 			// If MSB of zchan is set then
  spi_push_bar(EXTCALFS);		// Full Scale calibration
else					// else
  spi_push_bar(EXTCALZERO);		// Zero Scale calibration

tmp16 = 100;
while(tmp16--)				// Wait for Zero Calibration
    {
    delay(5000);
    spi_push_bar (64 + MODREG);	//checks mode reg
    tmp8_1 = spi_pull_bar();
    if ( (tmp8_1 & 7) == 1)		// MD bits = 001 ?
        break;
    }
if (!tmp16) 				// Timeout Error
    par.buf[0] = 'T';
else
    {
    spi_push_bar(64 + OFFREG);				// OFFSET read
    for(tmp8=0; tmp8 < 3; ++tmp8)
        par.buf[par.buf_index++] = spi_pull_bar();	// get HIGH, MID & LOW
    spi_push_bar(64 + GAINREG);				// GAIN read
    for(tmp8=0; tmp8 < 3; ++tmp8)
        par.buf[par.buf_index++] = spi_pull_bar();	// get HIGH, MID & LOW
    }
chip_disable();
}


void hr_adc_internal_cal(u8 chan)	// Internal calibration of chan
{
chip_enable_bar(CSADC);
spi_push_bar(0 + CONREG);		// Select channel
spi_push_bar(UB + (chan << 4) + 7);	// Range = 7 (2.56V)

for(tmp8=CALZERO; tmp8 <= CALFS; ++tmp8)
    {
    spi_push_bar(0 + MODREG);
    spi_push_bar(tmp8);			// ZERO and FS Calibration
    tmp16 = 100;
    while(tmp16--)			// Wait until Calibration is done
        {
        delay(5000);
        spi_push_bar (64 + MODREG);	//checks mode reg
        tmp8_1 = spi_pull_bar();
        if ( (tmp8_1 & 7) == 1)		// MD bits = 001 ?
            break;
        }
    if (!tmp16) 			// Timeout Error
        par.buf[0] = 'T';
    }
if(tmp16)	// There was no timeout error
    {
    spi_push_bar(64 + OFFREG);				// OFFSET read
    for(tmp8=0; tmp8 < 3; ++tmp8)
        par.buf[par.buf_index++] = spi_pull_bar();	// get HIGH, MID & LOW
    spi_push_bar(64 + GAINREG);				// GAIN read
    for(tmp8=0; tmp8 < 3; ++tmp8)
        par.buf[par.buf_index++] = spi_pull_bar();	// get HIGH, MID & LOW
    }
chip_disable();
}

void hr_select_adc(u8 chan_range) // Select Channel & Input Voltage Range
{
chip_enable_bar(CSADC);
spi_push_bar(0 + CONREG);
spi_push_bar(UB + chan_range);	 // Caller sends both chan & range info
chip_disable();
}

void hr_adc_read()	// Data is deposited in par.buf
{
chip_enable_bar(CSADC);
spi_push_bar(MODREG);		// Write to MODE REG
spi_push_bar(CONVERT);		// Start single A/D Conversion

tmp16 = 100;
while(tmp16--)			// Wait until Conversion is done
    {
    delay(5000);
    spi_push_bar (64 + STATREG);	//checks mode reg
    tmp8 = spi_pull_bar();
    if (tmp8 & RDY)			// RDY is set ?
        break;
    }
if (!tmp16) 				// Timeout Error
        par.buf[0] = 'T';
else
    {
    par.buf[par.buf_index++] = tmp8;		// Send Status byte first
    spi_push_bar(64 + DATREG);			// Command for Data Read
    par.buf[par.buf_index++] = spi_pull_bar();	// send HIGH first
    par.buf[par.buf_index++] = spi_pull_bar();	// followed by MID
    par.buf[par.buf_index++] = spi_pull_bar();	// and LOW
    }
chip_disable();
}


void hr_get_cal(void)		// Return Gain & Offset registers 3+3bytes
{
chip_enable_bar(CSADC);
spi_push_bar(64 + OFFREG);			// Command for GAIN read
for(tmp8=0; tmp8 < 3; ++tmp8)
  par.buf[par.buf_index++] = spi_pull_bar();	// get HIGH, MID & LOW
spi_push_bar(64 + GAINREG);			// Command for GAIN read
for(tmp8=0; tmp8 < 3; ++tmp8)
  par.buf[par.buf_index++] = spi_pull_bar();	// get HIGH, MID & LOW
chip_disable();
}


//-------------------- Interrupt Service Routines----------------------

SIGNAL (SIG_OUTPUT_COMPARE0)	// TIMER0 Compare Match Interrupt
{
switch(par.irq_func)
  {
  case IN_PULSE:
    if(par.minor_ticks++ == isr_tmp16) 	// Time to toggle
      {
      par.minor_ticks = 0;

      isr_tmp8 = PORTC & 0x30;		// get D0 and D1 status
      if(isr_tmp8)
          PORTC &= 0xcf;		// clear D0 and D1
      else
        PORTC |= 0x30;			// Set D0 and D1
      }  
    break;  


  case IN_PMRB:
/*
This routine got complicated because of the 128 byte block write requied
for the SEEPROM chip AT2HP5512. The ADC sampling is done only when the
Timestamp is a multiple of the 'delay' implies that Sampling is started
just after PMRB_START command from the PC. For example if delay = 10,
sampling will start within the next 10 seconds and then repeat every
10 seconds.
The upper 256 bytes of par.buf[] is used by this routine. The 8 bit variable
pmrb_buf_pos is used for indexing. When it crosses the LOWER 128 bytes are
saved to SEEPROM and when it overflows, the UPPER 128 bytes are saved and
this process goes on until the requested number of blocks are filled.
*/  
    if(par.minor_ticks++ == 124) 	// One second elapsed
      {
      par.minor_ticks = 0;
      ++par.pctime;
      if( (par.pctime % par.pmrb_delay) == 0 )	// Time to Sample ADCs
        {
        // Convert ADC channels as per par.pmrb_chlist. Store data
        for(isr_tmp8=0; isr_tmp8 < par.pmrb_num_chan; ++isr_tmp8)
          { 
          sbi(ADCSRA, ADIF);
          ADMUX = AVREF | ((par.adc_size & 1) << 5) | par.pmrb_chlist[isr_tmp8];
          ADCSRA = BV(ADEN) | BV(ADSC) | SLOW_CONV_MASK;
          while ( !(ADCSRA & (1<<ADIF)) ) ;	// wait for ADC conversion
          if(par.adc_size == 2)			// Read ADCL for 10 bit data
            par.buf[PMRB_INDEX + par.pmrb_bufpos++] = ADCL;
          par.buf[PMRB_INDEX + par.pmrb_bufpos++] = ADCH;
          }
 
        if( (par.pmrb_bufpos & 128) && (par.filling_half == LOWER) )
          {
          seeprom_write_enable(); 
          while(seeprom_status() & 1); 
          seeprom_write_block(128 * isr_tmp16++, par.buf + PMRB_INDEX);
          par.filling_half = UPPER;	// Mark the current HALF
          }
        else
        if( !(par.pmrb_bufpos & 128) && (par.filling_half == UPPER) )
          {
          seeprom_write_enable(); 
          while(seeprom_status() & 1); 
          seeprom_write_block(128 * isr_tmp16++, par.buf+BUFSIZE - 128);
          par.filling_half = LOWER;	
          }

        if(isr_tmp16 == par.pmrb_numblocks)	// Stop acquiring data
          {
          while(seeprom_status() & 1);	// Extra Block for END Time stamp 
          seeprom_write_enable(); 
          while(seeprom_status() & 1); 
          seeprom_write_block(128 * isr_tmp16, (u8*) &par.pctime);
          par.irq_func = CLOCK;
          }
        }
      }
  break;
      
  case CLOCK:
/* 
Increments the 4 byte time stamp loaded from PC, by SETTIME,  every second.
This is how we keep a local clock so long as power is up. Time stamp
is required by PMRB functions.
*/  
    if(par.minor_ticks++ == 124) 	// One second elapsed
      {
      par.minor_ticks = 0;
      ++par.pctime;
      }
  break;
  
  case USERWAVE:	// Output to PWM DAC, whatever loaded by the user
    OCR2 = eeprom_read_byte((u8ptr)par.minor_ticks++);
    if(par.minor_ticks == TABLESIZE) par.minor_ticks = 0;
    break;

  case HRUSERWAVE:		// Same as above, but uses Plug-in Serial DAC
    chip_enable(CSDAC);
    isr_tmp8 = eeprom_read_byte( (u8ptr)par.minor_ticks++);
    spi_push(isr_tmp8);		// Push Upper byte
    spi_push(0);		// Push Lower byte
    chip_disable();
    if(par.minor_ticks == TABLESIZE) par.minor_ticks = 0;
    break;

  case IN_SMRB:
/*
SMRB_START sets the TC0 interrupt 4 times per millisecond. So (4 * adc_delay)
gives delay in milliseconds. Data is stored in a manner simlar to 
MULTIREADBLOCK.
*/  
    if(par.minor_ticks++ % (4 * par.adc_delay) )	// 250 us * 4 * adc_delay
      break;
      
    for(isr_tmp8=0; isr_tmp8 < par.num_chan; ++isr_tmp8)	// Multi-channel
      { 
      sbi(ADCSRA, ADIF);
      ADMUX =  ((par.adc_size & 1) << 5) | par.chlist[isr_tmp8];
      ADCSRA = BV(ADEN) | BV(ADSC) | SLOW_CONV_MASK;
      while ( !(ADCSRA & (1<<ADIF)) ) ;		// wait for ADC conversion
      if(par.adc_size == 2)			// Read ADCL for 10 bit data
         par.buf[isr_tmp16++] = ADCL;
      par.buf[isr_tmp16++] = ADCH;
      }
      
    if (isr_tmp16 >= (par.num_samples * par.adc_size * par.num_chan + 4) )
      {
      par.irq_func = 0;			// Job is over. Caller checks this flag
      TIMSK &= ~BV(OCIE0);		// Disable Compare0 match interrupts
      }  
    break;


  }
}


SIGNAL (SIG_COMPARATOR)			// HISTOGRAM
{
sbi(ADCSRA, ADIF);			// clear old status
ADMUX = AVREF | BV(ADLAR) | 0;			// chan 0 , left adjest
ADCSRA = BV(ADEN) | BV(ADSC) | 5;	// Low clock speed
while ( !(ADCSRA & (1<<ADIF)) ) ;	// wait for ADC conversion

++*( (u16*) par.buf + ADCH + 2);	// Increment location as 16 bit word
if(*( (u16*) par.buf + ADCH + 2) == 0xffff)
      ACSR &= ~BV(ACIE);		// Overflow. Disable interrupts
      
tmp8 = PORTC;				// Clear DRDY flag
PORTC = tmp8 & 0x7f;			// Take D4 LOW
PORTC = tmp8 | 0x80;			// and back to HIGH
}


void processCommand()
{
/* This routine takes the command and the input data from PC from 'par.buf'.
The result and output data to the PC are filled back in the same buffer.
The 'DONE' response filled initially will be over written in case of an error
in executing the command. At the 'response + output data' is to the PC.
The number of bytes returned depends on the command and arguments.
The calling Python routines are written accordingly. In general
1. Time measurement calls return 1+3 bytes
2. READBLOCK and MULTIREADBLOCK sends two bytes after the response byte 
indicating the number of data bytes following.
Using the format "par.buf[par.bufindex++] = byte"
for filling keeps track of the number of bytes filled in par.bufindex.
*/
u8 cmd = par.buf[0];		// Save the Command 
par.buf[0] = DONE;		// Fill reply Assuming Success
par.buf_index = 1;		// Filling of return Data from second byte onwards

switch(cmd)
    {
/*
The normal MULTIREADBLOCK call allows a delay is specified in microseconds.
When digitizing the maximum possible 800 samples at a delay of 3000 the total
time takes in 2.4 seconds. Waiting long for ATmega16 at PC end may create
a feeling that the program is not responding. The Interrupt driver 
SLOW MULTI READ BLOCK (SMRB) is called in a manner similar to MRB.
The delay specified is taken as in milliseconds. The call returns after setting
the ISR and the user program can collect the data later, after checking the
status using SMRB_STATUS. The SMRB_GETDATA will get the colelcted data,
formatted same as MRB. This call can be used for slowly varying waveforms.
Pendulum digitization is one example. When an SMRB is in progress, do not use
the ADC reads or 'get_frequency()' function. They will mess up SMRB.
*/
    case SMRB_START:
      if ( (par.num_samples * par.adc_size * par.num_chan) > BUFSIZE)
        {
        par.buf[0] = INVBUFSIZE;
        break;
        }
      isr_tmp16 = 4;		// First 4 bytes status + chmask + nwords; 
      par.irq_func = IN_SMRB;		// Set the function for ISR
      par.minor_ticks = 0;
      OCR0 = 249;			// Tick every 250 usecs 
      TCCR0 = BV(WGM01) | BV(CS01);	// TC0 in Wavegen mode, Clock/8, 1 usec
      TIMSK = BV(OCIE0);		// Enable Compare0 match interrupts
      break;            

    case SMRB_GETDATA:
      par.buf[1] = par.chmask | (par.adc_size << 4);	// chmask + size
      tmp16 = isr_tmp16-4;	// Number of data bytes filled so far
      par.buf[2] = tmp16 & 255;
      par.buf[3] = (tmp16 >> 8) & 255;
      par.buf_index = tmp16 + 4;	// 1 status + 1 MRB info + 2 size + data
      break;

    case SMRB_STATUS:
      if(par.irq_func == IN_SMRB)
        par.buf[par.buf_index++] = TRUE;
      else
        par.buf[par.buf_index++] = FALSE;
      tmp16 = isr_tmp16;
      par.buf[par.buf_index++] = tmp16 & 255;
      par.buf[par.buf_index++] = (tmp16 >> 8) & 255;
      break;

//---------------- Top panel SPI fine control functions. -----------------    
    case SPI_PULL:
      par.buf[par.buf_index++] = spi_pull();
      break;

    case SPI_PULL_BAR:
      tmp8 = spi_pull_bar();
      par.buf[par.buf_index++] = tmp8;
      break;

    case SPI_PUSH:		// Send one byte to SPI
      spi_push(par.buf[1]);
      break;

    case SPI_PUSH_BAR:		// Send one byte to SPI
      spi_push_bar(par.buf[1]);
      break;

    case CHIP_ENABLE:		// Enable an SPI device
      chip_enable(par.buf[1]);
      break;

    case CHIP_ENABLE_BAR:	// Enable an SPI device
      chip_enable_bar(par.buf[1]);
      break;

    case CHIP_DISABLE:		// Disable an SPI device
      chip_disable();
      break;
//----------------------------------------------------------------------
    case COPY_E2S:
    /*
    Used only for trouble shooting the SEEPROM Plugin. This will copy 128 bytes
    from the beginning of the internal EEPROM to the AT25HP512 
    Serial EEPROM plugged into the front side slot.    
    Important : This one uses isr_tmp16.
    */
      TIMSK &= ~BV(OCIE0);	// Disable Compare0 interrupts, for isr_tmp16
      isr_tmp16 = par.buf[2] << 8;	// high byte of address
      isr_tmp16 |= par.buf[1];		// low byte of address
      tmp16 = 0;
      while (tmp16 < 128)
          par.buf[par.buf_index++] = eeprom_read_byte((u8ptr)tmp16++);
      seeprom_write_enable();
      seeprom_write_block(isr_tmp16, par.buf+1); // write at the address
      par.buf_index = 1; 
      break;
      
    case GETMCUSTAT:
/*
  Used only for trouble shooting. More registers can be added as and when
  required. The get_mcustatus() in phm.py must be changed accordingly.
*/    
      par.buf[par.buf_index++] = DDRA;
      par.buf[par.buf_index++] = DDRB;
      par.buf[par.buf_index++] = DDRC;
      par.buf[par.buf_index++] = DDRD;
      break;
      
    case GETVERSION:
      memcpy_P(&par.buf[1], version,5);
      par.buf_index += 5;
      break;

    case LCD_INIT:		// Set Plugin port for LCD and clear LCD
      initDisplay();
      break;

    case LCD_PUTCHAR:		// Send one character to LCD
      writeLCD(par.buf[1]);
      break;

    case DIGOUT:
      PORTC = (par.buf[1] << 4) | 15;
      break;

    case DIGIN:
      par.buf[par.buf_index++] = PINC & 15;
      break;

    case READACOMP:
      par.buf[par.buf_index++] = (ACSR >> ACO) & 1;
      break;

    case SETDDR:
      if(par.buf[1] == 0) DDRA = par.buf[2];
      else if(par.buf[1] == 1) DDRB = par.buf[2];
      else if(par.buf[1] == 2) DDRC = par.buf[2];
      else if(par.buf[1] == 3) DDRD = par.buf[2];
      break;

    case SETPORT:
      if(par.buf[1] == 0) PORTA = par.buf[2];
      else if(par.buf[1] == 1) PORTB = par.buf[2];
      else if(par.buf[1] == 2) PORTC = par.buf[2];
      else if(par.buf[1] == 3) PORTD = par.buf[2];
      break;

    case GETPORT:
      if(par.buf[1] == 0) par.buf[par.buf_index++] = PINA;
      else if(par.buf[1] == 1) par.buf[par.buf_index++] = PINB;
      else if(par.buf[1] == 2) par.buf[par.buf_index++] = PINC;
      else if(par.buf[1] == 3) par.buf[par.buf_index++] = PIND;
      break;

      break;



//---------------------------ADC related functions-----------------------
    case SETADCSIZE:
/*
The 10 bit ADC output can be made 8 bit by the LEFT ADJUST option. This reduces
the data size from two bytes one byte. User can select this option.
*/    
        if(par.buf[1] > 2)
          {
          par.buf[0] = INVARG;
          break;
          }
        par.adc_size = par.buf[1];
        break;
        
    case SETCURCHAN:
/*
The ADC input channel to be used by the subsequent ADCREAD and READBLOCK calls.
*/    
      if(par.buf[1] <= 4)
        par.current_chan = par.buf[1];
      else
        par.buf[0] = INVARG;
      break;

    case SETNUMSAMPLES:
/*
Number of samples for BLOCKREAD and MULTIREADBLOCK calls. The upper limit
is decided by the RAM available, 800 bytes buffer for ATMEGA16
*/    
      tmp16 = par.buf[2] << 8;		// Shift High bytes
      tmp16 |= par.buf[1];		// Low bytes came first
      par.num_samples = tmp16;
      break;


    case ADCREAD:
/*
Samples the currently selected ADC input channel and does a coversion.
Using smaller clock frequency for better accuracy.
*/    
      sbi(ADCSRA, ADIF);			// clear old status
      ADMUX = AVREF | ((par.adc_size & 1) << 5) | par.current_chan;
      ADCSRA = BV(ADEN) | BV(ADSC) | SLOW_CONV_MASK;	// Low clock speed
      while ( !(ADCSRA & (1<<ADIF)) ) ;		// wait for ADC conversion
      if(par.adc_size == 2)			// Read ADCL for 10 bit data
         par.buf[par.buf_index++] = ADCL;
      par.buf[par.buf_index++] = ADCH; 
      sbi(ADCSRA, ADIF);
      break;

    case SETADCDELAY:
/*
The time interval between two digitizations in the READBLOCK calls is set here.
The ADC clock speed is set to get the highest possible conversion time that is
less than the requested interval. Slow conversions have better accuracy.
*/    
      tmp16 = par.buf[2] << 8;		// Shift High bytes
      tmp16 |= par.buf[1];		// Low bytes came first
      if( (tmp16 < 7) || (tmp16 > MAXDELAY) )
        {			// 10 to 1000 usecs between digittizations
        par.buf[0] = INVARG;
        break;
        }
      par.adc_delay = tmp16;	// One less for the OCR1A register

      if(tmp16 < 20)
        par.adc_ctmask = 1;
      else
      if(tmp16 < 40)
        par.adc_ctmask = 2;
      else
      if(tmp16 < 80)
        par.adc_ctmask = 3;
      else
      if(tmp16 < 160)
        par.adc_ctmask = 4;
      else
      if(tmp16 < 320)
        par.adc_ctmask = 5;
      else
        par.adc_ctmask = 6;	// ADCclk = (8MHz/64) = 125 KHz
      break;


    case SETACTION:
/* For certain experiments we need to start digitizing a waveform just after
changing the state of some of the DIGITAL Output sockets. Depending on the value
of the variable 'par.set', the bits are SET or CLEARED according to the
values of 'par.setmask.
*/
      par.set = par.buf[1];	// 1=> SET, 2=> CLR, 3=> +Pulse, 4=> -Pulse
      par.setmask = par.buf[2] << 4;	// The bits to be set or cleared
      break;

    case WAITACTION:
/* For digitizing a transient waveform, we wait for a LEVEL transition on one
of the DIGITAL input Sockets, before proceeding towards the digitization. 
*/
      par.wait = par.buf[1];		// 1 => rising edge, 2 => falling
      par.waitmask = par.buf[2];	// bits to wait on
      break;
 
    case ADDCHAN:			// For MRB calls
/*
The MULTIREADBLOCK call digitizes the channels as per 'par.chmask'.
par.chlist[] is made from chmask. The order in which channels are selected is 
decided by 'par.chlist'. For example, if chmask is 1001 binary, chlist becomes
chlist = {1,0,0,1}. MULTIREADBLOCK digitizes first and fourth channels.
ADDCHAN is for adding a channel to the list and DELCHAN for removing one.
par.num_chan and par.chlist[] are evaluated every time you change 'par.chmask'.
*/    
      if(par.buf[1] > 3)		// Channels from 0 to 3 only
          {
          par.buf[0] = INVARG;
          break;
          }
      par.chmask |= 1 << par.buf[1];	// Set the bit in mask
      par.num_chan = 0;
      for(tmp8 = 0; tmp8 < 4; ++tmp8)	// Re-arrange the list. Set numchan
        if( (1 << tmp8) & par.chmask)
          par.chlist[par.num_chan++] = tmp8;
      break;

    case DELCHAN:			// For MRB calls
      if(par.buf[1] > 3)		// Channels from 0 to 3 only
          {
          par.buf[0] = INVARG;
          break;
          }
      par.chmask &= ~(1 << par.buf[1]);	// Clear the bit in mask
      par.num_chan = 0;
      for(tmp8 = 0; tmp8 < 4; ++tmp8)	// Re-arrange the list. Set numchan
        if( (1 << tmp8) & par.chmask)
          par.chlist[par.num_chan++] = tmp8;
      break;

    case GETCHANMASK:			
        par.buf[par.buf_index++] = par.chmask | (par.adc_size << 4);
        break;	

    case ADCTRIGLEVELS:
/*
To get a stable display of periodic waveform, every time the digitization
should start roughly at the same position of the waveform. Two levels are
specified to allow rising and falling edge triggering. See the MULTIREADBLOCK
below to see the usage of the variables below.
*/    
      par.tr1 = par.buf[1];			// First Trigger level
      par.tr2 = par.buf[2];			// Second Trigger Level
      break;


    case READBLOCK:
    case MULTIREADBLOCK:
/*
READBLOCK digitizes ADC input 'current_chan'. Number of samples is limited to
BUFSIZE if 'adc_size' is one byte, half of it for two byte 'adc_size'.
The time interval between samples is decided by 'par.adc_delay'. 
    
MULTIREADBLOCK digitizes upto four channels as per the current chmask[],
num_samples and adc_size. Total data output should not exceed BUFSIZE.
In one byte size, upto 200 samples possible when all four channels 
are selected.

SET, CLEAR and PULSE on Digital Output Sockets and WAIT on Digital Inputs
are common to both calls.
*/    
      if (cmd == READBLOCK)	// Command is stored in cmd
        {
        ADMUX = AVREF | BV(ADLAR) | par.current_chan;	// Trigger Source
        if(par.num_samples * par.adc_size > BUFSIZE)
          {
          par.buf[0] = INVBUFSIZE;
          break;
          }
        }
      else	// This is an MRB call
        {
        ADMUX = AVREF | BV(ADLAR) | par.chlist[0];	// Trigger Source
        if ( (par.num_samples * par.adc_size * par.num_chan) > BUFSIZE)
          {
          par.buf[0] = INVBUFSIZE;
          break;
          }
        }
      // Second byte: Returns info on chmask and adc_size to the caller.  
      par.buf[par.buf_index++] = par.chmask | (par.adc_size << 4);

/*        
Operations on Digital I/O Sockets just before block reads are done here,
based on the values of par.set, par.wait, par.setmask and par.waitmask.
par.set: 1 for SET; 2 for CLR; 3 for HIGH PULSE; 4 for LOW PULSE 
*/      
      if(par.set == 1)		// Check for SET/CLR type Actions 
        PORTC |= par.setmask;	// Set the output bits as per mask
      else
      if(par.set == 2)
        {
        tmp8 = PORTC & (~par.setmask);	// Clear the output bits as per mask
        PORTC = tmp8 | 15;		// 15 maintains pullup on read lines
        }
      else
      if(par.set == 3)			// HIGH TRUE PULSE
        {
        tmp8 = PORTC;			// Set the output bit as per mask
        PORTC |= par.setmask;		// Set the output bits as per mask
        delay_us(par.pulse_width);			
        PORTC = tmp8 | 15;		// Restore the old value
        }
      else
      if(par.set == 4)			// LOW TRUE PULSE
        {
        tmp8 = PORTC;			// Clear the output bit as per mask
        PORTC = (tmp8 & ~par.setmask) | 15;	// 15 maintains pullups
        delay_us(par.pulse_width);			
        PORTC = tmp8 | 15;		// Restore the old value
        }

      if(par.wait == 1)			// Check for WAIT actions
        {
        if(!clear_on_rise(par.waitmask))  // Wait for a rising edge
          break;
        }
      else
      if(par.wait == 2)
        {
        if(!clear_on_fall(par.waitmask))  // Wait for a falling edge
          break;
        }      

      if( (par.set == 0) && (par.wait == 0) )	// No conditions, so trigger
        {
        for(tmp16 = 0; tmp16 < 2000; ++tmp16)
          {
          ADCSRA = BV(ADEN) | BV(ADSC) | par.adc_ctmask;
          while ( !(ADCSRA & (1<<ADIF)) ) ;	// wait for ADC conversion
          sbi(ADCSRA, ADIF);
          tmp8 = ADCH;				// Initial point

          ADCSRA = BV(ADEN) | BV(ADSC) | par.adc_ctmask;
          while ( !(ADCSRA & (1<<ADIF)) ) ;	// wait for ADC conversion
          sbi(ADCSRA, ADIF);
          tmp8_1 = ADCH;
          
          if(par.tr1 < par.tr2)		// Rising Edge Trigger
            {
            if( (tmp8 < tmp8_1) && (tmp8 > par.tr1) && (tmp8 < par.tr2) )
              break;	
            }
          else				// Falling Edge Trigger
          if( (tmp8 > tmp8_1) && (tmp8 < par.tr1) && (tmp8 > par.tr2) )
              break;			// Falling Edge Trigger reached
          }
        }

      // Wavegen mode, Clock/8 to TCC1. TCNT1 clears when it matches OCR1A
      TCCR1B = BV(WGM12) | BV(CS11);
      
      // Digitization starts. Code for RB and MRB are different from here.
      if(cmd == READBLOCK)	// Command is stored in cmd
        {
        ADMUX = AVREF |((par.adc_size & 1) << 5) | par.current_chan; // MUX
        OCR1A = par.adc_delay - 1; 
        TCNT1 = 0;		// Reset TCNT1 before intering loop
        for(tmp16=0; tmp16 < par.num_samples; ++tmp16)
          {
          ADCSRA = BV(ADEN) | BV(ADSC) | par.adc_ctmask;
          while ( !(ADCSRA & (1<<ADIF)) ) ;	// wait for ADC conversion
          if(par.adc_size == 2)			// Read ADCL for 10 bit data
             par.buf[par.buf_index++] = ADCL;
          par.buf[par.buf_index++] = ADCH;
          sbi(ADCSRA, ADIF);		// reset ADC flag
          while(TCNT1 > 2) ;		// Wait until CTC clears TCNT1
          }
        ADCSRA = BV(ADEN);			// Leave ADC enabled	
        TCCR1B = BV(CS11);			// T/C to Normal mode, Clock/8 
        break;
        }
        
      // MULTIREADBLOCK Code starts here
      if(par.adc_ctmask < 2) 	// ADC conversion time mask
        ADCSRA = BV(ADEN) | par.adc_ctmask;
      else
        ADCSRA = BV(ADEN) | 2;
      tmp8 = (par.adc_size & 1) << 5;	// ADLAR  BIT
      ADMUX = AVREF | tmp8 | par.chlist[0]; 
      OCR1A = par.num_chan * par.adc_delay - 1; 
      tmp16 = 0;
      TCNT1 = 0;		// Reset TCNT1 before intering loop
      while(tmp16 < par.num_samples)
        {
        tmp8_1 = 0;
        while(tmp8_1 < par.num_chan)
          {
          ADCSRA |= BV(ADSC);		// Start Conversion
          ++tmp8_1;
          if(tmp8_1 < par.num_chan)
            ADMUX = AVREF | tmp8 | par.chlist[tmp8_1]; 	// Next
          else
            ADMUX = AVREF | tmp8 | par.chlist[0]; 	// First in list
          while ( !(ADCSRA & (1<<ADIF)) ) ;	// wait for ADC conversion
          if(par.adc_size == 2)			// Read ADCL for 10 bit data
             par.buf[par.buf_index++] = ADCL;
          par.buf[par.buf_index++] = ADCH;
          sbi(ADCSRA, ADIF);			// reset ADC flag
          }
        ++tmp16;
        while(TCNT1 > 2) isr_tmp16 = TCNT1;	// Wait until CTC clears TCNT1
        }
      ADCSRA = BV(ADEN);			// Leave ADC enabled	
      TCCR1B = BV(CS11);			// T/C to Normal mode, Clock/8 
      break;


    case AINPERIOD:
/*
Connect the specified ADC input channel internally to the Analog Comparator
and measure the time interval between two consecutive rising edges.
*/
      ADCSRA = 0;
      ADMUX = AVREF | (par.buf[1] & 3);	// only four channels to look for
      SFIOR |= BV(ACME);
          
      tmp16 = 0;
      tmp8_1 = par.buf[1] & 15;		// 4 LSBs 
      TCNT1 =0;
      HTM = 0;
      if(!wait_for_low(0)) break;	// Make sure the level is LOW
      if(!clear_on_rise(0))break;	// Clear counter on rising edge src pin 
      if(!wait_for_low(0)) break;
      mark_on_rise(0);			// Store counters at rising edge
      break;
      
/*---------------------------------------------------------------------------
 Time interval measurement functions using DIGITAL I/O and ACOMP Sockets.
The 16 bit Timer/Counter is used for time measurements. A 1 MHz clock is fed
to the counter and the variable HTM is incremented after when it reaches 50000.
Timeout is provided on all time measurements.

Measures the time interval between a Rising edge on one Input to the Falling edge
on another. The 8 bit input data specifies the Input Sockets to wait for.
The lower 4 bits contain the Sockets to look for the First Transition.
For example par.buf[1] = 00100001, time between a rising edge on D0 to a falling
edge on D1 is measured. In fact it is possible to wait for more than one sockets
at the same time and which ever come first can be taken. At the moment the
Python function sets only a single bit in each half.
A special case arise when all the 4 bits are zero. In that case transition on
the Analog Comparator input Socket is waited for.
For R2R, R2F,F2R and F2F type calls both Start and Stop could same or different.
*/    
    case R2RTIME:
      tmp8_1 = par.buf[1];		// 4 LSBs source pins -4 MSBs end pins
      if(clear_on_fall(tmp8_1 & 15))	// Just make sure the level is LOW
        if(clear_on_rise(tmp8_1 & 15))	// Clear counter on rising edge src pin 
          if(wait_for_low(tmp8_1 & 15))	// Wait for it to go LOW
            mark_on_rise(tmp8_1 >> 4);	// Store counters at rising edge dst pin
      break;

    case R2FTIME:
      tmp8_1 = par.buf[1];		// 4 LSBs source pins -4 MSBs end pins
      if(clear_on_fall(tmp8_1 & 15))	// Just make sure the level is LOW
        if(clear_on_rise(tmp8_1 & 15))	// Clear counter on rising edge src pin 
          mark_on_fall(tmp8_1 >> 4);	// Store counters at falling edge dst pin
      break;

      if(!wait_for_low(0)) break;	// Make sure the level is LOW

    case F2RTIME:
      tmp8_1 = par.buf[1];	// 4 LSBs source pins --4 MSBs end pins
      if(clear_on_rise(tmp8_1 & 15))	//Just make sure the level is HIGH
        if(clear_on_fall(tmp8_1 & 15))	//Clear counter on falling of src pin 
          mark_on_rise(tmp8_1 >> 4);	// Store counters at rising of dst pin
    break;

    case F2FTIME:
      tmp8_1 = par.buf[1];		// 4 LSBs source pins -4 MSBs end pins
      if(clear_on_rise(tmp8_1 & 15))	// Just make sure the level is LOW
        if(clear_on_fall(tmp8_1 & 15))	// Clear counter on rising edge src pin 
          if(wait_for_high(tmp8_1 & 15))// Wait for it to go HIGH
            mark_on_fall(tmp8_1 >> 4);	// Store counters at falling edge dst pin
      break;

    case MULTIR2R:			// Multiple cycles on the same pin
/*
Measures the time interval between two rising edges on the same Input Socket.
The 4 LSBs of the first argument specifies the Input Socket to look for.
The second argument specifies the number of rising edges to be skipped in between
the two edges measured. For example par.buf[2] = 9 returns the time taken
for 10 cycles. Averaging is useful for  better measurement accuracy.
*/    
      tmp16 = 0;
      tmp8_1 = par.buf[1] & 15;		// 4 LSBs 
      TCNT1 =0;
      HTM = 0;
      if(!wait_for_low(tmp8_1)) break;	// Make sure the level is LOW
      if(!clear_on_rise(tmp8_1))break;	// Clear counter on rising edge src pin 
      if(!wait_for_low(tmp8_1)) break;
      
      while (par.buf[2]--)
        {
        if(!wait_for_high(tmp8_1))break;
        if(!wait_for_low(tmp8_1)) break;
        }

      if(par.buf[0] == TIMEOUT) break;
  
      mark_on_rise(tmp8_1);		// Store counters at rising edge
      break;

    case TPEND:				// Pendulum T using light barrier
/*
This is no more required. multi_r2r() with skip = 1 does the job.
This function was written to take care of the noise in light barrier output.
*/    
      tmp16 = 0;
      tmp8_1 = par.buf[1] & 15;		// 4 LSBs 
      TCNT1 =0;
      HTM = 0;
      if(!wait_for_low(tmp8_1)) break;	// Make sure the level is LOW
      d100us(1);
      if(!clear_on_rise(tmp8_1))break;	// Clear counter on rising edge src pin 
      d100us(1);
      if(!wait_for_low(tmp8_1)) break;
      d100us(1);
      if(!wait_for_high(tmp8_1))break;
      d100us(1);
      if(!wait_for_low(tmp8_1)) break;
      d100us(1);
      mark_on_rise(tmp8_1);	// Store counters at rising edge
      break;

    case SET2RTIME:	// Argument: 4 LSBs Source pins --4 MSBs end pins
/*
Sets the DIGITAL Output Sockets as per the 4 MSBs of the argument and measures 
the time from that to a rising edge on the Input Socket specified by the 4 LSBs 
of the argument. SET2F, CLR2R and CLR2F are similar functions.
*/    
      PORTC |= par.buf[1] << 4;
      HTM = 0;
      TCNT1 = 0;
      mark_on_rise(par.buf[1] >> 4);	// Store counters at rising of read pin
    break;

    case SET2FTIME:	// Argument: 4 LSBs source pins --4 MSBs end pins
      PORTC |= par.buf[1]<<4;
      HTM = 0;
      TCNT1 = 0;
      mark_on_fall(par.buf[1] >> 4);	// Store counters at falling of dst pin
    break;

    case CLR2RTIME:		// 4 LSBs source pins --4 MSBs end pins
      tmp8_1 = (par.buf[1] << 4) & 0xf0;// 4 LSBs are source, shift them
      PORTC &= ~tmp8_1;			// Clear the source bit
      HTM = 0;
      TCNT1 = 0;
      mark_on_rise(par.buf[1] >> 4);	// Store counters at rising of dst pin
    break;

    case CLR2FTIME:
      tmp8_1 = (par.buf[1] << 4) & 0xf0;// 4 LSBs are source, shift them
      PORTC &= ~tmp8_1;			// Clear the source bit
      HTM = 0;
      TCNT1 = 0;
      mark_on_fall(par.buf[1] >> 4);	// Store counters at falling of dst pin
    break;


    case SETPULSEWIDTH:			// For the  PULSE2*TIME functions
/*
The width of the pulse generated by the PULSE2RTIME and PULSE2FTIME calls
are set here. Used by SETACTION pulse before BLOCK READ also.
*/    
      par.pulse_width = par.buf[1];
      break;

    case SETPULSEPOL:			// For the PULSE2* functions
/*
Polarity of '0' means the pulse will go from LOW to HIGH and come back to LOW
after 'pulse_width' microseconds. The Digital Output must be made LOW before
making this call, otherwise you will get a STEP only.
Polarity '1' implies a HIGH to LOW and going back to HIGH. Digital output
must be set to HIGH before calling it.
*/    
      par.pulse_pol = par.buf[1];
      break;

    case PULSE2RTIME:	// Lower nibble output, upper inputs
/*
Sends a Pulse on the specified, by 4 LSBs, Digital Output Socket and waits for 
a rising edge on the Input Sockets specified by 4 MSBs of the argument.
Time taken in microseconds is returned.
*/    
      tmp8_1 = (par.buf[1]<<4) & 0xf0;	// get the output pins mask		
      if(!par.pulse_pol)		// HIGH TRUE pulse
        {
        PORTC |= tmp8_1;		// Set source bit
        delay_us(par.pulse_width);			
        PORTC &= ~tmp8_1;		// Restore old value
        }
      else				// LOW TRUE pulse
        {
        PORTC &= ~tmp8_1;		// Clear source bit
        delay_us(par.pulse_width);			
        PORTC |= tmp8_1;		// Restore old value
        }     
      delay_us(PULSEDEADTIME);		// To avoid false trigger
      HTM = 0;
      TCNT1 = PULSEDEADTIME;		// add that up in the result
                                        
      mark_on_rise(par.buf[1] >> 4);	// Store counters at rising of dst pin
    break;

    case PULSE2FTIME:		// Argument: 4LSB write pins  - 4MSB read pins
      tmp8_1 = (par.buf[1]<<4) & 0xf0;	// get the output pins mask		
      if(!par.pulse_pol)		// HIGH TRUE pulse
        {
        PORTC |= tmp8_1;		// Set source bit
        delay_us(par.pulse_width);			
        PORTC &= ~tmp8_1;		// Restore old value
        }
      else				// LOW TRUE pulse
        {
        PORTC &= ~tmp8_1;		// Clear source bit
        delay_us(par.pulse_width);			
        PORTC |= tmp8_1;		// Restore old value
        }     
      delay_us(PULSEDEADTIME);		// To avoid false trigger
      HTM = 0;
      TCNT1 = PULSEDEADTIME;		// add that up in the result
      mark_on_fall(par.buf[1] >> 4);	// Store counters at falling of dst pin
    break;


    case SETCOUNTER2:
/*
Sets the Timer/Counter 2 using the two arguments send by caller. A Square wave
output is generated on the PWG output socket.
*/    
      if(par.buf[1] <= 7)
        {
        TCCR2 = BV(WGM21) | BV(COM20) | par.buf[1];	// CTC mode
        OCR2 = par.buf[2];
        TCNT2 = 0;
        }
      else
        par.buf[0] = INVARG;
      break;

    case SETDAC:			// Set the PWM DAC
/* The PWG output is filtered by an RC network (R = 10K, c = 0.1 uF) and
connected to the DAC Socket. This feature is not avilable along with
the SETCOUNTER2 feature since they use the same PWG output.
*/    
      OCR2 = par.buf[1];
      TCCR2 = BV(WGM21) | BV(WGM20) | BV(COM21) | BV(CS20); // Fast PWM mode
      TCNT2 = 0;
      break;

    case COUNT:
/*
This function returns the number of pulses received on the Clock Input
of the 8 bit Timer/Counter0 in one second. Calling this function will
disturb the operation of functions using the Timer Interrupt features.
For example SETTIME, GETTIME functions use Timer0 interrupts to
maintain a clock.
*/    
      cli();
      tmp8_1 = TCCR0;			// Save TCCR0
      TCCR0 = 0;
      tmp16 = 0;
      tmp8 = 0;
      TIFR |= BV(TOV0);			// Clear TCC0 OVF flag
      TCNT0 = 0;			// counts external input
      TCNT1 = 0;			// to keep time with clk/8
      TCCR0 = 7;			// TC0 counts External  clock

      while(1)
        {
        if(TCNT1 >= TIMERSIZE)		// 50000 usecs elapsed
          {
          TCNT1 = 0;			// Reset it
          if (++tmp8 == 20)
            {
            TCCR0 = 0;			// Stop counting
            break;
            }
          }
          
        if(TIFR & BV(TOV0))		// TC0 overflow after 255 counts
          {
          ++tmp16;
          TIFR |= BV(TOV0);		// Clear OVF flag
          }
        }
      par.buf[par.buf_index++] = TCNT0;
      par.buf[par.buf_index++] = tmp16 & 255;
      par.buf[par.buf_index++] = tmp16 >> 8;
      TCCR0 = tmp8_1;			// Restore TCCR0
      ++par.pctime;			// Compensate the second we took
      sei();
      break;


/*------------------------------------------------------------------------ 
Radiation Detection System Plug-in card routines for processing input signals
coming at random intervals. The Radiation Detection Plugin circuit takes 
ACOMP input LOW when a pulse comes. The stretched pulse is fed to ADC ch0. 
The ACOMP interrupt routine digitizes the data and makes a 256 channel 
histogram with 16 bit per channel. The interrupts are automatically disabled 
if any of the channels reach 65535. A LOW TRUE pulse is send on D4 to clear 
the Plug-in card's Data Ready signal.
*/    
    case STARTHIST:
      ACSR = BV(ACIS1) | BV(ACIS0);	// AIN+ = 1.23V, F.edge interrupt
      ACSR |= BV(ACBG) | BV(ACIE);	// AIN+ = 1.23V, F.edge interrupt
      tmp8 = PORTC;			// LOW TRUE Pulse on output D3
      PORTC = tmp8 & 0x7f;		// to clear any pending DRDY flag
      PORTC = tmp8 | 0x80;
      break;

    case READHIST:
      par.buf_index = 514;		// 1 status + 1 pad + 512 bytes data
      break;

    case CLEARHIST:
      for(tmp16 = 1; tmp16 < 515; ++tmp16)	// Clear the buffer
        par.buf[tmp16] = 0;
      break;

    case STOPHIST:
      ACSR &= ~BV(ACIE);		// disable AC interrupt
      break;

/*------------------------------------------------------------------------ 
Functions below are based on the TC0 interrupt. They setup TC0 registers
and other required variables and return. The work is carried out later by 
the interrup service routine "SIGNAL (SIG_OUTPUT_COMPARE0)".
PC collects the results later using appropriate function calls.
*/

    case SETTIME:	
/*
Initialize the 32 bit integer 'pctime' to the Timestamp send from the PC. 
The ISR is set to run after every 8 milliseconds and it increments 'pctime' once
in a second. GETTIME returns the current value of 'pctime' to the PC.
*/
      par.irq_func = CLOCK;		// maintain a local clock
      par.pctime = par.buf[4];
      par.pctime = (par.pctime << 8) | par.buf[3];
      par.pctime = (par.pctime << 8) | par.buf[2];
      par.pctime = (par.pctime << 8) | par.buf[1];
      par.minor_ticks = 0;
                      
      TCCR0 = BV(WGM01) | BV(CS02);	// Wavegen mode, Clock/256 to TCC0
      sbi(TIFR,OCF0);			// Clear pending int. flag, if any
      OCR0 =  249;			// Interrupt every 32*250=8000 usec
      TCNT0 = 0;			// ADC starts here OCR1B = TCNT1
      TIMSK = BV(OCIE0);		// Enable Compare A match interrupts

      break;

    case GETTIME:
      par.buf[par.buf_index++] = par.pctime & 255;
      par.buf[par.buf_index++] = (par.pctime >> 8) & 255;
      par.buf[par.buf_index++] = (par.pctime >> 16) & 255;
      par.buf[par.buf_index++] = (par.pctime >> 24) & 255;
      break;

    case SETWAVEFORM:
/*
Configures TC0 interrupt to run in multiples of 32 microseconds. The DAC output
is set by the ISR. The sinewave table is part of the code. Ramp and Triagular 
waves are generated by calculations. Generates waves from 0.5 Hz to 125 Hz.
The wave forms are not of great quality since we do not have a proper DAC,
we use the PWM DAC
*/    
      par.irq_func = par.buf[2];		// Set the type of wave
      if(par.irq_func == HRUSERWAVE)		// Use plug-in DAC	
        {
//        SDACP_DIR |= SDACP_DMASK;		// Set direction for SDAC
//        DDRA = PA_SPIMASK;	      		// and SPI communication
        }
      else
        TCCR2 = BV(WGM21) | BV(WGM20) | BV(COM21) | BV(CS20); // use PWM DAC

      par.minor_ticks = 0;		// Used by ISR
      isr_tmp16 = 0;			// Used by TRI and RAMP
      OCR0 = par.buf[1];		// Tick every 32 * par.buf[1] usecs 
      TCCR0 = BV(WGM01) | BV(CS02);	// TC0 in Wavegen mode, Clock/256, 32 usec
      TIMSK = BV(OCIE0);		// Enable Compare0 match interrupts
      break;            

    case STOPWAVE:
      par.irq_func = 0;			// Mark that we are through
      TIMSK &= ~BV(OCIE0);		// Disable Compare0 match interrupts
      break;
      
    case PULSE_D0D1:
      par.irq_func = IN_PULSE;		// Mark where we are
      par.minor_ticks = 0;		// use this as a counter
      isr_tmp16 = par.buf[2] << 8;	// Toggle D0 and D1 when
      isr_tmp16 |= par.buf[1];		// minor_ticks reaches isr_tmp16
      OCR0 = 0;				// Tick every 32 usecs 
      TCCR0 = BV(WGM01) | BV(CS02);	// TC0 in Wavegen mode, Clock/256, 32 usec
      TIMSK = BV(OCIE0);		// Enable Compare0 match interrupts
      break;            


//------Functions using the Serial EEPROM Plug-in Module------------------

    case PMRB_START:
/*
PROM MULTI READ BLOCK, PMRB, is meant for converting Phoenix-M into a multi-
channel data logger. It requires the SEEPROM plug-in module. PMRB_START 
is called with the number of Samples and the delay between digitizations.
SETTIME must be called before calling PMRB.
The adc_size and active channel information should be set earlier.
For its operations PMRB uses the last 256 bytes of the 800 byte buffer.
It is possible to use BLOCKREADS during PMRB in progress but a digitization
but there is a small probability of PMRB interrupt striking in between and
corrupting the BLOCKREAD in progress.
The data stored to EEPROM has 10 + 4 byte header:
0,1 : number of 128 byte blocks going to be filled  (maximum 510 for 64K PROM)
2,3 : Delay in seconds between samples
4,5 : Number of samples (Maximum 8000 for 2 byte, 4 channels)
6   : adc_size
7   : Number of active channels
8   : channel mask
9   : pad byte
10 to 13 : 4 byte absolute timestamp (Epoch loaded from the PC by SETTIME)
After that the data is filled continuously. The ISR will stop only after
digitizing few more points than specified Number of Samples, to fill the
last 128 byte block.
After that it adds an extra 128 byte block that contains only the final
time stamp. The integrity of data can be checked from the two time stamps
and the expected duration (num_samples * delay)
The python routine smrb_getdata() formats the SEEPROM data properly.
After giving a PMRB_START command, a battery powered Phoenix-M can be detached
from the serial port and taken anywhere to record data.
*/
      if(par.irq_func != CLOCK)
        {
        par.buf[0] = NOCLOCK;
        break;
        }

      par.irq_func = IN_PMRB;		// Set the function for ISR
      par.pmrb_numblocks = par.buf[2];	// Number of samples
      par.pmrb_numblocks = (par.pmrb_numblocks << 8) | par.buf[1];
      par.pmrb_delay = par.buf[4];	// Delay between samples
      par.pmrb_delay |= (par.pmrb_delay << 8) | par.buf[3];
      for(tmp8 = 0; tmp8 < 4; ++tmp8)	// Copy the current channel list
        par.pmrb_chlist[tmp8] = par.chlist[tmp8];
      par.pmrb_num_chan = par.num_chan;	// and number of active channels

      isr_tmp16 = 0;		// Point to EEPROM first block,128 bytes
      par.pmrb_bufpos = 0;	// position on th 2 x 128 bytes buffer
      par.filling_half = LOWER;	// Start with lower block
      
      // Add the 10 bytes header with sampling details + 4 byte timestamp
      par.buf[PMRB_INDEX + par.pmrb_bufpos++] = par.buf[1]; 	// numblocks
      par.buf[PMRB_INDEX + par.pmrb_bufpos++] = par.buf[2];
      par.buf[PMRB_INDEX + par.pmrb_bufpos++] = par.buf[3];	// delay
      par.buf[PMRB_INDEX + par.pmrb_bufpos++] = par.buf[4];
      par.buf[PMRB_INDEX + par.pmrb_bufpos++] = par.num_samples & 255;
      par.buf[PMRB_INDEX + par.pmrb_bufpos++] = par.num_samples >> 8;
      par.buf[PMRB_INDEX + par.pmrb_bufpos++] = par.adc_size;	// data size
      par.buf[PMRB_INDEX + par.pmrb_bufpos++] = par.pmrb_num_chan;	// nchan
      par.buf[PMRB_INDEX + par.pmrb_bufpos++] = par.chmask;	// chmask
      par.buf[PMRB_INDEX + par.pmrb_bufpos++] = 0;		// pad byte
      par.buf[PMRB_INDEX + par.pmrb_bufpos++] = par.pctime & 255;
      par.buf[PMRB_INDEX + par.pmrb_bufpos++] = (par.pctime >> 8) & 255;
      par.buf[PMRB_INDEX + par.pmrb_bufpos++] = (par.pctime >> 16) & 255;
      par.buf[PMRB_INDEX + par.pmrb_bufpos++] = (par.pctime >> 24) & 255;

      ADCSRA = BV(ADEN);	// Enable ADC
      break;            

    case PMRB_RUNNING:
      if(par.irq_func == IN_PMRB)
        par.buf[par.buf_index++] = TRUE;
      else
        par.buf[par.buf_index++] = FALSE;
      break;

    case READSEEPROM:
      tmp16 = par.buf[2] << 8;	// SEEPROM address to read
      tmp16 |= par.buf[1];	// combine low and high bytes
      tmp8 = par.buf[3];	// Number of bytes to read
      while (tmp8--)
        {
        while(seeprom_status() & 1);		// Wait until chip is ready
        par.buf[par.buf_index++] = seeprom_read_byte(tmp16++);
        }
      break;

/* -----------------------------------------------------------------------
High resolution AD/DA plug-in modules. Currently 16 bit.
*/

    case HR_ADCINIT:
      hr_adc_init();
      break;

    case HR_SETCHAN:
      hr_select_adc(par.buf[1]);
      break;

    case HR_CALINT:
      hr_adc_internal_cal(par.buf[1]);
      break;

    case HR_CALEXT:
      hr_adc_external_cal(par.buf[1]);
      break;

    case HRADCREAD:
      hr_adc_read();
      break;

    case HRSETDAC:
      hr_set_dac();
      break;


//--------------------------------------------------------------------
    case PULSEOUT:
/*
http://www.andrew.cmu.edu/user/ebuehl/robosapien-lirc/ir_codes.htm
*/
        TCNT2 = 0;
        OCR2 = 101;				// 39.2 KHz when clock_sel = 1
        TCCR2 = BV(WGM21) | BV(COM20) | 1;  	// Pulsing for Start marker
        delay_us(8 * 833);
        TCCR2 = BV(WGM21) | BV(COM20);  	// Stop
        tmp8_1 = par.buf[1];
        tmp8 = 8;
        while(tmp8--)
          {
          if(tmp8_1 & 128)			// MSB of data
            delay_us(3332);			// HIGH (no pulse) duration
          else
            delay_us(833);			// HIGH (no pulse) duration
          TCCR2 = BV(WGM21) | BV(COM20) | 1;  	// start Pulsing
          delay_us(833);
          TCCR2 = BV(WGM21) | BV(COM20);  	// Stop Pulsing
          tmp8_1 <<= 1;
          }
      break;

    case TABLEDATA:
      tmp16 = par.buf[2] << 8;	// 16 bit Internal SEEPROM address by
      tmp16 |= par.buf[1];	// combining low and high bytes
      eeprom_write_byte ( (u8ptr)tmp16, par.buf[3]);
      break;


    default:
      par.buf[0] = INVCMD;		// Invalid Command
      break;
    }

//initDisplay(); writeLCD(par.buf[0]); write16(par.buf_index); // for debug only

for(tmp16=0; tmp16 < par.buf_index; ++tmp16)
    {
    loop_until_bit_is_set (UCSRA, UDRE);
    if (UCSRA & (1<<RXC))
      {
      writeLCD('X');
      write16(UDR);		// look for XOFF ????
      }
    UDR = par.buf[tmp16];
    }
}
  //------------------- End of processCommand function-------------------


int
main (void)
{
  delay(30000);
  initialize();
  initDisplay(); write16(BUFSIZE);

  par.buf_index = 0;
  for(;;)
    {
    while ( !(UCSRA & (1<<RXC)) ) ;		// wait for receiver data
    par.buf[par.buf_index++] = UDR;		// Put the byte in the buffer. Error TODO 

    if(par.buf_index*GROUPSIZE > par.buf[0])	// Process after required no. of arguments
      {
      processCommand();
      par.buf_index = 0;
      }
    }
}
