/* 
mh-timer.c -- Advanced functions using Timer/Counter
Author : Ajith Kumar, Inter-University Accelerator Centre, New Delhi. 
License : GNU GPL version 3 or later
Date : 23-Oct-2013
*/

#include <avr/io.h>
#include <avr/interrupt.h>

//------------------- Frequency measurement ----------------------------

#define MTIME	250 	// We count 100  on TC0

uint32_t measure_freq(void)
{ 
  DDRB &= ~(1 << PB1);              // Timer/Counter1 clock in T1 (PB1) as input
  TCCR0 = (1 << CS02) |(1 << CS00);	// Normal mode , CPU Clock / 1024 
  TIFR |= (1 << OCF0);      // Clear OCF flag for T0
  TCCR1B = (1 << CS12) | (1 << CS11) | (1 << CS10);	// External clock on T1 pin 
  TCNT0 = 0;			    // Clear TCNT0
  TCNT1 = 0;			    // Clear TCNT1
  while(TCNT0 < MTIME) ;
  TCCR1B = 0;  
  return TCNT1;
}

//----------------------- Time interval measurement--------------------------
volatile uint16_t HIWORD;
ISR(TIMER1_COMPA_vect)	// TIMER1 Compare Match A Interrupt
{
TCNT1 = 0;
++HIWORD;
PORTB = 1;
}

void start_timer()
{
/*
When TCNT1 reaches OCR1A, the ISR will run. It will clear TCNT1 and increment HIWORD.
The total time elapsed between start_timer and get_timer = HIWORD * 50000 + TCNT1
*/
 TCCR1B = (1 << CS11);   // Normal mode, with 1MHz clock
 HIWORD = 0;
 OCR1A = 50000;        
 OCR1B = 0xffff;
 TIMSK = (1 <<  OCIE1A);   // Enable compare match interrupt
 TIFR = (1 << OCF1A); 
 TCNT1 = 0;
 sei();
}

uint32_t read_timer()
{
 uint32_t x;
 
 TCCR1B = 0;    // stop TC1 clock
 x = HIWORD * 50000 + TCNT1;
 cli();
 return x;
}

