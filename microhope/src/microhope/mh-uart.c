                                                                               
/* uart.c -- routines for manipulating the ATmega16 UART.

   Copyright (C) 2008 Ajith Kumar, Inter-University Accelerator Centre,
   New Delhi and Pramode C.E, GnuVision.com.

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 3, or (at your option)
   any later version.
*/

#include <avr/io.h>

#define CPU_CLOCK	8000000		// 8 MHz clock is assumed
#define COMPUTE_BAUD(b) ((uint32_t)(CPU_CLOCK)/((uint32_t)(b)*16) - 1)


    //Initialise UART: format 8 data bits, No parity, 1 stop bit
void uart_init(uint16_t baud)
{
    UCSRB = (1 << TXEN) | (1 << RXEN);
    UBRRH = (COMPUTE_BAUD(baud) >> 8) & 0xff;
    UBRRL = (COMPUTE_BAUD(baud)) & 0xff;
    UCSRC = (1 << URSEL) | (1 << UCSZ1) | (1 << UCSZ0);
}


uint8_t uart_recv_byte(void)
{
    while( !(UCSRA & (1 <<RXC)) );
    return UDR;
}

void uart_send_byte(uint8_t c)
{
    while( !(UCSRA & (1 <<UDRE) ) );
    UDR = c;
}

