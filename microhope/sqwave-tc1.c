#include "mh-timer.c"

uint8_t  csb = 2;       // 2 is divide by 8 option, 1MHz clock in
uint16_t  ocra = 50000;  // Output Compare register A

// 10Hz squarewave on OC1A will be generated
 
int main()
{
sqwave_tc1(csb, ocra); 
return 0;
}
