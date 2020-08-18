#! /usr/bin/python3
# -*- coding: utf-8 -*-
#  MicroHOPE IDE program, a wxpython text widget with File I/O,
#  Compile and Upload , undo and redo , device selection 
#  Main author:
#  Copyright 2014 Arun Jayan <arunjayan32@gmail.com>
#
#  Contributors:
#  Copyright 2014-2020 Georges Khaznadar <georgesk@debian.org>
#  Copyright 2014 Ajith Kumar <ajith@iuac.res.in>
#
#  Licence : GPL version 3
#  version : microHOPE 4.0.2

"""
###########################################################################
Features implemented :
	1. We can Compile a AVR C program using this IDE. It will generate
           a .hex file of corresponding C Program. (to compile we are
           using avr-gcc)
	2. It is Mainly designed for MicroHOPE(Micro-controllers for
           Hobby Projects and Education) .
	3. This IDE will detect 2 Board or versions of microhope hardware
           ( board using ft232 ic and  another board(latest) using Mcp220
           usb interfacing is)
	4. It can uplod programmes to microHOPE using avrdude 
	3. Undo/Redo is implemented . 
	4. A Status bar is there to view the line and column number
	5. A Toolbar is there to easy access
	6. We can also uplod Program through USBASP addon module to mcu.
	7. We can Set microhope Bootloader through USBASP.
	8. We can RESET our microhope from IDE using Soft RST option
	9. Microhope 3.0.1 also support Assembly 
###########################################################################
"""

from uhope import run

run()
