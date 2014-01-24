#include "mh-timer.c"

uint8_t csb = 2;       // Clock select bits
uint8_t ocrval = 99;   // Output Compare register vaule

int main()
{
sqwave_tc0(csb, ocrval);
return 0;
}
