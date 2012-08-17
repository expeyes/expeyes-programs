/*
EYES for Young Engineers and Scientists -Junior (EYES Junior 1.0)
C library to communicate to the PIC24FV32KA302 uC running 'eyesj.c'
Author  : Ajith Kumar B.P, bpajith@gmail.com, ajith@iuac.res.in
License : GNU GPL version 3
Started on 25-Jun-2012

The micro-controller pins used are mapped into 13 I/O channels (numbered 0 to 12)
and act like a kind of logical channels.  The Python function calls refer to them
using the corresponding number, ie 0 => A0. 

 * 0 : A0, Analog Comaparator(A5) output.
 * 1 : A1, -5V to +5V range Analog Input 
 * 2 : A2, -5V to +5V range Analog Input 
 * 3 : IN1 , Can function as Digital or 0 to 5V Analog Input
 * 4 : IN2, Can function as Digital or 0 to 5V Analog Input
 * 5 : SEN, Simial to A3 & A4, but has a 5K external pullup resistor (Comp input)
 * 6 : SQR1-read, Input wired to SQR1 output
 * 7 : SQR2-read,  Input wired to SQR2 output
 * 8 : SQR1 control, 0 to 5V programmable Squarewave. Setting Freq = 0 means 5V, Freq = -1 means 0V
 * 9 : SQR2 control, 0 to 5V programmable Squarewave
 * 10: Digital output OD1, 
 * 11: CCS, Controls the 1mA constant current source. 
 * A12: Analog Input  AN0 / RA0  (dummy entry for RA0), special case
*/

#include "ejlib.h"

// The global variable below are an issue, if we want to make a DLL out of this. For the time being compile this file
//with the main program.

extern int		fd;						// File handle, global variable
// Conversion factors m and c (y = mx+c) for 12bit and 8bit ADC resolutions. Total 13 channels (some unused)
// Initialized by open() function.
float m12[13], m8[13], c[13];
float dacm = 5.0/4095;		// For DAC
float tgap = 0.004;			// Time gap between digitization of two channels

//================================= OS dependent code starts here ==================================
struct 	termios oldtio, newtio;

boolean sendByte(byte data)		// Sends a single byte. Returns TRUE or FALSE
{
if(write(fd, &data, 1) != 1)  return FALSE;
return TRUE;
}

boolean sendInt(u16 data)		// Sends a 16bit integer. Returns TRUE or FALSE
{
byte* buf = (byte*) &data;
if(write(fd, buf, 1) != 1)  return FALSE;
usleep(10000);
if(write(fd, buf+1, 1) != 1)  return FALSE;
return TRUE;
}

int ssread(int nb, byte* data)	// Read 'nb' bytes. Returns nb(-1 on error). Result in 'data'
{
if(read(fd, data, nb) != nb)
	{
	fprintf(stderr,"Read ERR %x\n",fd);
	return -1;
	}
return nb;
}

int sread(int nb, byte* data)	// Read 'nb' bytes. Returns nb(-1 on error). Result in 'data'
{
u16  br, tbr, bal;
tbr = br = 0;
bal = nb;

while(tbr < nb)		// Total bytes receibed < nb
	{
	tbr += read(fd, data+tbr, nb-tbr);
//	fprintf(stderr,"Read %d bytes. %d remaining\n", tbr, nb-tbr);
	}
return tbr;
}

int search_eyesj(char *device)	
// Search for the reply "ejx.x" (version x.x) on the specified port. Returns file handle or -1
{
  byte ss[10];
  
  fd = open (device, O_RDWR | O_NOCTTY);
  if (fd < 0)
	{
	fprintf(stderr,"ERROR opening %s\n",device); 
    return -1;
	}

  //printf("Opened Device %s\n", device);
  tcgetattr (fd, &oldtio);			// save current port settings 
  memset (&newtio, 0, sizeof (newtio));
  newtio.c_cflag = BAUDRATE | CS8 | CLOCAL | CREAD | PARENB;
  newtio.c_iflag = INPCK;
  newtio.c_oflag = 0;
  newtio.c_lflag = 0;				// non-canonical mode
  newtio.c_cc[VTIME] = 40; //MAXWAIT;		// Timeout for read in deciseconds
  newtio.c_cc[VMIN] = 0;			// read will return after VTIME for sure
  tcflush (fd, TCIOFLUSH);
  tcsetattr (fd, TCSANOW, &newtio);

  sendByte(GETVERSION);
  sread(1,ss);
  if(*ss != 'D')
	{
	fprintf(stderr,"No expEYES Found : %c:", *ss);
	return -1;
	}
  sread(5,ss);
  if(!strncmp((char*)ss,"ej",2))			// found proper version of hardware
		return fd;
  return -1;
}

void close_eyesj(void)
{
  tcflush (fd, TCIOFLUSH);
  tcsetattr (fd, TCSANOW, &oldtio);
}
//============================== OS dependent code ends here ==========================================

