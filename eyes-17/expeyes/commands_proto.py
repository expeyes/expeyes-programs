import math,sys,time, struct

# allows to pack numeric values into byte strings
Byte =     struct.Struct("B") # size 1
ShortInt = struct.Struct("H") # size 2
Integer=   struct.Struct("I") # size 4

ACKNOWLEDGE = Byte.pack(254)
MAX_SAMPLES = 10000
DATA_SPLITTING = 200

#/*----flash memory----*/
FLASH =Byte.pack(1)
READ_FLASH       = Byte.pack(1)
WRITE_FLASH      = Byte.pack(2)
WRITE_BULK_FLASH = Byte.pack(3)
READ_BULK_FLASH  = Byte.pack(4)

#/*-----ADC------*/
ADC                 = Byte.pack(2)
CAPTURE_ONE         = Byte.pack(1)
CAPTURE_TWO         = Byte.pack(2)
CAPTURE_DMASPEED    = Byte.pack(3)
CAPTURE_FOUR        = Byte.pack(4)
CONFIGURE_TRIGGER   = Byte.pack(5)
GET_CAPTURE_STATUS  = Byte.pack(6)
GET_CAPTURE_CHANNEL = Byte.pack(7)
SET_PGA_GAIN        = Byte.pack(8)
GET_VOLTAGE         = Byte.pack(9)
GET_VOLTAGE_SUMMED  = Byte.pack(10)
START_ADC_STREAMING = Byte.pack(11)
SELECT_PGA_CHANNEL  = Byte.pack(12)
CAPTURE_12BIT       = Byte.pack(13)
CAPTURE_12BIT_SCAN  = Byte.pack(14)
SET_HI_CAPTURE      = Byte.pack(15)
SET_LO_CAPTURE      = Byte.pack(16)

MULTIPOINT_CAPACITANCE= Byte.pack(20)
SET_CAP				= Byte.pack(21)
PULSE_CAPTURE		= Byte.pack(22)

#/*------I2C-------*/
I2C_HEADER       = Byte.pack(4)
I2C_START        = Byte.pack(1)
I2C_SEND         = Byte.pack(2)
I2C_STOP         = Byte.pack(3)
I2C_RESTART      = Byte.pack(4)
I2C_READ_END     = Byte.pack(5)
I2C_READ_MORE    = Byte.pack(6)
I2C_WAIT         = Byte.pack(7)
I2C_SEND_BURST   = Byte.pack(8)
I2C_CONFIG       = Byte.pack(9)
I2C_STATUS       = Byte.pack(10)
I2C_READ_BULK    = Byte.pack(11)
I2C_WRITE_BULK   = Byte.pack(12)
I2C_ENABLE_SMBUS = Byte.pack(13)
I2C_INIT         = Byte.pack(14)
I2C_PULLDOWN_SCL = Byte.pack(15)
I2C_DISABLE_SMBUS= Byte.pack(16)
I2C_START_SCOPE  = Byte.pack(17)


#/*-----------DAC--------*/
DAC                = Byte.pack(6)
SET_DAC            = Byte.pack(1)


#/*--------WAVEGEN-----*/
WAVEGEN              = Byte.pack(7)
SET_WG               = Byte.pack(1)
SET_SQR1             = Byte.pack(3)
SET_SQR_LONG         = Byte.pack(4)
SET_SINE1            = Byte.pack(13)

LOAD_WAVEFORM1       = Byte.pack(15)
SET_SINE_AMP         = Byte.pack(16)

#/*-----digital outputs----*/
DOUT      = Byte.pack(8)
SET_STATE = Byte.pack(1)

#/*-----digital inputs-----*/
DIN        = Byte.pack(9)
GET_STATES  = Byte.pack(1)


ID1	   = Byte.pack(0)
ID2        = Byte.pack(1)
ID3        = Byte.pack(2)
ID4        = Byte.pack(3)
LMETER     = Byte.pack(4)


#/*------TIMING FUNCTIONS-----*/
TIMING                      = Byte.pack(10)
GET_TIMING                  = Byte.pack(1)
GET_PULSE_TIME              = Byte.pack(2)
GET_DUTY_CYCLE              = Byte.pack(3)
FETCH_DMA_DATA              = Byte.pack(7)
FETCH_INT_DMA_DATA          = Byte.pack(8)
FETCH_LONG_DMA_DATA         = Byte.pack(9)
GET_INITIAL_DIGITAL_STATES  = Byte.pack(11)

TIMING_MEASUREMENTS         = Byte.pack(12)
INTERVAL_MEASUREMENTS       = Byte.pack(13)
SINGLE_PIN_EDGES            = Byte.pack(14)
DOUBLE_PIN_EDGES            = Byte.pack(15)
#/*--------MISCELLANEOUS------*/
COMMON                = Byte.pack(11)

