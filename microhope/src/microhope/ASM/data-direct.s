
 ; data-direct.s  , demonstrate data direct mode

DDRB = 0x37
PORTB = 0x38
   
         .section .data  
var1:

         .section .text    ; denotes code section
         .global main
main: 	
       ldi      r17, 0xf0             ; load r16 with 255
       sts	   var1, r17           ; store r17 to location var1 
       lds    r16, var1            ; content of RAM at var1 to r16
       out 0x17, r16             ; Display content of R16
       out 0x18, r16             ; using LEDs on port B
       sts     DDRB, r16        ; Do the same again using 
       sts     PORTB, r16     ;  memory mapped addresses
       .end
