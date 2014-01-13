// Reads ADC channel 0 and diplays the result on the LCD 

#include "mh-lcd.c"
#include "mh-adc.c"

disp_mv_as_v(uint16_t mv)
{
uint16_t j, k = mv % 1000;
j = mv/1000;
lcd_put_int(j);
lcd_put_char('.');
lcd_put_int(k);
}

main()
{
uint16_t data, k;
double v;
char  ss[10];

lcd_init();
adc_enable();
data = read_adc(0);
data = 300;          // this is for testing only, 1.466 volt
v = 5.0 * data/1023;
k = (int) (v*1000);
disp_mv_as_v(k);
}
