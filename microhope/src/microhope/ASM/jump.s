    ; jump.s  ,  demonstrates JUMP instruction

IO_DDRB = 0x17
IO_PORTB = 0x18

        .section .text   

        .global main                           
main:
        ldi  r16, 255
        out  IO_DDRB,  r16   ; DDRB 
	jmp lab1
        ldi r16, 15               ; load 15 ro r16
lab1:
        out IO_PORTB, r16    ; r16 to PortB
	.end
