  ;  test.s , a single instruction program. Examine the .lst file
        .section .text    ; denotes code section

        .global main                           
main:
	clr r16   ; just one instruction
	.end
