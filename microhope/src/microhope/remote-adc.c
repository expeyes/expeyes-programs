#include "mh-lcd.c"
#include "mh-uart.c"
#include "mh-adc.c"

int main(void)
{
uint8_t chan, low, hi;
uint16_t adcval;

lcd_init();
uart_init(38400);
adc_enable();

for(;;)
  {
    chan = uart_recv_byte();
    if (chan <=7)
        {
        adcval = read_adc(chan);
	lcd_clear();
        lcd_put_int(low);
        low = adcval & 255;
        hi = adcval >> 8;
        uart_send_byte(low);       // send LOW byte
        uart_send_byte(hi);        // send HI byte
        }
  }
}
