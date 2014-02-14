#include "mh-lcd.c"
#include "mh-uart.c"

int main(void)
{
uint8_t data;

lcd_init();
uart_init(38400);

for(;;)
  {
    data = uart_recv_byte();
    lcd_put_char(data);
    uart_send_byte(data);
  }
}
