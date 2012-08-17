#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <termios.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "eyes.h"


/*
Functions 'swrite' and 'sread' does single character Output & Input to the
Serial port using the file handle 'fd'. Routines need to rewritten
for porting to a different platform are open_eyes(), close_eyes(), swrite()
and sread().
*/

#define BAUDRATE B38400
#define DEVICE 	"/dev/ttyACM0"
#define _POSIX_SOURCE 1				// POSIX compliant source
#define MAXWAIT	30					// 30 deciseconds (3 seconds)

struct 	termios oldtio, newtio;

int	fd;
byte	ss[10];		// temporary buffer used for rs232 read/write
byte	tmpb;


char swrite(byte data)	// Function returns -1 on error
{
if(write(fd, &data, 1) != 1)
  return -1;
return 0;
}

char sread(byte* data)	// returns -1 on error. Result returned in 'data'
{
*data = RS232ERR;
if(read(fd, data, 1) != 1)
  return -1;
return 0;
}

byte read_bytes(int nb, byte* data)	// returns -1 on error. Result returned in 'data'
{
if(read(fd, data, nb) != nb)
  return RS232ERR;
return 0;
}

int open_eyes(void)
{
  int k;
  fd = open (DEVICE, O_RDWR | O_NOCTTY);
  if (fd < 0)
	{
	fprintf(stderr,"ERROR opening %s\n",DEVICE); 
    return -1;
	}

  tcgetattr (fd, &oldtio);	/* save current port settings */
  memset (&newtio, 0, sizeof (newtio));
  newtio.c_cflag = BAUDRATE | CS8 | CLOCAL | CREAD | PARENB;
  newtio.c_iflag = INPCK;
  newtio.c_oflag = 0;
  newtio.c_lflag = 0;		// non-canonical mode
  newtio.c_cc[VTIME] = MAXWAIT;	// Timeout for read in deciseconds
  newtio.c_cc[VMIN] = 0;	// read will return after VTIME for sure
  tcflush (fd, TCIOFLUSH);
  tcsetattr (fd, TCSANOW, &newtio);

  return 0;
}

void close_eyes(void)
{
  tcflush (fd, TCIOFLUSH);
  tcsetattr (fd, TCSANOW, &oldtio);
}

main()
{
int k;
byte   ss[100];
open_eyes();
swrite(1);
read_bytes(1,ss);
read_bytes(5,ss);
for(k=0; k <7; ++k)
	{
	printf("%c", ss[k]);
	}
printf("\n");

close_eyes();
}