int open_eyesj(void) // Returns file descriptor on success and -1 on error. 
{
	int k;
	
	for(k=0; k <13; ++k) 			// Initialize the scale factors
		{
		m12[k] = 5.0/4095; 
		m8[k] = 5.0/255;
		c[k] = 0.0;
		}
	m12[1] = m12[2] = 10.0/4095;	// Channels 1 & 2 have -5 to +5 volts range
	m8[1] = m8[2] = 10.0/255;
	c[1] = c[2] = -5.0;

#ifdef WINDOWS						// Under MS-Windows, compile with option -DWINDOWS
	#define MAXPORT		255
	for(k= 0; k < MAXPORT; ++k)		// to be tested
		{
		char ss[10];
		sprintf(ss,"COM%d",k);
		fd = search_eyesj(ss);
		if(fd > 0)
			return fd;
		}
#else
	#define MAXPORT		2
	char *devlist[MAXPORT] = {"/dev/ttyACM0","/dev/ttyACM1"}; 
	for(k= 0; k < MAXPORT; ++k)
		{
		fd = search_eyesj(devlist[k]);
		if(fd > 0)
			return fd;
		}
#endif
return -1;		
}

//========= expEYES Junior Functions. All will return zero on success, or some error code.===============

//---------------- Square Wave Generation & Measuring the Frequency ------------------
byte set_osc(byte osc, float freq, float* fset)
	{
	// Sets the output frequency of the SQR1 (osc=0) or SQR2. The actual value set is returned in fset.
	static	float mtvals[4] = {0.125e-6, 8*0.125e-6, 64*0.125e-6, 256*0.125e-6};	// Possible Timer period values
	float	per;
	byte k, res[1], TCKPS = 0;		// TCKPS & OCRS are uC registers
	u16 OCRS = 0;

	if(freq < 0)	        // Disable Timer and Set Output LOW
		TCKPS = 254;
	else if(freq == 0)		// Disable Timer and Set Output HIGH
		TCKPS = 255;
	else					// Set the frequency
		{
		per = 1.0/freq;		// T requested
		for(k=0; k < 4; ++k)				// Find the optimum scaling, OCR value
			if(per < mtvals[k]*50000)
				{
				TCKPS = k;
				OCRS = per/mtvals[k];
				OCRS = (int)(OCRS+0.5);
				freq = 1.0/(mtvals[k]*OCRS);
				break;
				}
		if( (TCKPS < 4) && (OCRS == 0) )
			return INVARG;
		if(osc == 0)
			sendByte(SETSQR1);
		else
			sendByte(SETSQR2);
		sendByte(TCKPS);			// prescaling for timer
		sendInt(OCRS);				// OCRS value
		*res = COMERR;
		sread(1, res);
		if(*res != 'D')
			return *res;
		*fset = freq;
		}
	return 0;
	}

byte set_sqr1(float freq, float *fset)
	{
	//	Sets the frequency of SQR1 (between .7Hz and 200kHz). All intermediate values are not possible.
	//	Returns the actual value set.
	return set_osc(0, freq, fset);
	}

byte set_sqr2(float freq, float *fset)
	{
	//	Sets the frequency of SQR2 (between .7Hz and 200kHz). All intermediate values are not possible.
	//	Returns the actual value set.
	return set_osc(1, freq, fset);
	}

byte set_sqrs(float freq, float diff, float *fset)       // Freq in Hertz, phase difference in % of T
	{
	// Sets the output frequency of both SQR1 & SQR2. 'fset' returns actual value set. 
	// The second argument is the phase difference between them  in percentage.
	static	float mtvals[4] = {0.125e-6, 8*0.125e-6, 64*0.125e-6, 256*0.125e-6};	// Possible Timer period values
	float	per;
	byte k, res[1], TCKPS = 0;		// TCKPS, TG & OCRS are uC registers
	u16 TG, OCRS = 0;

	if(freq == 0)				// Disable both Square waves
		{
		set_sqr1(0, fset);
		set_sqr2(0, fset);
		return 0;
		}
	else if(freq < 0)			// Disable both Square waves
		{
		set_sqr1(-1, fset);
		set_sqr2(-1, fset);
		return 0;
		}
	if( (diff < 0) || (diff >= 100.0) )
		{
		fprintf(stderr,"Invalid phase difference\n");
		return INVARG;
		}
	per = 1.0/freq;						// period T requested
	for(k=0; k < 4; ++k)				// Find the optimum scaling, OCR value
		if(per < mtvals[k]*50000)
			{
			TCKPS = k;
			OCRS = per/mtvals[k];
			OCRS = (int)(OCRS+0.5);
			freq = 1./(mtvals[k]*OCRS);
			break;
			}
	if( (TCKPS < 4) && (OCRS == 0) )
		{
		fprintf(stderr,"Invalid Freqency\n");
		return INVARG;
		}
	TG = (int)(diff*OCRS/100.0 +0.5);
	if(TG == 0) TG = 1;		// Need to examine this
	//print 'TCKPS ', TCKPS, 'ocrs ', OCRS, TG
	sendByte(SETSQRS);
	sendByte(TCKPS);		// prescaling for timer
	sendInt(OCRS);			// OCRS value
	sendInt(TG)	;			// time difference
	*res = COMERR;
	sread(1, res);
	if(*res != 'D')
		return *res;
	*fset = freq;
	return 0;
	}


