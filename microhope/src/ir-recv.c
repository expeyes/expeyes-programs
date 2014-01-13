/*
IR Receiver on Atmega32. Uses TSOP1738 IR receiver output connected on PD2 (INT0)
Non standard single byte receiver, for data from expEYES Junior irsend1(byte)
Tested on microHOPE running at 8MHz
Author : Jithin B P, IISER, MOhali, jithinbp@gmail.com
License : GPL v3

TSOP1738 connections:
----- PD2
----- blank space
----- 5V
----- GND
*/

#include <avr/io.h>
#include <avr/interrupt.h>
#include "mh-lcd.c"


volatile uint8_t val=0,rb=0,x=0;
ISR (INT0_vect)		// interrupt triggered on a falling edge on PD2
{
uint16_t time;
time=TCNT1;
TCNT1=0;		

if(time>10000)		// Detected start pulse > 10 msec   ~13.5ms
		{
		rb=0;		//Set bit count to zero
		val=0;		//set receive buffer to zero
		return;
		}
else				
	rb+=1;			//increment bit count in case of short pulses

if(time >2000 && time < 2800)		// A binary 1 lies in this time interval of low pulse
	val = (val<<1)|1;
if(time>900 && time < 1500) // A binary zero has around this length acc. to protocol
	val = (val<<1);

if(rb==8) // Recived 1 byte. Display it on PORTA LEDs
	{
	lcd_clear();
	lcd_put_byte(val);
	}
}


main()
{
uint8_t x;
lcd_init();

PORTD = (1 << PD2);  // Enable internal pullup resistor

TCCR1B = (1<<CS01);		// Set TC1 to 1MHz. Divide 8MHz clock by 8. timer initialized!!
TCNT1=0;

MCUCR = (1<<ISC01);		// Falling edge on INT0
GICR = (1<<INT0);		// Enable INT0
sei();   				//enable interrupt

for(;;) ;  // infinite loop. Job is done inside the ISR only
}
