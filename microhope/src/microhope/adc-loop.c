// Reads ADC channel 0 and diplays the result on the LCD 

#include "mh-lcd.c"
#include "mh-adc.c"
#include "mh-utils.c"

main()
{
uint16_t data;

lcd_init();
adc_enable();
while(1)
    {
    data = read_adc(0);   // Read voltage at PA0
    lcd_clear();
    lcd_put_int(data);
    delay_ms(500);
    }
}
