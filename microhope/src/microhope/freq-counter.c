#include "mh-utils.c"
#include "mh-timer.c"
#include "mh-lcd.c"

// Connect input to PB1, test frequency available on PD7

int main()
{
uint32_t f;

set_sqr_tc2(1500);    // Set a square wave on TC2 output (PD7)
lcd_init();
while(1)
   {
   f = measure_freq();   // Measures on T1 (PB1)
   lcd_clear();
   lcd_put_long(f);
   delay_ms(200);
   }
return 0;
}
