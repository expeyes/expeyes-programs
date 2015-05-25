/* utils.c -- various utilities for microHOPE

   Copyright (C) 2008 Ajith Kumar, Inter-University Accelerator Centre,

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 3, or (at your option)
   any later version.
*/

#include <avr/io.h>


void delay_100us (uint16_t k)  	 // k* 100 usecs delay, valid only for 8MHz clock
{
  volatile uint16_t x;
  while (k--) {x=52; while (x--);}
}


void delay_ms (uint16_t k)  // idle for k milliseconds, only for 8MHz clock
    {
    volatile uint16_t x;
    while(k--) {x=532; while (x--);}
    }
    


