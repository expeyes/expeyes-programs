#include "mh-timer2.c"
#include "mh-lcd.c"
#include "mh-utils.c"

 
int main()
{
uint32_t x;

DDRB = 1;

lcd_init();
start_timer();
delay_ms(950);
x = read_timer();
lcd_put_long(x);
return 0;
}
