#include "mh-timer.c"
#include "mh-lcd.c"

int main()
{
uint32_t f;

lcd_init();
f = set_sqr_tc2(1500); 
lcd_put_long(f);
return 0;
}
