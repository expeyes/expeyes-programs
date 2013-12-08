/* adc.c -- routines for handling the Analog to Digital converter

   Copyright (C) 2008 Ajith Kumar, Inter-University Accelerator Centre,
   New Delhi. 

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 3, or (at your option)
   any later version.
*/

#include <avr/io.h>

#ifndef BV
  #define BV(bit)  (1 << (bit))
#endif

#define REF_EXT		0	// Feed reference voltage externally
#define REF_INT		(3<<6)	// use the 2.56 V internal reference
#define REF_AVCC	(1<<6)	// Connect AVCC internally to reference
#define ADMAX		7	// channels 0 to 7 
#define ADC_SPEED	7	// ADCClk = (8 MHz/ 128) = 62.5 KHz =>208 usec


uint8_t adc_active = 0;
uint8_t adc_ref = REF_AVCC;		// Default is to use AVCC

void adc_enable(void)
{
	ADCSRA = BV(ADEN);		// Enable the ADC
	ADMUX = REF_AVCC;		// Use AVCC as reference
	adc_active = 1;
}

void adc_disable(void)
{
	ADCSRA = 0;			// Disable the ADC
	adc_active = 0;
}


void adc_set_ref(uint8_t val)
{
	ADMUX &= 0x3f;		// Clear reference selection bits
	ADMUX |= val;		// Set the selected reference source
}

uint16_t read_adc(uint8_t ch)	// Returns 10 bit number
{
	uint8_t low;
	uint16_t val;

	if (!adc_active)
  	adc_enable();
	if (ch > ADMAX)
  	return 0;
	ADMUX =  adc_ref | ch;			// Set channel & reference
	ADCSRA = BV(ADEN) | BV(ADSC) | ADC_SPEED;
	while ( !(ADCSRA & (1<<ADIF)) ) ;	// wait for ADC conversion
	ADCSRA |= ADIF;
	low = ADCL;
	val = ADCH;
	return (val << 8) | low;
}

