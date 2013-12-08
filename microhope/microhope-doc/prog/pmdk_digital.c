/* digital.c -- routines for manipulating the I/O pins. 

   Copyright (C) 2008 Ajith Kumar, Inter-University Accelerator Centre,
   New Delhi and Pramode C.E, GnuVision.com.

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 3, or (at your option)
   any later version.
*/

#include <avr/io.h>

struct port_pin {
    volatile uint8_t* port;
    volatile uint8_t* input_reg;
    volatile uint8_t* dir_reg;
    uint8_t pin;
};

static struct port_pin pmap[] = {{&PORTB, &PINB, &DDRB,0}, {&PORTD, &PIND, &DDRD, 0},
                                 {&PORTC, &PINC, &DDRC, 0}};
/*
 * The following functions act on pin numbers 0 ... 20 on the
 * Phoenix-MDK board. These pins are  mapped to the 
 * corresponding ports by the `translate' function.
 */

/* 
 * Pins belonging to Ports B,C and D are marked with serial numbers ranging 
 * from 0 to 20 on the PCB. This routine translates those numbers into port 
 * address and the actual pin number. Used for implementing simpler functions.
 */

static struct port_pin* translate(uint8_t pin)
{
    if (pin <= 4) {		// PB0 to PB4 are labelled from 0 to 4 
        pmap[0].pin = pin;
        return pmap;
    } else if (pin <= 12) {	// PD0 to PD7 are labelled from 5 to 12
        pmap[1].pin = pin - 5;
        return pmap + 1;
    } else if (pin <= 20) {	// PC0 to PC7 are labelled from 13 to 20
        pmap[2].pin = pin - 13;
        return pmap + 2;
    } else {
        	// Invalid pin number will select the LSB of port B.
            return pmap;
    }
}

/*
 * Set direction of pin to `input' or `output'
 */

void make_pin_input(uint8_t pin)
{
    struct port_pin *t = translate(pin);
    *(t->dir_reg) &= ~(1 << t->pin);
}

void make_pin_output(uint8_t pin)
{
    struct port_pin *t = translate(pin);
    *(t->dir_reg) |= (1 << t->pin);
}

/*
 * For a PIN configured as input, setting/clearing the corresponding bit
 * of PORTX will enable/disable the corresponding pullup resistor.
 */

void enable_pullup(uint8_t pin)
{
    struct port_pin *t = translate(pin);
    if(!(((*(t->dir_reg)) >> t->pin) & 1))
        *(t->port) |= (1 << t->pin);
}

void disable_pullup(uint8_t pin)
{
    struct port_pin *t = translate(pin);
    if(!(((*(t->dir_reg)) >> t->pin) & 1))
        *(t->port) &= ~(1 << t->pin);
}

void  set_high(uint8_t pin)
{
    struct port_pin *t = translate(pin);
    *(t->port) |= (1 << t->pin);
}

void  set_low(uint8_t pin)
{
    struct port_pin *t = translate(pin);
    *(t->port) &= ~(1 << t->pin);
}

uint8_t read_pin(uint8_t pin)
{
    struct port_pin *t = translate(pin);
    return ((*(t->input_reg)) >> (t->pin)) & 1;
}

