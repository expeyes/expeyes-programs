/*
EYES for Young Engineers and Scientists -Junior (EYES Junior 1.0)
Header file for the C library to communicate to the PIC24FV32KA302 uC running 'eyesj.c'
Author  : Ajith Kumar B.P, bpajith@gmail.com, ajith@iuac.res.in
License : GNU GPL version 3
Started on 25-Jun-2012
*/

#include <sys/types.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <fcntl.h>
#include <termios.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <math.h>

#define FALSE 			0
#define TRUE 			1
#define BAUDRATE		B115200

// commands without any arguments (1 to 40)
#define GETVERSION		1		// 1 + 5 bytes
#define READCMP         2       // 1 + 1
#define READTEMP        3       // 1 + 2
#define GETPORTB        4       // 1 + 2 Reads port B, in digital mode

// Commands with One byte argument (41 to 80)
#define READADC			41		// 1 + 2 , Read the specified ADC
#define GETSTATE        42      // 1 + 1 , Digital Input Status
#define NANODELAY       43      // 1 + 4 , TODO delay using CTMU
#define SETADCREF       44      // 1 + 0 , Choose Vdd (0) or External +Vref (1)
#define READADCSM		45		// 1 + 2 , Read ADC, in sleep mode

// Commands with Two bytes argument (81 to 120)
#define R2RTIME         81      // 1 + 1 + 4 bytes are returned for all time measurement calls.
#define R2FTIME         82      //
#define F2RTIME         83      //
#define F2FTIME         84      //
#define MULTIR2R        85      //
#define SET2RTIME       86      // From a Dout transition to the Din transition
#define SET2FTIME       87      //
#define CLR2RTIME       88      //
#define CLR2FTIME       89      //
#define HTPUL2RTIME     90      // High True Pulse to HIGH
#define HTPUL2FTIME     91      // High True Pulse to LOW
#define LTPUL2RTIME     92      //
#define LTPUL2FTIME     93      //
#define SETPULWIDTH     94      //
#define SETSTATE        95      // Pin number, hi/lo
#define SETDAC			96		//
#define	SETCURRENT		97		// channel, Irange
#define SETACTION       98      // capture modifiers, action, target pin
#define SETTRIGVAL      99      // Analog trigger level

// Commands with Three bytes argument (121 to 160)
#define	SETSQR1			121		// Set squarewave/level on OC2
#define	SETSQR2			122		// Set squarewave/level on OC3

// Commands with Four bytes argument (161 to 200)
#define MEASURECV       163     // ch, irange, duration
#define SETPWM1         164     // PWM on SQR1. scale, pr, ocrs
#define SETPWM2         165     // PWM on SQR1. scale, pr, ocrs

// Commands with Five bytes argument (201 to 240)
#define	CAPTURE			201		// 1 byte CH, 2 byte NS, 2 byte TG
#define	CAPTURE_HR		202		// 1 byte CH, 2 byte NS, 2 byte TG
#define SETSQRS         203     // scale, ocr, time diff

// Commands with Six bytes argument (241 to 255)
#define	CAPTURE2		241		// CH1,CH2: 1byte, NS, TG : 8 bit data
#define	CAPTURE2_HR		242		// same with 12 bit data
#define CAPTURE3        243     // 3 channels, 12 bit
#define CAPTURE4        244     // 3 channels, 12 bit

#define AANATRIG    	0      // Trigger on analog input level, set by SETRIGVAL
#define AWAITHI			1
#define AWAITLO			2
#define AWAITRISE		3
#define AWAITFALL		4
#define ASET			5
#define ACLR			6
#define APULSEHT		7
#define APULSELT		8

// Reply from PIC micro to the PC
#define SUCCESS		'D'			// Command executed successfully
#define	INVCMD		'C'			// Invalid Command
#define INVARG		'A'			// Invalid input data
#define INVBUFSIZE	'B'			// Resulting data exceeds buffersize
#define TIMEOUT		'T'			// Time measurement timed out
#define COMERR		'S'			// Serial Communication error
#define INVSIZE		'Z'			// Size mismatch, result of capture