byte set_pwm(byte osc, float ds, byte resol) // osc#, duty cycle, resolution 
	{
	// Sets PWM on SQR1 / SQR2. The frequency is decided by the resolution in bits.
	byte res[1];
	u16 ocxrs, ocx;
	
	if( (ds > 100) || (resol < 6) || (resol > 16) )
		return INVARG;
	ocxrs = pow(2.0, resol);  
	ocx = (u16)(0.01 * ds * ocxrs + 0.5);
	if(osc == 0)
		sendByte(SETPWM1);
	else
		sendByte(SETPWM2);
	sendInt(ocxrs-1);			// ocxrs
	sendInt(ocx);				//ocx
	*res = COMERR;
	sread(1, res);
	if(*res != 'D')
		{
		fprintf(stderr, "SETPWM error\n");
		return *res;
		}
	return 0;
	}
	
byte set_sqr1_pwm(byte dc)
	{
	// 	Sets 488 Hz PWM on SQR1. Duty cycle is specified in percentage. The third argument, PWM resolution, is 
	//	14 bits by default. Decreasing this by one doubles the frequency.
	return set_pwm(0,dc,14);
	}

byte set_sqr2_pwm(byte dc)
	{
	// Sets 488 Hz PWM on SQR2. Duty cycle is specified in percentage. The third argument, PWM resolution, is 
	//	14 bits by default. Decreasing this by one doubles the frequency.
	return set_pwm(1,dc,14);
	}

byte set_sqr1_dc(float volt)
	{
	// PWM DAC on SQR1. Resolution is 10 bits (f = 7.8 kHz) by default. External Filter is required to get the DC
	// The voltage can be set from 0 to 5 volts.
	return set_pwm(0, volt * 20.0, 10)/20;   // 100% means 5 volts., 10 bit resolution, 8kHz 
	}

byte set_sqr2_dc(float volt)
	{    
	// PWM DAC on SQR2. Resolution is 10 bits (f = 7.8 kHz) by default. External Filter is required to get the DC
	// The voltage can be set from 0 to 5 volts.
	return set_pwm(1, volt * 20.0, 10)/20;   // 5V correspods to 100%
	}

//------------------------- Digital I/O-----------------------------
byte set_state(byte pin, byte state)
	{
	// Sets the status of Digital outputs SQR1, SQR2, OD1 or CCS. 
	// It will work on SQR1 & SQR2 only if the frequency is set to zero.
	byte res[1];

	sendByte(SETSTATE);
	sendByte(pin);	
	sendByte(state);	
	*res = COMERR;
	sread(1, res);
	if (*res != 'D')
		{
		fprintf(stderr, "SETSTATE error \n");
		return *res;
		}
	return 0;
	}

byte get_state(byte pin, byte *st)
	{
	//	gets the status of the digital input pin. IN1, IN2 & SEN are set to digital mode before sensing input level.
	byte res[1];

	sendByte(GETSTATE);	
	sendByte(pin);	
	*res = COMERR;
	sread(1, res);
	if(*res != 'D')
		{
		fprintf(stderr,"GETSTATE error\n");
		return *res;
		} 
	if(sread(1,res) != 1) return COMERR;
	*st = *res;
	return 0;
	}

