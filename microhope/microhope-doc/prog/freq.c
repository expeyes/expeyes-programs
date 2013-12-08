#include "pmdk_timer.c"
#include "pmdk_adc.c"
#include "pmdk_lcd.c"

int main()
{
uint16_t fr;

lcd_init();
set_frequency(500); 	// Generate square wave on PD7 (OC2)
fr = measure_frequency();
lcd_put_int(fr);
}
