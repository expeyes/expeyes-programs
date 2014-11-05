    ; sub-routine.s  , CALL instruction

IO_DDRB = 0x17
IO_PORTB = 0x18

        .section .text    ; denotes code section

disp:  	                   ; subroutine 
        inc r1 
        out  IO_PORTB, r1      ; PORTB 
	ret

        .global main                           
main:
        ldi  r16, 255
        out  IO_DDRB,  r16   ; DDRB 
	clr  r1               
	rcall disp   ; relative call
	call disp    ; direct call
	.end