//---------- Time Interval Measurements ----------------------
byte tim_helper(byte cmd, byte src, byte dst, float* ti)
	{
	// Helper function for all Time measurement calls. Command, Source and destination pins are imputs.
	// Returns time in microseconds, -1 on error.
	byte res[4];
	unsigned int* up = (unsigned int*) res;

	if(cmd == MULTIR2R)
		{
		if(src > 7)
			{	
			fprintf(stderr, "Pin should be digital input capable: 0,3,4,5,6 or 7\n");
			return INVARG;
			}
		if(dst > 249)
			{	
			fprintf(stderr, "Skip should be less than 250\n");
			return INVARG;
			}
		}

	if( (cmd == R2RTIME) || (cmd == R2FTIME) || (cmd == F2RTIME) || (cmd == F2FTIME) )
		{
		if( (src > 7) || (dst > 7) )
			{
			fprintf(stderr,"Both pins should be digital input capable: 0,3,4,5,6 or 7\n");
			return INVARG;
			}
		}

	if( (cmd == SET2RTIME) || (cmd == CLR2RTIME) ||(cmd == SET2FTIME) ||(cmd == CLR2FTIME) ||
		(cmd == HTPUL2RTIME) ||(cmd == HTPUL2FTIME) ||(cmd == LTPUL2RTIME) || (cmd == LTPUL2FTIME) )
		{
		if( (src < 8) || (src > 11) )
			{
			fprintf(stderr,"Starting pin should be digital output capable: 8,9,10 or 11\n");
			return INVARG;
			}
		if(dst > 7)
			{
			fprintf(stderr,"Destination pin should be digital input capable: 0,3,4,5,6 or 7\n");
			return INVARG;
			}
		}
	sendByte(cmd);	
	sendByte(src);	
	sendByte(dst);	
	*res = COMERR;
	sread(1, res);
	if(*res != 'D')
		{
		fprintf(stderr, "Time measurement error = %c\n", *res);
		return *res;
		}
	sread(1, res);				// Read & ingnore this byte, due to word alignment of uC
	if(sread(4, res) != 4) 
		{
		fprintf(stderr, "Time measurement Data read error\n");
		return COMERR;
		}
	//printf("%d\n", *up);
	*ti = (float)*up *0.125;		 //convert to microseconds
	return 0;
	}

byte r2rtime(byte pin1, byte pin2, float *ti)
	{
	// Time between a rising edge to a rising edge. The pins must be distinct.
	return tim_helper(R2RTIME, pin1, pin2, ti);
	}

byte f2ftime(byte pin1, byte pin2, float *ti)
	{
	// Time between a falling edge to a falling edge. The pins must be distinct.
	return tim_helper(F2FTIME, pin1, pin2, ti);
	}

byte r2ftime(byte pin1, byte pin2, float *ti)
	{
	// Time between a rising edge to a falling edge. The pins could be same or distinct.
	return tim_helper(R2FTIME, pin1, pin2, ti);
	}

byte f2rtime(byte pin1, byte pin2, float *ti)
	{
	// Time between a falling edge to a rising edge. The pins could be same or distinct.
	return tim_helper(R2FTIME, pin1, pin2, ti);
	}

byte multi_r2rtime(byte pin, byte skip, float *ti)
	{
	//Time between rising edges, could skip desired number of edges in between. (pin, 9) will give time required for
	//	10 cycles of a squarewave, increases resolution.
	return tim_helper(MULTIR2R, pin, skip, ti);
	}

byte get_frequency(byte pin, float *fr)
	{
	// This function measures the frequency of an external 0 to 5V PULSE on digital inputs, by calling multi_r2rtime().
	float ti;
	if( multi_r2rtime(pin, 0, &ti)) return COMERR;
	*fr = 1.0e6 / ti;
	if(ti < 10000)			// increase accuracy by averaging
		{
		if(multi_r2rtime(pin,9, &ti))return COMERR;
		*fr = 1.0e7/ti;
		}
	return 0;
	}

//======================== Active time interval measurements ==========================
byte set2rtime(byte pin1, byte pin2, float *ti)
	{
	// Time from setting pin1 to a rising edge on pin2.
	return tim_helper(SET2RTIME, pin1, pin2, ti);
	}

byte set2ftime(byte pin1, byte pin2, float *ti)
	{
	// Time from setting pin1 to a falling edge on pin2.
	return tim_helper(SET2FTIME, pin1, pin2, ti);
	}

byte clr2rtime(byte pin1, byte pin2, float *ti)
	{
	// Time from clearing pin1 to a rising edge on pin2.
	return tim_helper(CLR2RTIME, pin1, pin2, ti);
	}

byte clr2ftime(byte pin1, byte pin2, float *ti)
	{
	// Time from clearing pin1 to a falling edge on pin2.
	return tim_helper(CLR2FTIME, pin1, pin2, ti);
	}

byte htpulse2rtime(byte pin1, byte pin2, float* ti)
	{
	// Time from a HIGH True pulse on pin1 to a rising edge on pin2.
	return tim_helper(HTPUL2RTIME, pin1, pin2, ti);
	}

byte htpulse2ftime(byte pin1, byte pin2, float *ti)
	{
	// Time from HIGH True pulse on pin1 to a falling edge on pin2.
	return tim_helper(HTPUL2FTIME, pin1, pin2, ti);
	}

byte ltpulse2rtime(byte pin1, byte pin2, float *ti)
	{
	// Time from a LOW True pulse on pin1 to a rising edge on pin2.
	return tim_helper(LTPUL2RTIME, pin1, pin2, ti);
	}

byte ltpulse2ftime(byte pin1, byte pin2, float *ti)
	{
	// Time from LOW True pulse on pin1 to a falling edge on pin2.
	return tim_helper(LTPUL2FTIME, pin1, pin2, ti);
	}

