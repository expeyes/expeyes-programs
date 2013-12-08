#include "pmdk_adc.c"
#include "pmdk_uart.c"
#include "pmdk_lcd.c"

#include <stdio.h>

int main()
{
uint16_t data;
char   ss[10], *p;

lcd_init();
adc_enable();
uart_init(38400);

data = read_adc(0);
sprintf(ss,"%5d",data);
lcd_put_string(ss);
p = ss;
while (*p++) uart_send_byte(*p);
}

