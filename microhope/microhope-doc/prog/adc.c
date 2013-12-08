// Reads ADC channel 0 and diplays the result on the LCD 

#include "pmdk_lcd.c"
#include "pmdk_adc.c"

main()
{
uint16_t data;

lcd_init();
adc_enable();
data = read_adc(0);
lcd_put_int(data);
}