//=================== Charge Time Measurement Unit related functions ==========================
byte read_temp(int* temp)
	{
//	Reads the temperature of uC, currently of no use. Have to see whether this can be used for correcting
//	the drift of the 5V regulator with temeperature.
	byte res[2];

	sendByte(READTEMP);
	*res = COMERR;		// Assume an error
	sread(1,res);
	if( *res != 'D') return *res;
	if(sread(2,res) != 2) return COMERR;
	*temp = res[0] | (res[1] << 8);
	return 0;
	}

byte measure_cv(int ch, int ctime, float i, float* v)
//	Using the CTMU of PIC, charges a capacitor connected to IN1, IN2 or SEN, for 'ctime' microseconds
//		and then mesures the voltage across it.
//		The value of current can be set to .55uA, 5.5 uA, 55uA or 550 uA
	{  
	byte res[2], irange;
	int  iv;

	if(i > 500)			// 550 uA range
		irange = 0;
	else if(i > 50)		//	55 uA
		irange = 3;
	else if(i > 5)		// 5.5 uA
		irange = 2;
	else				// 0.55 uA
		irange = 1;

	if( (ch != 3) && ( ch !=4) )
		{
		fprintf(stderr, "Current to be set only on IN1 or IN2. %d\n",ch);
		return INVARG;
		}
	sendByte(MEASURECV);
	sendByte(ch);
	sendByte(irange);
	sendInt(ctime);
	*res = COMERR;
	sread(1, res);
	if (*res != 'D') return *res;
	if(sread(2,res) != 2) return COMERR;
	iv = res[0] | (res[1] << 8);
	*v = m12[ch] * iv + c[ch];
	return 0;
	}

byte measure_cap(float* pf)
	{
// Measures the capacitance (in picoFarads) connected between IN1 and GND. Stray capacitance should be
// subtracted from the measured value. Measurement is done by charging the capacitor with 5.5 uA
// for a given time interval. 
	int ctime;
	float v;
	for(ctime= 10; ctime < 10000; ctime +=10)
		{
		if(measure_cv(3, ctime, 5.5, &v)) return COMERR;   // 5.5 uA range is chosen
		if(v > 2.0) break;
		if(v > 4)
			{
			fprintf(stderr,"Error measuring capacitance. V = %5.3f\n", v);
			return INVARG;
			}
		}
	if(v == 0) return INVSIZE;
	*pf = 5.5 * ctime / v; 		// microAmp * microSecond makes the result in picoFarads 
	printf("MC %d %f %f\n", ctime, v, *pf);
	return 0;
	}

byte set_current(int ch, float i, float *v)
	{
	// Sets CTMU current 'i' on a channel 'ch' and returns the voltage measured across the load. 
	// Allowed values of current are .55, 5.5, 55 and 550 micro ampleres. ch=0 puts CTMU Off.
	byte res[2], irange;
	int  iv;

	if(i > 500)			// 550 uA range
		irange = 0;
	else if(i > 50)		//	55 uA
		irange = 3;
	else if(i > 5)		// 5.5 uA
		irange = 2;
	else				// 0.55 uA
		irange = 1;

	if( (ch != 0) && (ch != 3) && ( ch !=4) )
		{
		fprintf(stderr, "Current to be set only on IN1 or IN2. %d\n",ch);
		return INVARG;
		}
	sendByte(SETCURRENT);
	sendByte(ch);
	sendByte(irange);
	*res = COMERR;
	sread(1, res);
	if( *res != 'D') return *res;
	if(sread(2,res)!= 2) return COMERR;
	iv = res[0] | (res[1] << 8);
	*v = m12[ch] * iv + c[ch];
	return 0;
	}

//====================== Analog Set, Get & Capture functions =======================================
byte read_adc(byte ch, u16* iv)  // Read ADC, in SLEEP mode
	{
	byte res[2];
	if ((ch < 0) || (ch > 12))
		return INVARG;
	sendByte(READADCSM);
	sendByte(ch);
	*res = COMERR;
	sread(1, res);
	if (*res != 'D') return *res;
	if(sread(2, res) != 2) return COMERR;
	*iv = res[0] | (res[1] << 8);
	return 0;
	}

byte read_adcNS(byte ch, u16* iv)	// Read ADC, without entering SLEEP mode
	{
	byte res[2];
	if ((ch < 0) || (ch > 12))
		return INVARG;
	sendByte(READADC);
	sendByte(ch);
	*res = COMERR;
	sread(1, res);
	if (*res != 'D') return *res;
	if(sread(2, res) != 2) return COMERR;
	*iv = res[0] | (res[1] << 8);
	return 0;
	}

byte get_voltage(byte ch, float* v)
	{
	u16 iv;
	byte res;
	res = read_adc(ch, &iv);
	if(res != 0) return res;			// Error return
	*v = m12[ch] * iv + c[ch];
	return 0;
	}

