#include <avr/io.h>

        .section .text
        .global main
main:
	ldi     r16, 255
        ;out     _SFR_IO_ADDR(DDRB), r16
        out     0x17, r16

        ldi		r17, 0x0e
        ldi		r18, 0xe0
	add	r18, r17
	out	0x18, r18
fin:
	jmp fin
        .end
