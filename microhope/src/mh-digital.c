/* mh-digital.c -- routines for manipulating the I/O pins. 

   Copyright (C) 2008 Ajith Kumar, Inter-University Accelerator Centre,

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 3, or (at your option)
   any later version.
*/

#include <avr/io.h>


// Macro to calculate the binary value of a bit (specify 0 to 7)
#ifndef BITVAL
  #define BITVAL(bit)  (1 << (bit))
#endif

// Macro to clear a bit (specify 0 to 7)
#ifndef CLRBIT
	#define CLRBIT(sfr, bit) (_SFR_BYTE(sfr) &= ~BITVAL(bit))
#endif

// Macro to set a bit (specify 0 to 7)
#ifndef SETBIT
  #define SETBIT(sfr, bit) (_SFR_BYTE(sfr) |= BITVAL(bit))
#endif

// Macro to read a bit (specify 0 to 7)
#ifndef GETBIT
	#define GETBIT(sfr, bit) (_SFR_BYTE(sfr) & BITVAL(bit))
#endif