byte get_voltageNS(byte ch, float* v)	// get_voltage, without entering SLEEP mode
	{
	u16 iv;
	byte res;
	res = read_adcNS(ch, &iv);
	if(res != 0) return res;			// Error return
	*v = m12[ch] * iv + c[ch];
	return 0;
	}

byte write_dac(int iv)		// Returns zero on success
	{
	byte res[1];
	if(iv < 0) iv = 0;		// Keep within limits
	else if (iv > 4095) iv = 4095;

	sendByte(SETDAC);
	sendInt(iv);
	*res = COMERR;   	// Assume an error
	sread(1, res);
	if(*res != 'D')	return *res;
	return 0;
	}

byte set_voltage(float v, float* vset)
	{
	//	Sets the PVS voltage. Reads it back and applies correction in a loop.
	u16 k, iv, isv, goal;
	if ((v < 0) || (v > 5.0))
		return INVARG;
	goal = (int)(v / dacm + 0.5);
	iv = goal;
	for(k=0; k < 15; ++k)
		{
		if(write_dac(iv)) return COMERR;
		if(read_adc(12, &isv)) return COMERR;	// Read channel 12.
		if (abs(isv-goal) <= 1) break;
		if (isv > goal) iv -= 1;
		else if(isv < goal) iv += 1;
		}
	*vset = m12[12] * isv + c[12];		//The voltage actually set
	return 0;
	}

/*------------ capture functions (8bit data)--------------------
Accepts channel numbers (ch, ch2 etc), Number of samples "ns",and Time interval between two samples "tg".
The return value consists of arrays of Time & Voltage, starting at location 'data'. The first 'ns' floats are the Time, 
followed by another 'ns' floats of voltage. This repeats for each channel captured.
*/
byte capture(int ch, int ns, int tg, float* data) 
// Returns 2 vectors(of size 'ns'), T1, V1 starting at pointer *data
	{
	byte 	res[MAXBUF], *bp=res;
	u16		k;
	
	//	Arguments : channel number , number of samples and timegap. data out is Time (ns*float), Voltage(ns*float)
	if( (ch < 0) || (ch > 12) || (tg < 4) || (ns > 1800))
		{
		fprintf(stderr,"ch= %d ns = %d tg = %d\n", ch, ns, tg);
		return INVARG;
		}
	sendByte(CAPTURE);
	sendByte(ch);
	sendInt(ns);
	sendInt(tg);
	*res = COMERR;				// fill response with error, call should correct it.
	sread(1, res);				// get response
	if(*res != 'D')
		{
		fprintf(stderr,"Invalid argument list\n");
		return *res;
		}
	sread(1, res);				// Read & ingnore this byte, due to word alignment of uC
	k = sread(ns, res);			// Read 'ns' data bytes
	if(k != ns)
		{
		fprintf(stderr, "CAPTURE:Expected %d bytes. Got %d only\n", ns, k);
		return INVSIZE;
		}
	for(k=0; k < ns; ++k) *data++ = 0.001 * k * tg;			// Fill Time, microseconds to milliseconds
	for(k=0; k < ns; ++k) *data++ = *bp++ * m8[ch] + c[ch]; // Fill voltage
	return 0;
	}

byte capture2(int ch1, int ch2, int ns, int tg, float* data) 
// Returns 4 vectors(of size 'ns'), T1, V1,T2,V2 starting at pointer *data
	{
	byte 	res[MAXBUF], *bp=res;
	u16		k;

	sendByte(CAPTURE2);
	sendByte(ch1);
	sendByte(ch2);
	sendInt(ns);
	sendInt(tg);
	*res = COMERR;				// fill response with error, call should correct it.
	sread(1, res);				// response byte
	if(*res != 'D')
		{
		fprintf(stderr,"Invalid argument list\n");
		return *res;
		}
	sread(1, res);				// Read & ingnore this byte, due to word alignment of uC
	k = sread(2*ns, res);		// Read '2*ns' data bytes, comes inter leaved, like, a1, b1, a2, b2 ...
	if(k != 2*ns)
		{
		fprintf(stderr, "CAPTURE:Expected %d bytes. Got %d only\n", 2*ns, k);
		return INVSIZE;
		}
	for(k=0; k < ns; ++k)		// Fill the inter-leaved data as T1, V1, T2, V2
		{
		data[k] = 0.001 * k * tg;					// Fill T1, microseconds to milliseconds
		data[k + 2*ns] = 0.001 * k * tg + tgap;		// Fill T2, with offset
		data[k + ns] = *bp++ * m8[ch1] + c[ch1]; 	// Fill V1
		data[k + 3*ns] = *bp++ * m8[ch2] + c[ch2]; 	// Fill V2
		}
	return 0;
	}

