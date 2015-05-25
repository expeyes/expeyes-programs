
 ; data-direct.s  , demonstrate Load Immediate mode

DDRB = 0x37
PORTB = 0x38
   
         .section .data  
var1:

         .section .text    ; denotes code section
         .global main
main: 	
          ldi  r17, 0b10101010           ; set r17 to 10101010b
          sts  var1, r17                           ; store it to RAM at var1
          ldi  r26, lo8(var1)                  ; lower byte and
          ldi  r27, hi8(var1)                  ; higher byte of the address
          ld   r16, X                                   ; data from where X is pointing to
          sts     DDRB, r16                     ; Display content of R16
          sts     PORTB, r16                  ; using LEDs on port B
       .end
