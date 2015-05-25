; first.s , example assembly language program (avr-gcc)
work = 1      ; not R1     

        .equ   DDRB,   0x37
        .equ   PORTB, 0x38

         .section .data    ; the data section
var1:
         .byte 15  ; global variable var1

         .section .text  ; The code section
         .global __do_copy_data  ; initialize global variables 
         .global __do_clear_bss  ; and setup stack pointer

         .global main ;   declare label main as global
main:
         lds    work, var1           ; load R1 with var1
         sts    DDRB, work        ; PB0 as output
         sts    PORTB, work     ; set  PB0  HIGH
         .end                  