byte capture3(int ch1, int ch2, int ch3, int ns, int tg, float* data) 
// Returns 6 vectors(of size 'ns'), T1, V1,T2,V2,T3,V3 starting at pointer *data
	{
	byte 	ch12, res[MAXBUF], *bp=res;
	u16		k;
	sendByte(CAPTURE3);
	ch12 = (ch2 << 4) | ch1;		// ch1 & ch2 packed into one byte
	sendByte(ch12);
	sendByte(ch3);
	sendInt(ns);
	sendInt(tg);
	*res = COMERR;				// fill response with error, call should correct it.
	sread(1, res);				// response
	if(*res != 'D')
		{
		fprintf(stderr,"Invalid argument list\n");
		return *res;
		}
	sread(1, res);				// Read & ingnore this byte, due to word alignment of uC
	k = sread(3*ns, res);			// Read '2*ns' data bytes
	if(k != 3*ns)
		{
		fprintf(stderr, "CAPTURE:Expected %d bytes. Got %d only\n", 3*ns, k);
		return INVSIZE;
		}
	for(k=0; k < ns; ++k)		// Fill the inter-leaved data as T1, V1, T2, V2
		{
		data[k] = 0.001 * k * tg;					// Fill T1, microseconds to milliseconds
		data[k + 2*ns] = 0.001 * k * tg + tgap;		// Fill T2, with 1*offset
		data[k + 4*ns] = 0.001 * k * tg + 2*tgap;	// Fill T3, with 2*offset
		data[k + ns] = *bp++ * m8[ch1] + c[ch1]; 	// Fill V1
		data[k + 3*ns] = *bp++ * m8[ch2] + c[ch2]; 	// Fill V2
		data[k + 5*ns] = *bp++ * m8[ch3] + c[ch3]; 	// Fill V3
		}
	return 0;
	}

byte capture4(int ch1, int ch2, int ch3, int ch4, int ns, int tg, float* data) 
// Returns 8 vectors(of size 'ns'), T1, V1,T2,V2,T3,V3,T4,V4 starting at pointer *data
	{
	byte 	ch12, ch34, res[MAXBUF], *bp=res;
	u16		k;
	sendByte(CAPTURE4);
	ch12 = (ch2 << 4) | ch1;		// ch1 & ch2 packed into one byte
	ch34 = (ch4 << 4) | ch3;		// ch3 & ch4 packed into one byte
	sendByte(ch12);
	sendByte(ch34);
	sendInt(ns);
	sendInt(tg);
	*res = COMERR;				// fill response with error, call should correct it.
	sread(1, res);				// response byte
	if(*res != 'D')
		{
		fprintf(stderr,"Invalid argument list\n");
		return *res;
		}
	sread(1, res);				// Read & ingnore this byte, due to word alignment of uC
	k = sread(4*ns, res);			// Read '2*ns' data bytes
	if(k != 4*ns)
		{
		fprintf(stderr, "CAPTURE:Expected %d bytes. Got %d only\n", 4*ns, k);
		return INVSIZE;
		}
	for(k=0; k < ns; ++k)		// Fill the inter-leaved data as T1, V1, T2, V2
		{
		data[k] = 0.001 * k * tg;					// Fill T1, microseconds to milliseconds
		data[k + 2*ns] = 0.001 * k * tg + tgap;		// Fill T2, with 1*offset
		data[k + 4*ns] = 0.001 * k * tg + 2*tgap;	// Fill T3, with 2*offset
		data[k + 6*ns] = 0.001 * k * tg + 3*tgap;	// Fill T4, with 3*offset
		data[k + ns] = *bp++ * m8[ch1] + c[ch1]; 	// Fill V1
		data[k + 3*ns] = *bp++ * m8[ch2] + c[ch2]; 	// Fill V2
		data[k + 5*ns] = *bp++ * m8[ch3] + c[ch3]; 	// Fill V3
		data[k + 7*ns] = *bp++ * m8[ch4] + c[ch4]; 	// Fill V3
		}
	return 0;
	}

//----------------------- Capture with 12 bit resolution, each item is 2byte in size -----------------
byte capture_hr(int ch, int ns, int tg, float* data) 
// Returns two vectors(of size 'ns'), T1, V1 starting at pointer *data
	{
	byte 	res[MAXBUF];
	u16		k, *ip = (u16*)res;
	
	sendByte(CAPTURE_HR);
	sendByte(ch);
	sendInt(ns);
	sendInt(tg);
	sread(1, res);				// response byte
	if(*res != 'D')
		return COMERR;
	sread(1, res);				// Read & ingnore this byte, due to word alignment of uC
	k = sread(2*ns, res);		// Read 2*ns data bytes
	if(k != 2*ns)
		{
		fprintf(stderr, "CAPTURE_HR:Expected %d bytes. Got %d only\n", 2*ns, k);
		return INVSIZE;
		}
	for(k=0; k < ns; ++k) *data++ = 0.001 * k * tg;				// Fill Time, microseconds to milliseconds
	ip = (u16*)res;
	for(k=0; k < ns; ++k) *data++ = *ip++ * m12[ch] + c[ch]; 	// Fill voltage
	return 0;
	}

