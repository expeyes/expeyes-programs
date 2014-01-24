#include "mh-lcd.c"

int main(void)
{
  uint8_t data;

  lcd_init();
  // Set UART to 38400 baud, 8 databits , 1 stopbit, No parity
  UCSRB = (1 << RXEN) | (1 << TXEN);
  UBRRH = 0;
  UBRRL = 12;	// At 8MHz (12 =>38400) (25 => 19200)
  UCSRC = (1<<URSEL) | (1<<UCSZ1) | (1<< UCSZ0); // 8,1,N

  for(;;)
     {
     while ( !(UCSRA & (1<<RXC)) );  //wait on the receiver
     data = UDR;                     // read a byte
     lcd_put_char(data);
     while ( !(UCSRA & (1<<UDRE)) ); // wait on Data Reg Empty flag
     UDR = data;
  }
}
