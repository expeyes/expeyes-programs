// Sinewave generator using ATtiny85. Squarewave input on pin2(PB3), output on pin3 (PB4)
// avrdude  -c dapa -p t85 -U lfuse:w:0x61:m   , to set the fuse for 64MHz Timer/Counter clock

#include <avr/io.h>
#include <avr/interrupt.h>


const uint8_t sinetab[64] = {64 , 70 , 75 , 81 , 86 , 91 , 96 , 101 , 105 , 109 , 112 , 115 , 117 , 119 , 120 , 121 , 122 , 121 , 120 , 119 , 117 , 115 , 112 , 109 , 105 , 101 , 96 , 91 , 86 , 81 , 75 , 70 , 64 , 58 , 53 , 47 , 42 , 37 , 32 , 27 , 23 , 19 , 16 , 13 , 11 , 9 , 8 , 7 , 6 , 7 , 8 , 9 , 11 , 13 , 16 , 19 , 23 , 27 , 32 , 37 , 42 , 47 , 53 , 58};


const uint8_t sinetab2[32] = {64 , 75 , 86 , 96 , 105 , 112 , 117 , 120 , 122 , 120 , 117 , 112 , 105 , 96 , 86 , 75 , 64 , 53 , 42 , 32 , 23 , 16 , 11 , 8 , 6 , 8 , 11 , 16 , 23 , 32 , 42 , 53 };

volatile uint8_t i;

ISR(PCINT0_vect)
{
OCR1B = sinetab2[(i++ & 31)];
}


int main()
{
  DDRB |= (1 << PB4);    // Set PB4(OC1B) as output
  PLLCSR = (1 << PCKE);         // Enable PLL clock source, for Timer/Counter1

  // Set Timer/Counter1 for the Fast PWM on OCR1B
  OCR1C = 128;
  TCCR1 =(1 << CS10);
  GTCCR =(1 << PWM1B) | (1 << COM1B1);
  OCR1B = 70;

  GIMSK |= (1 << PCIE);		// Enable Pin Change Interrupts
  PCMSK |= (1 << PCINT3);   // Mask to select interrupt on PB3

  sei();				 // enable interrupts
  for (;;) ;             // Infinite loop is a must to keep interrupts enabled
}






