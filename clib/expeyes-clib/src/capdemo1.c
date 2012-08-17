/* 
Test program demonstrating Analog I/O functions. Connect SINE to A1 before running the code. 
Compile & run using
$ gcc -Wall -o capdemo capdemo.c -lm
$ ./capdemo > log.dat
$ xmgrace log.dat
*/

#include "ejlib.h" 
/* extern */ int fd;

void err(char* s)
{
fprintf(stderr,"Error: %s\n",s);
exit(0);
}

int main()
{
float fr, tvbuf[MAXBUF*2];		// Array to store Time & Voltage data from capture.
int	ns, tg, k;

fd = open_eyesj();
if(fd < 0)
	{
	fprintf(stderr,"EYES Open Failed\n");
	exit(0);
	}

set_sqr1(100.0, &fr);		// Sets 100Hz on SQR1
ns = 1800;
tg = 100;

// Capture single channel, 8 bit resolution
if(capture(1, ns, tg, tvbuf))err("capture");
for(k=0; k < ns; ++k) printf("%f  %f\n", tvbuf[k], tvbuf[ns+k]);
printf("\n");

return 0;
}