byte capture2_hr(int ch1, int ch2, int ns, int tg, float* data) 
// Returns four vectors, T1, V1, T2, V2 , starting at pointer *data
	{
	byte 	res[MAXBUF];
	u16		k, *ip = (u16*)res;
	
	sendByte(CAPTURE2_HR);
	sendByte(ch1);
	sendByte(ch2);
	sendInt(ns);
	sendInt(tg);
	sread(1, res);				// response byte
	if(*res != 'D')
		return COMERR;
	sread(1, res);				// Read & ingnore this byte, due to word alignment of uC
	k = sread(4*ns, res);		// Read 2*2*ns data bytes, each data 2 bytes
	if(k != 4*ns)
		{
		fprintf(stderr, "CAPTURE:Expected %d bytes. Got %d only\n", 4*ns, k);
		return INVSIZE;
		}
	for(k=0; k < ns; ++k)		// Fill the inter-leaved data as T1, V1, T2, V2
		{
		data[k] = 0.001 * k * tg;					// Fill T1, microseconds to milliseconds
		data[k + 2*ns] = 0.001 * k * tg + tgap;		// Fill T2, with offset
		data[k + ns] = *ip++ * m12[ch1] + c[ch1]; 	// Fill V1
		data[k + 3*ns] = *ip++ * m12[ch2] + c[ch2];	// Fill V2
		}
	return 0;
	}

//------------------- Modifiers for Capture ------------------------------
byte disable_actions()
	{
	// Disable all modifiers to the capture call. The capture calls will be set to 
	// do analog triggering on the first channel captured.
	byte res[1];

	sendByte(SETACTION);
	sendByte(AANATRIG);
	sendByte(0);			//Self trigger on channel zero means the first channel captured
	*res = COMERR;
	sread(1,res);
	if(*res != 'D') return *res;
	return 0;
	}

byte enable_action(byte action, byte ch)
	{
	byte res[1];

	if( (action < 0) || (action > 8) || (ch < 1) || (ch > 11) )
		{
		fprintf(stderr, "Invalid actions or source specified\n");
		return INVARG;
		}
	sendByte(SETACTION);
	sendByte(action);
	sendByte(ch);
	*res = COMERR;
	sread(1,res);
	if(*res != 'D') return *res;
	return 0;
	}

byte set_trig_source(byte ch)
	{
	// Analog Trigger of the desired channel
	return enable_action(AANATRIG, ch);
	}

byte enable_wait_high(byte ch)
	{
	// Wait for a HIGH on the speciied 'pin' just before every Capture.
	return enable_action(AWAITHI, ch);
	}

byte enable_wait_low(byte ch)
	{
	// Wait for a LOW on the speciied 'pin' just before every Capture.
	return enable_action(AWAITLO, ch);
	}

byte enable_wait_rising(byte ch)
	{
	// Wait for a rising EDGE on the speciied 'pin' just before every Capture.
	return enable_action(AWAITRISE, ch);
	}

byte enable_wait_falling(byte ch)
	{
	// Wait for a falling EDGE on the speciied 'pin' just before every Capture.
	return enable_action(AWAITFALL, ch);
	}

byte enable_set_high(byte ch)
	{
	// Sets the speciied 'pin' HIGH, just before every Capture.
	return enable_action(ASET, ch);
	}

byte enable_set_low(byte ch)
	{
	// Sets the speciied 'pin' LOW, just before every Capture.
	return enable_action(ACLR, ch);
	}

byte enable_pulse_high(byte ch)
	{
	// Generate a HIGH TRUE Pulse on the speciied 'pin', just before every Capture.
	// width is specified by the set_pulsewidth() function.
	return enable_action(APULSEHT, ch);
	}

byte enable_pulse_low(byte ch)
	{
	// Generate a LOW TRUE Pulse on the speciied 'pin', just before every Capture.
	return enable_action(APULSELT, ch);
	}
	
byte set_pulsewidth(u16 width)
	{
	// Sets the 'pulse_width' parameter for pulse2rtime() command. 
	// Also used by usound_time() and the elable_pulse_high/low() functions
	byte res[1];

	if( (width < 1) || (width > 500) )
		return INVARG;
	sendByte(SETPULWIDTH);
	sendInt(width);
	*res = COMERR;
	sread(1,res);
	if(*res != 'D') return *res;
	return 0;
	}

//==================== End Analog I/O ========================

byte get_version(byte* res)
	{
	if(sendByte(GETVERSION)== FALSE) return COMERR;
	*res = COMERR;	// Assume en error
	sread(1, res);
	if(*res != 'D') return *res;
	if(sread(5,res)==5) return 0;
	return COMERR;
	}

