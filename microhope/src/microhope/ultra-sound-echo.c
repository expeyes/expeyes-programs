#include "mh-utils.c"
#include "mh-timer.c"
#include "mh-lcd.c"

int vsby2 = 17;  // velocity of sound = 34 mS/cm
int main()
{
uint32_t x;

DDRB |=  (1 << PB0);  // set PB0 as output
DDRB &= ~(1 << PB1);  // and PB1 as inpt
lcd_init();

while(1)
   {
   PORTB |=  (1 << PB0);  // set PB0 HIGH
   delay_100us(1);
   PORTB &=  ~(1 << PB0);  // set PB0 LOW
   delay_100us(5);
   start_timer();
   while( (PINB & 2) != 0 ) ;   // Wait for LOW on PB1
   x = read_timer() + 400;
   lcd_clear();
   lcd_put_long(x*vsby2/1000);  // distance in cm
   delay_ms(500);
   }
return 0;
}
