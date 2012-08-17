/* 
Test program demonstrating Analog I/O functions.
Connect SINE to A1 before running the code. Compile & run using
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

// Capture single channel, 8 bit resolution
ns = 1800;
if(capture(1, ns, 100, tvbuf))err("capture");
for(k=0; k < ns; ++k) printf("%f  %f\n", tvbuf[k], tvbuf[ns+k]);
printf("\n");

// Capture two channes, 8 bit resolution
ns = 900;
if(capture2(1, 6, ns, tg, tvbuf))err("capture2");
for(ch=0; ch < 2; ++ch)
	{
	fp = tvbuf + ch*2*ns;
	for(k=0; k < ns; ++k) printf("%f  %f\n", fp[k], fp[ns+k]);
	printf("\n");
	}
exit(0);

// Capture three channes, 8 bit resolution
ns = 600;
if(capture3(1, 6, 7, ns, tg, tvbuf))err("capture3");
for(ch=0; ch < 3; ++ch)
	{
	fp = tvbuf + ch*2*ns;
	for(k=0; k < ns; ++k) printf("%f  %f\n", fp[k], fp[ns+k]);
	printf("\n");
	}

// Capture four channes, 8 bit resolution
ns = 450;
if(capture4(1, 6, 7, 1, ns, tg, tvbuf))err("capture4");
for(ch=0; ch < 4; ++ch)
	{
	fp = tvbuf + ch*2*ns;
	for(k=0; k < ns; ++k) printf("%f  %f\n", fp[k], fp[ns+k]);
	printf("\n");
	}

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

