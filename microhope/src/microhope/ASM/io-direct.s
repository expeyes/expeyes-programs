; program io-direct.s to demonstrate direct I/O addressing

     .section .text    ; denotes code section         
     .global main                           
main: 	
      clr    r1
      inc	r1         ; R1 now contains 1
      out    0x17, r1   ; using I/O address, DDRB and
      out    0x18, r1   ; PORTB. LED should glow
      .end