#define MAXWAIT		40			// 40 deciseconds = 4 seconds
#define MAXTG		1000    	// Maximum timegap for CAPTURE, usec
#define MINTG		4			// Minimum timegap for CAPTURE, usec
#define MAXBUF		1800		// uC has only a 1800 bytes buffer.

typedef unsigned char byte;
typedef unsigned short  u16;
typedef	byte boolean;

int 	open_eyesj(void);			// Opens eyesj on USB (virtual serial ports /dev/ttyACM0 / ACM1)
int 	search_eyesj(char*);			// Search for EYESJ on the specified device
void 	close_eyesj(void);			// Close connection
boolean	sendByte(byte data);		// write one byte to serial port, returns TRUE or FALSE
boolean	sendInt(u16 data);			// write a 2 byte integer to serial port, returns TRUE or FALSE
int		sread(int nb, byte* data);	// reads nb bytes .Returns number of bytes read. -1 on error.

//------------------------- Digital I/O-----------------------------
byte set_state(byte pin, byte state);
byte get_state(byte pin, byte *st);

//---------------- Square Wave Generation & Measuring the Frequency ------------------
byte set_pwm(byte osc, float ds, byte resol);
byte set_sqr1_pwm(byte dc);
byte set_sqr2_pwm(byte dc);
byte set_sqr1_dc(float volt);
byte set_sqr2_dc(float volt);

byte set_osc(byte osc, float freq, float* fset);
byte set_sqr1(float freq, float *fset);
byte set_sqr2(float freq, float *fset);
byte set_sqrs(float freq, float diff, float *fset);

//====================== Time Interval measurements =============================
byte r2rtime(byte pin1, byte pin2, float *ti);
byte f2ftime(byte pin1, byte pin2, float *ti);
byte r2ftime(byte pin1, byte pin2, float *ti);
byte f2rtime(byte pin1, byte pin2, float *ti);
byte multi_r2rtime(byte pin, byte skip, float *ti);
byte get_frequency(byte pin, float *fr);
byte set2rtime(byte pin1, byte pin2, float *ti);
byte set2ftime(byte pin1, byte pin2, float *ti);
byte clr2rtime(byte pin1, byte pin2, float *ti);
byte clr2ftime(byte pin1, byte pin2, float *ti);
byte htpulse2rtime(byte pin1, byte pin2, float* ti);
byte htpulse2ftime(byte pin1, byte pin2, float *ti);
byte ltpulse2rtime(byte pin1, byte pin2, float *ti);
byte ltpulse2ftime(byte pin1, byte pin2, float *ti);

//========== CTMU ===============================
byte read_temp(int* temp);
byte measure_cv(int ch, int ctime, float i, float* v);
byte measure_cap(float *pf);
byte set_current(int ch, float i, float *v);

//============================ Analog I/O routines=====================================
byte 	read_adc(byte ch, u16* iv);  // Read ADC, in SLEEP mode
byte 	read_adcNS(byte ch, u16* iv);	// Read ADC, without entering SLEEP mode
byte 	get_voltage(byte ch, float* v);
byte 	get_voltageNS(byte ch, float* v);	// get_voltage, without entering SLEEP mode
byte 	write_dac(int iv);		// Returns zero on success
byte 	set_voltage(float v, float* vset);
byte 	capture(int ch, int ns, int tg, float* data); 
byte 	capture2(int ch1, int ch2, int ns, int tg, float* data); 
byte 	capture3(int ch1, int ch2, int ch3, int ns, int tg, float* data);
byte 	capture4(int ch1, int ch2, int ch3, int ch4, int ns, int tg, float* data);
byte 	capture_hr(int ch1, int ns, int tg, float* data);
byte 	capture2_hr(int ch1, int ch2, int ns, int tg, float* data);
//------------------- Modifiers for Capture ------------------------------
byte disable_actions();
byte enable_action(byte action, byte ch);
byte set_trig_source(byte ch);
byte enable_wait_high(byte ch);
byte enable_wait_low(byte ch);
byte enable_wait_rising(byte ch);
byte enable_wait_falling(byte ch);
byte enable_set_high(byte ch);
byte enable_set_low(byte ch);
byte enable_pulse_high(byte ch);
byte enable_pulse_low(byte ch);
byte set_pulsewidth(u16 width);
byte 	get_version(byte* res);

