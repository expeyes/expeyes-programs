/* timers.c -- routines for handling the timer

   Copyright (C) 2008 Ajith Kumar, Inter-University Accelerator Centre,
   New Delhi. 

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 3, or (at your option)
   any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software Foundation,
   Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.  */


#include <avr/io.h>


#ifndef BV
  #define BV(bit)  (1 << (bit))
#endif

#define CPU_CLOCK	8000000		// 8 MHz clock is assumed
#define FLIMIT  (CPU_CLOCK/2)

static uint16_t f[] = {1,8,32,64,128,256,1024};
 
uint32_t set_frequency(uint32_t freq)
{
	uint32_t tmp;
	uint8_t ocr, k;

	DDRD |= 0x80;    // Make PD7 as output
	if(freq == 0) {
  	TCCR2 = BV(WGM21) | BV(COM20);	// CTC mode, clock disabled
  	return 0;
  } else if(freq <= 15) {
  	TCCR2 = BV(WGM21) | BV(COM20) | 7;	// CTC mode, ck/1024
  	OCR2 = 255;
  	return 15;
  } else if(freq >= FLIMIT) {
  	TCCR2 = BV(WGM21) | BV(COM20) | 1;	// CTC mode, ck/1
  	OCR2 = 0;
  	return FLIMIT;
  } else {
  	k = 0;
  	while(k < 7) {
    	tmp = FLIMIT / f[k];	// maximum value for the chosen prescaler
    	if (tmp/freq <= 256) {
      	TCCR2 = BV(WGM21) | BV(COM20) | (k+1);	// CTC mode
      	ocr = tmp/freq;
      	tmp = tmp/ocr;	// the value actually set
      	if (ocr) 
        	--ocr;
      	OCR2 = ocr;
      	return tmp;
      }
    	k = k + 1;
    }
  }
	return 0;  
}


#define MTIME	50000	// We count the pulses for 50 milliseconds only

uint32_t measure_frequency(void)
{
/*
Count the input of TC0 for 50000 microseconds (using TC1).
multiply by 20 to get the counts/second.
*/
  uint32_t low = 0;

  TCCR1B = BV(CS11);		// Feed Clock/8 (1 MHz ) to TCNT1
  TCCR0 = 7;			// TC0 counts External  clock
  TIFR |= BV(TOV0);		// Clear TCC0 OVF flag
  TCNT0 = 0;			// Reset TCNT0
  TCNT1 = 0;			// to keep time with clk/8
  while(TCNT1 < MTIME)
    {          
    if(TIFR & BV(TOV0))		// TC0 overflow after 255 counts
      {
      ++low;
      TIFR |= BV(TOV0);		// Clear OVF flag
      }
    }
  TCCR0 = 0;  
  return (low * 256 + TCNT0)*20;
  }


/* PWM DAC on counter 2, PD0 (OC2) */
void set_voltage(uint8_t val)	
{
	DDRD |= 0x80;	     // make PD0 as output
	OCR2 = val;
	// Fast PWM mode
	TCCR2 = BV(WGM21) | BV(WGM20) | BV(COM21) | BV(CS20);  
	TCNT2 = 0;
}

