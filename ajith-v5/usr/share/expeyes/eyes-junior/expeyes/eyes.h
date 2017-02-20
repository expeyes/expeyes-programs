#define FALSE 0
#define TRUE 1

typedef unsigned char byte;

// commands without any arguments (1 to 40)
#define GETVERSION	1	// Get the Eyes firmware version
#define DIGIN		2	// Digital Input (4 bits)

// Reply from ATmega8 to the PC
#define DONE		'D'	// Command executed successfully
#define	INVCMD		'C'	// Invalid Command
#define INVARG		'A'	// Invalid input data
#define INVBUFSIZE	'B'	// Resulting data exceeds buffersize
#define TIMEOUT		'T'	// Time measurement timed out
#define RS232ERR	'R'	// RS232  read error

int open_phm(void);		// Opens Phoenix on RS232
void close_phm(void);	// Close RS232 connection
char swrite(byte data);	// write one byte to serial port, returns -1 on error
char sread(byte* data);	// read one byte .returns -1 on error.

