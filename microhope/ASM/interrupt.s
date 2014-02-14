        .section .data    ; data section starts here
        .section .text    ; denotes code section

	.global __vector_1 ; INT0_vect
__vector_1:
	inc r1
	out 0x18, r1
	reti
	
        .global main                           
main:
	ldi  r16, 255
	out  0x17, r16   ; DDRB
	out  0x12, r16   ; Port D pullup
	ldi  r16, 0x40   ; enable INT0
	out  0x3b, r16
	clr r1   
	sei
loop:	rjmp loop
	.end
