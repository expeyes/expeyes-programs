/*
Sinewave generator using ATtiny85. Squarewave input on pin2(PB3), output on pin3 (PB4). Every level change on pin2
triggers the interrupt and the PWM value is changed by sending the next value from the sine table to OCRB1.
Frequency of sinewave is input frequency divided by 32, sinetable has 64 values.
avrdude  -c dapa -p t85 -U lfuse:w:0x61:m   , to set the fuse for 64MHz Timer/Counter clock
*/

#include <avr/io.h>
#include <avr/interrupt.h>

    .section .data
    .global stab

stab:	; sine table
	.byte 64 , 70 , 75 , 81 , 86 , 91 , 96 , 101 , 105 , 109 , 112 , 115 , 117 , 119 , 120 , 121 , 122 , 121 , 120 , 119 , 117 , 115 , 112 , 109 , 105 , 101 , 96 , 91 , 86 , 81 , 75 , 70 , 64 , 58 , 53 , 47 , 42 , 37 , 32 , 27 , 23 , 19 , 16 , 13 , 11 , 9 , 8 , 7 , 6 , 7 , 8 , 9 , 11 , 13 , 16 , 19 , 23 , 27 , 32 , 37 , 42 , 47 , 53 , 58

indx:
	.byte 0

    .section .text
    .global __do_copy_data
	.global __do_clear_bss


	.global PCINT0_vect
PCINT0_vect:
	ld  r24, X+							; get current value from the sine table, increment pointer
    out     _SFR_IO_ADDR(OCR1B), r24	; write it to OCR1B
	inc	r22								; increment r22
	CPSE	r20,r22						; is it 64 ?
	reti								; if not return, else skip reti
	clr	r22								; set it bck to 0
	subi	r26,64						; set X to beginning of table
	reti

        .global main
main:
	sbi     _SFR_IO_ADDR(DDRB), 4

	ldi     r24, (1 << PCKE)
	out     _SFR_IO_ADDR(PLLCSR), r24

	ldi		r24, 128;
    out     _SFR_IO_ADDR(OCR1C), r24

	ldi		r24, 50;
    out     _SFR_IO_ADDR(OCR1B), r24

	ldi		r24, (1 << CS10)
    out     _SFR_IO_ADDR(TCCR1), r24

    ldi	r24, (1 << PWM1B) | (1 << COM1B1);
    out     _SFR_IO_ADDR(GTCCR), r24

	ldi	r24, (1 << PCIE)			; Enable Pin Change Interrupts
    out     _SFR_IO_ADDR(GIMSK), r24

	ldi	r24, (1 << PCINT3)		; Mask to select interrupt on PB3
    out     _SFR_IO_ADDR(PCMSK), r24

	ldi		XL, lo8(stab)      ; point X to the sine table
	ldi		XH, hi8(stab)
	clr		r22					; clear r22
	ldi		r20,64

	sei
fin:
	rjmp fin

    .end


