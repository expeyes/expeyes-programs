#define FALSE 0
#define TRUE 1

typedef unsigned char byte;

// commands without any arguments (1 to 40)
#define GETVERSION	1	// Get the Eyes firmware version
#define DIGIN		2	// Digital Input (4 bits)

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
#define RS232ERR	'R'	// RS232  read error

int open_phm(void);		// Opens Phoenix on RS232
void close_phm(void);	// Close RS232 connection
char swrite(char data);	// write one byte to serial port, returns -1 on error
char sread(char* data);	// read one byte .returns -1 on error.

