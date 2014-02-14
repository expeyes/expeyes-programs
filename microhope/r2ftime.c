#include "mh-utils.c"
#include "mh-timer.c"
#include "mh-lcd.c"

 
int main()
{
lcd_init();

set_sqr_tc2(500);    // Test signal on PD7

while(1)
   {
   lcd_clear();
   lcd_put_long(r2ftime(PB1));
   delay_ms(100);
   }
return 0;
}
