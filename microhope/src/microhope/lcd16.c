// Used by phoenix.c only. Not for the microHOPE LCD

#define LCDDATA	PORTA
#define LCDCTL	PORTD
#define EN      PD2
#define RW      PD3
#define RS      PD4

#define LCDDATADIR	DDRA
#define LCDCTLDIR	DDRD
#define	LCDDATAMASK	0xf0	// for setting port Direction
#define LCDCTLMASK	0x1c


void delay (uint16_t k)	 // roughly 2 usec per loop at 8 MHz system clock
{
  volatile uint16_t x = k;
  while (x)  --x;
}

/*
(void d100us (uint16_t k)	 // 100 usecs for k = 1
{
  volatile uint16_t x = k * 47;
  while (x)  --x;
}
*/

void
commandLCD (uint8_t cmd)
{
  cbi (LCDCTL, RS);
  cbi (LCDCTL, RW);
  LCDDATA = (LCDDATA & 15) | (cmd & 0xf0);
  sbi (LCDCTL, EN);
  sbi (LCDCTL, EN);
  cbi (LCDCTL, EN);
  LCDDATA = (LCDDATA & 15) | (cmd << 4);
  sbi (LCDCTL, EN);
  sbi (LCDCTL, EN);
  cbi (LCDCTL, EN);
  delay (1000);
}

uint8_t cpos;

void
initDisplay ()
{
  LCDDATADIR |= LCDDATAMASK;
  LCDCTLDIR |= LCDCTLMASK;
  delay (1000);
  commandLCD (0x2c);		// 4 bit data mode
  delay (10000);
  commandLCD (1);			// clear display
  delay (10000);
  commandLCD (0xe);		// display ON, no cursor
  delay (10000);
  commandLCD (6);			// cursor home
  delay (10000);
  cpos = 0;
}


void
writeLCD (char c)
{
  sbi (LCDCTL, RS);
  cbi (LCDCTL, RW);
  LCDDATA = (LCDDATA & 15) | (c & 0xf0);
  sbi (LCDCTL, EN);
  sbi (LCDCTL, EN);
  cbi (LCDCTL, EN);
  LCDDATA = (LCDDATA & 15) | (c << 4);
  sbi (LCDCTL, EN);
  sbi (LCDCTL, EN);
  cbi (LCDCTL, EN);
  delay(100);

  ++cpos;
  if(cpos == 8)
    commandLCD(128+40);
}  


void write16(uint16_t i)
{
uint16_t pos = 0;

if(i/10000)
  {
  pos = 1;
  writeLCD('0' + i/10000);
  i %= 10000;
  }
  
if( (i/1000) || pos)
  {
  pos = 1;
  writeLCD('0' + i/1000);
  i %= 1000;
  }
  
if( (i/100) || pos)
  {
  pos = 1;
  writeLCD('0' + i/100);
  i %= 100;
  }
  
if( (i/10) || pos)
  {
  writeLCD('0' + i/10);
  i %= 10;
  }

writeLCD('0' + i);
}

void writeByte(uint8_t i)
{
uint8_t pos100 = 0;

if(i/100)
  {
  pos100 = 1;
  writeLCD('0' + i/100);
  i %= 100;
  }

if( (i/10) || pos100)
  {
  writeLCD('0' + i/10);
  i %= 10;
  }
writeLCD('0' + i);
}

