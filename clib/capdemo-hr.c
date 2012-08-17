/* 
Test program demonstrating Analog I/O functions.
Connect SINE to A1 before running the code. Compile & run using
$ gcc -Wall -o capdemo-hr capdemo-hr.c -lm
$ ./capdemo-hr > log.dat
$ xmgrace log.dat
*/

#include "ejlib.c"

int fd;

void err(char* s)
{
fprintf(stderr,"Error: %s\n",s);
exit(0);
}

int main()
{
float fr, tvbuf[MAXBUF*2], *fp;		// Array to store Time & Voltage data from capture.
int	ch, ns, tg, k;

fd = open_eyesj();
if(fd < 0)
	{
	fprintf(stderr,"EYES Open Failed\n");
	exit(0);
	}

set_sqr1(100.0, &fr);		// Sets 100Hz on SQR1 & SQR2 , with 50% phase difference

tg = 100;

// Capture single channel, 12 bit resolution
ns = 900;
if(capture_hr(1, ns, 100, tvbuf))err("capture_hr");
for(k=0; k < ns; ++k) printf("%f  %f\n", tvbuf[k], tvbuf[ns+k]);
printf("\n");

// Capture two channes, 12 bit resolution
ns = 450;
if(capture2(1, 6, ns, tg, tvbuf))err("capture2_hr");
for(ch=0; ch < 2; ++ch)
	{
	fp = tvbuf + ch*2*ns;		// Point to the location where desired T,V is stored.
	for(k=0; k < ns; ++k) printf("%f  %f\n", fp[k], fp[ns+k]);
	printf("\n");
	}

return 0;
}

