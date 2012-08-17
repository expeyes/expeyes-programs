/* 
Test program demonstrating single Input/Output & waveform generation. Compile & run using
$ gcc -Wall -o basic-io basic-io.c -lm
$ ./basic-io
*/

#include "ejlib.h" 
/* extern */ int fd;

int main()
{
byte ss[10], st;
float v, fr, ti;	

fd = open_eyesj();
if(fd < 0)
	{
	fprintf(stderr,"EYES Open Failed\n");
	exit(0);
	}

if(get_version(ss)) exit(1);
printf("The version of EYES-Junior found is %s\n",ss);

// Set PVS voltage
if(set_voltage(5.0, &v))exit(1);
printf("The voltage at PVS is set to %5.3f V\n", v);

// Read voltage from a channel. Connect PVS to IN1
if(get_voltage(3, &v)) exit(1);
printf("Voltage at IN1 is %5.3f V\n", v);

// Reads Logic level at a channel. Connect PVS to IN1
if(get_state(3, &st)) exit(1);
printf("Level at IN1 is %d\n", st);

// Sets Logic level at a channel.
if(set_state(10, 1)) exit(1);		// Check OD1 with a voltmeter. Or connect it to IN2
if(get_state(4, &st)) exit(1);		// and Read IN2
printf("Level at IN2 is %d\n", st);

// Sets square wave
if(set_sqr1(100.0, &fr)) exit(1);		
printf("SQR1 set to %5.3f Hz\n", fr);

// Sets square wave
if(set_sqrs(1000.0, 25.0, &fr)) exit(1);		// 25% => 90 degree phase shift between SQR1 & SQR2
printf("SQR1 & SQR2 set to %5.3f Hz\n", fr);


// The 1000Hz set on SQR1 & SQR2 are available on Readback channels 6 & 7. 
// We will use them for Time interval measurements.

if(r2ftime(6,6, &ti)) exit(1);		// Rising edge to Falling Edge
printf("Rise to Fall time on channel 6 = %5.0f usec\n", ti);

if(r2rtime(6,7, &ti)) exit(1);		// Rising edge to rising edge, delay between two channels
printf("Rise to Rise time from channel 6 to 7 = %5.0f usec\n", ti);

if(multi_r2rtime(6, 0, &ti)) exit(1);		// Time between two rising edges, same input
printf("Rise to Rise time for 6  = %5.0f usec\n", ti);

if(get_frequency(6, &fr)) exit(1);		// Frequency of squarewave on input 
printf("Rise to Rise time for 6  = %5.3f Hz\n", fr);

return 0;
}

