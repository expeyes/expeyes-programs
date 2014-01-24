#include "mh-timer.c"
#include "mh-adc.c"
#include "mh-utils.c"

uint8_t  csb = 1;         // 2 is divide by 8 option, 1MHz clock in
uint16_t  ocra = 1024/3;  // around 33% duty cycle set


int main()
{
while(1)
    {
    ocra = read_adc(0);    // 0 to 1023 output
    pwm10_tc1(csb, ocra);
    delay_ms(200);
    }
return 0;
}
