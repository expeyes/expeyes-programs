 ; immed.s  , demonstrate Load Immediate mode

          .section .text    ; denotes code section
          .global main
main:
     ldi r16, 255      ; load r16 with 255
     out 0x17, r16  ; Display content of R16
     out 0x18, r16  ; using LEDs on port B
     .end