GET_CTMU_VOLTAGE      = Byte.pack(1)
GET_CAPACITANCE       = Byte.pack(2)
GET_FREQUENCY         = Byte.pack(3)
GET_INDUCTANCE        = Byte.pack(4)

GET_VERSION           = Byte.pack(5)

RETRIEVE_BUFFER       = Byte.pack(8)
GET_HIGH_FREQUENCY    = Byte.pack(9)
CLEAR_BUFFER          = Byte.pack(10)
SET_RGB1		      = Byte.pack(11)
READ_PROGRAM_ADDRESS  = Byte.pack(12)
WRITE_PROGRAM_ADDRESS = Byte.pack(13)
READ_DATA_ADDRESS     = Byte.pack(14)
WRITE_DATA_ADDRESS    = Byte.pack(15)

GET_CAP_RANGE	      = Byte.pack(16)
SET_RGB2		      = Byte.pack(17)
READ_LOG              = Byte.pack(18)
RESTORE_STANDALONE    = Byte.pack(19)
GET_ALTERNATE_HIGH_FREQUENCY = Byte.pack(20)
SET_RGB3		      = Byte.pack(22)

START_CTMU		      = Byte.pack(23)
STOP_CTMU		      = Byte.pack(24)

START_COUNTING		  = Byte.pack(25)
FETCH_COUNT  		  = Byte.pack(26)
FILL_BUFFER           = Byte.pack(27)
HCSR04           	  = Byte.pack(28)
HX711                 = Byte.pack(29)


#/*---------- BAUDRATE for main comm channel----*/
SETBAUD     = Byte.pack(12)
BAUD115200  = Byte.pack(round(((64e6/115200)/4))-1)
BAUD230400  = Byte.pack(round(((64e6/230400)/4))-1)
BAUD500000  = Byte.pack(round(((64e6/500000)/4))-1)
BAUD1000000 = Byte.pack(round(((64)/4))-1)



#/*------INPUT CAPTURE---------*/
#capture modes
EVERY_SIXTEENTH_RISING_EDGE = Byte.pack(0b101)
EVERY_FOURTH_RISING_EDGE    = Byte.pack(0b100)
EVERY_RISING_EDGE           = Byte.pack(0b011)
EVERY_FALLING_EDGE          = Byte.pack(0b010)
EVERY_EDGE                  = Byte.pack(0b001)
DISABLED		    = Byte.pack(0b000)

##########commands from old ExpEYES
# Commands with Two bytes argument (81 to 120)
R2RTIME     =   81  # Time from rising edge to rising edge,arguments pin1 & pin2
R2FTIME     =   82      
F2RTIME     =   83      
F2FTIME     =   84      
MULTIR2R    =   85  # Time between rising edges, arguments pin & skipcycles    
SET2RTIME   =   86  # From a Dout transition to the Din transition
SET2FTIME   =   87  #
CLR2RTIME   =   88  #   
CLR2FTIME   =   89  #    
HTPUL2RTIME =   90  # High True Pulse to HIGH
HTPUL2FTIME =   91  # High True Pulse to LOW
LTPUL2RTIME =   92  #
LTPUL2FTIME =   93  #


#/*--------Chip selects-----------*/
CSA1 = Byte.pack(1)
CSA2 = Byte.pack(2)
CSA3 = Byte.pack(3)
CSA4 = Byte.pack(4)
CSA5 = Byte.pack(5)
CS1  = Byte.pack(6)
CS2  = Byte.pack(7)

#resolutions
TEN_BIT    = Byte.pack(10)
TWELVE_BIT = Byte.pack(12)


def applySIPrefix(value, unit='',precision=2 ):
		neg = False
		if value < 0.:
			value *= -1; neg = True
		elif value == 0.:  return '0 '  # mantissa & exponnt both 0
		exponent = int(math.log10(value))
		if exponent > 0:
			exponent = (exponent // 3) * 3
		else:
			exponent = (-1*exponent + 3) // 3 * (-3)

		value *= (10 ** (-exponent) )
		if value >= 1000.:
			value /= 1000.0
			exponent += 3
		if neg:
			value *= -1
		exponent = int(exponent)
		PREFIXES = "yzafpnum kMGTPEZY"
		prefix_levels = (len(PREFIXES) - 1) // 2
		si_level = exponent // 3
		if abs(si_level) > prefix_levels:
			raise ValueError("Exponent out range of available prefixes.")
		return '%.*f %s%s' % (precision, value,PREFIXES[si_level + prefix_levels],unit)


