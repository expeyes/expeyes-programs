#include <avr/io.h>

uint8_t  csb = 1;          // Clock select bits
uint8_t  ocrval = 256/4;   // Output Compare register vaule


int main()
{
// Set TCCR0 in the Fast PWM mode
  TCCR0 =(1 << WGM01) | (1 << WGM00) | (1 << COM01) | csb;
  OCR0 = ocrval;
  TCNT0 = 0;
  DDRB |= (1 << PB3);    // Set PB3(OC0) as output
}
