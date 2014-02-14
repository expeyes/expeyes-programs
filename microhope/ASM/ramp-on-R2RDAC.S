#include <avr/io.h>

     .section .text   
     .global main                           
main: 	
     ldi   r16, 255
     sts  DDRB, r16       ; all bits of DDRB set
loop:  
      inc	r1                 
      sts PORTB, r1   ; R1 to PORTB. LEDs
      rjmp loop
      .end
