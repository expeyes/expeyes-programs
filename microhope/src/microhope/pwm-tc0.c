#include "mh-timer.c"
#include "mh-utils.c"

uint8_t  csb = 1;       // Clock select bits
uint8_t  ocrval = 50;   // Output Compare register vaule

int main()
{
while(1) {delay_ms(100); pwm_tc0(csb, ocrval); }
return 0;
}
