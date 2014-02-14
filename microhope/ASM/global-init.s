
 ; global-init.s  , demonstrate

DDRB = 0x37
PORTB = 0x38
   
         .section .data  
var1:  
        .byte  0xee

         .section .text    ; denotes code section
         .global __do_copy_data  ; initialize global variables 
         .global __do_clear_bss  ; and setup stack pointer
         .global main
main: 	
       lds    r16, var1            ; content of RAM at var1 to r16
       sts     DDRB, r16        ; Do the same again using 
       sts     PORTB, r16     ;  memory mapped addresses
       .end
