
/* lcd.c -- routines for handling a text mode LCD display

   Copyright (C) 2008 Ajith Kumar, Inter-University Accelerator Centre,
   New Delhi and Pramode C.E, GnuVision.com.

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 3, or (at your option)
   any later version.
*/

#include <avr/io.h>
#include <stdint.h>

// LCD control bits of Port C on Phoenix MDK. Refer to the Schematic
#define ENBIT 0x8  	
#define RWBIT 0x4  
#define RSBIT 0x2  

void delay(uint16_t k)
{
    volatile uint16_t x = k;
    while(x)
        --x;
}


uint8_t cpos = 0;		// LCD cursor position

void lcd_command (uint8_t cmd)
{
	PORTC &= 1;				// Clear bits used by LCD
	PORTC |= (cmd & 0xF0);			// Put 4 MSBs, RS, RW & EN Low
	PORTC |= ENBIT;  PORTC &= ~ENBIT;	// Pulse on EN pin
	PORTC &= 1;
	PORTC |= (cmd << 4);			// Put 4 LSBs 
	PORTC |= ENBIT;  PORTC &= ~ENBIT;	// Pulse on EN pin
	delay (10000);
}


void lcd_init (void)  // This needs rewriting
{
	delay(10000);
	DDRC |= 254;			// Except PC0 all are outputs
	lcd_command (32 + 8 + 4);	// 4 bit data mode
	lcd_command (4 + 2);		// Entry mode
	lcd_command (8 + 4);		// display ON, no cursor
	lcd_command (1);		// Clear
	cpos = 0;			// Set cursor position variable
	delay(10000);
	DDRC |= 254;			// Except PC0 all are outputs
	lcd_command (32 + 8 + 4);	// 4 bit data mode
	lcd_command (4 + 2);		// Entry mode
	lcd_command (8 + 4);		// display ON, no cursor
	lcd_command (1);		// Clear
	cpos = 0;			// Set cursor position variable
}


void lcd_clear (void)
{
	lcd_command(1);
}


void lcd_put_char (char c)
{
	PORTC &= 1;				// Clear bits used by LCD
	PORTC |= RSBIT | (c & 0xF0);		// Put 4 MSBs, RS High, RW & EN Low
	PORTC |= ENBIT;  PORTC &= ~ENBIT;	// Pulse on EN pin
	PORTC &= 1;
	PORTC |= RSBIT | (c << 4);		// Put 4 LSBs 
	PORTC |= ENBIT;  PORTC &= ~ENBIT;	// Pulse on EN pin
	delay(1000);
	++cpos;  if(cpos == 8) 
		lcd_command(128 + 32 + 8);	// 1 x 16 display
}  


void lcd_put_string(char *p)
{
	while(*p) {
		lcd_put_char(*p);
		++p;
	}
}

void lcd_put_byte(uint8_t i)
{
	uint8_t pos100 = 0;

	if(i/100) {
		pos100 = 1;
		lcd_put_char('0' + i/100);
		i %= 100;
	}

	if( (i/10) || pos100) {
		lcd_put_char('0' + i/10);
		i %= 10;
	}
	lcd_put_char('0' + i);
}

void lcd_put_int(uint16_t val)
{
	char 	ss[8];
	uint8_t	k;

	if(val ==0) {
		lcd_put_char('0');
		return;
	}

	k = 0;
	while(val > 0) {
		ss[k++] = '0' + (val % 10);
		val /= 10;
	}
	while(k) {
		lcd_put_char(ss[k-1]);
		--k;
	}
}

void lcd_put_long(uint32_t val)
{
	char 	ss[8];
	uint8_t	k;

	if(val ==0) {
		lcd_put_char('0');
		return;
	}

	k = 0;
	while(val > 0) {
		ss[k++] = '0' + (val % 10);
		val /= 10;
	}
	while(k) {
		lcd_put_char(ss[k-1]);
		--k;
	}
}

