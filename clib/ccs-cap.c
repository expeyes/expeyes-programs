/* 
Test program demonstrating capacitance measurement using uC CTMU. Compile & run using
$ gcc -Wall -o ccs-cap ccs-cap.c -lm
$ ./basic-io
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
float pf;	

fd = open_eyesj();
if(fd < 0)
	{
	fprintf(stderr,"EYES Open Failed\n");
	exit(0);
	}

// Connect a capacitance (100pF to 5000 pF range) between IN1 and GND
if(measure_cap(&pf))err("Too high value ?");
printf("The capacitance (+stray) = %5.3f pF\n", pf);

// Repeat the experiment without connecting the capacitor, to measure the stray capacitance

return 0;
}

