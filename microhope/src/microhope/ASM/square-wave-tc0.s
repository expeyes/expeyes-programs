TCCR0 = 0x53
WGM01 =  3
COM00 = 4
OCR0 = 0x5C
DDRB = 0x37
PB3 =  3

        .section .text    ; denotes code section
        .global main                           
main:
	ldi   r16,  (1 << WGM01) | (1 << COM00) |  1  ; Set TCCR0 in the CTC mode
  	 sts  TCCR0 , r16
         ldi   r16, 250
         sts  OCR0, r16
         ldi    r16, (1 <<  PB3)         
         sts   DDRB, r16
	.end
