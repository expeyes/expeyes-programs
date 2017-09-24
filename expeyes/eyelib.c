#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <termios.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "eyelib.h"


#define GNULINUX
//#define WINDOWS


#define VERSION  "ey1.0"			// Version number, we check only first 2 bytes
#define BAUDRATE B38400
#define _POSIX_SOURCE 1				// POSIX compliant source
#define MAXWAIT	30					// 30 deciseconds (3 seconds)

struct 	termios oldtio, newtio;
int	fd;						// File handle, global variable


char swrite(char data)		// Writes a single character. Function returns -1 on error
{
if(write(fd, &data, 1) != 1)
  return -1;
return 0;
}


byte read_bytes(int nb, char* data)	// Returns o or RS232ERR. Result returned in 'data'
{
if(read(fd, data, nb) != nb)
	{
	printf("Read ERR %x\n",fd);
	return RS232ERR;
	}
return 0;
}

int search_eyes(char *device)			// Returns handle on success, else -1
{
  char ss[10];
  fd = open (device, O_RDWR | O_NOCTTY);
  if (fd < 0)
	{
	fprintf(stderr,"ERROR opening %s\n",device); 
    return -1;
	}

  printf("Opened Device %s\n", device);
  tcgetattr (fd, &oldtio);	/* save current port settings */
  memset (&newtio, 0, sizeof (newtio));
  newtio.c_cflag = BAUDRATE | CS8 | CLOCAL | CREAD | PARENB;
  newtio.c_iflag = INPCK;
  newtio.c_oflag = 0;
  newtio.c_lflag = 0;				// non-canonical mode
  newtio.c_cc[VTIME] = MAXWAIT;		// Timeout for read in deciseconds
  newtio.c_cc[VMIN] = 0;			// read will return after VTIME for sure
  tcflush (fd, TCIOFLUSH);
  tcsetattr (fd, TCSANOW, &newtio);

  swrite(GETVERSION);
  read_bytes(1,ss);
  if(*ss == 'D')					// Found Something like Phoenix or expEYES
	{
    read_bytes(5,ss);
    if(!strncmp(ss,"ey",2))			// found proper version of hardware
		{
		ss[6] = '\0';
		fprintf(stderr,"Found EYES Version : %s\n",ss);
		return fd;
		}
	}
  else
	{
	fprintf(stderr,"Response = %c\n",ss[0]);
	}
  tcflush (fd, TCIOFLUSH);			// Not EYES on this port, rcover settings
  tcsetattr (fd, TCSANOW, &oldtio);
  return -1;
}

void close_eyes(void)
{
  tcflush (fd, TCIOFLUSH);
  tcsetattr (fd, TCSANOW, &oldtio);
}

int open_eyes(void)
{
int k, fd;
#ifdef GNULINUX
#define MAXPORT		4
char *devlist[MAXPORT] = {"/dev/ttyUSB0","/dev/ttyUSB1","/dev/ttyACM0","/dev/ttyACM1",};
for(k= 0; k < MAXPORT; ++k)
	{
	fd = search_eyes(devlist[k]);
	if(fd > 0)
		return fd;
	}
#endif

#ifdef WINDOWS
#define MAXPORT		255
for(k= 0; k < MAXPORT; ++k)		// to be tested
	{
	char ss[10];
	sprintf(ss,"COM%d",k);
	fd = search_eyes(ss);
	if(fd > 0)
		return fd;
	}
#endif


return -1;		
}


int main()
{
char s[10];
char c;
int k;

fd = open_eyes();
if(fd < 0)
	{
	fprintf(stderr,"EYES Open Failed");
	exit(0);
	}

for(k=0; k < 256; ++k)
	{
	c = k & 255;
	swrite('A');
	read_bytes(1, s);
	printf("res = %c\n",s[0]);
	}

close_eyes();
return 0;
}

