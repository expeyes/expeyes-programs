// Reads ADC channel 0 and diplays the result on the LCD 

#include "mh-lcd.c"
#include "mh-adc.c"
#include "mh-utils.c"

main()
{
uint16_t data;
uint16_t v100c =  800;          // ADC output when temp is 100 degree C
DDRB = 1;        				// PB0 as output

lcd_init();
adc_enable();
adc_set_ref(REF_INT);
while(1)
    {
    data = read_adc(0);   				// Read voltage at PA0
    if (data > v100c) 
	PORTB = 0;              // switch ON heater control
    else if (data < (v100c - 10))     // window of 10
	PORTB = 1;              // switch OFF hrater control
    lcd_clear();
    lcd_put_int(data);
    delay_ms(500);
    }
}
