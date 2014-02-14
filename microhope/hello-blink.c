#include "mh-lcd.c"
#include "mh-utils.c"
int main()
{
lcd_init();
for(;;)
	{
	lcd_put_string("Hello World..");
        delay_ms(300);
	lcd_clear();
        delay_ms(300);
        }
}
