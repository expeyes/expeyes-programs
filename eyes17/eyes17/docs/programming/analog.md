
## :material-flash-triangle: get_voltage : Measure voltage 

Reads voltage from specified channel , and returns the value.


Autorange is enabled for this function, and it automatically selects the appropriate voltage range if either A1, or A2 are specified

|parameter      |  description  |
|---------      | -------       |
|Channel|   Analog input to measure. A1,A2,A3, MIC, SEN, or IN1  |
|return| Voltage from chosen input |

!!! tip "x = p.get_voltage('A1')"
	```python
	import eyes17.eyes
	p = eyes17.eyes.open()

	print ('Voltage between A1 and GND = ',p.get_voltage('A1'))
	print (p.get_voltage('A2'))
	print (p.get_voltage('A3'))

	```


<hr>


## capture1 : Single Channel Oscilloscope

Blocking call that fetches oscilloscope traces from any analog input `A1,A2,A3, MIC, SEN, or IN1`

|parameter      |  description  |
|---------      | -------       |
|Channel|   Analog input to measure. A1,A2,A3, MIC, SEN, or IN1  |
|ns             | Number of samples to fetch. Maximum 2500|
|tg            |  Timegap between samples in microseconds. Minimum 1.75uS|
| <hr> |
|return| Arrays X(timestamps),Y(Voltages from chosen input)|

???+ tip "x,y = p.capture1('A1',500,10)"
	```python
	import eyes17.eyes
	p = eyes17.eyes.open()

	from matplotlib import pyplot as plt
	x,y = p.capture1('A1',500,10)
	plot(x,y)
	show()

	```


<hr>


## capture_action : Single Channel Oscilloscope with digital state control

Blocking call that records and returns an oscilloscope trace from the specified input channel after executing another command
such as SET_LOW,SET_HIGH,FIRE_PULSE etc on SQ1

|parameter      |  description  |
|---------      | -------       |
|Channel|   Analog input to measure. A1,A2,A3, MIC, SEN, or IN1  |
|ns             | Number of samples to fetch. Maximum 2500|
|tg            |  Timegap between samples in microseconds. Minimum 1.75uS|
| \*args | SET_LOW    : set OD1 low before capture |
|        | SET_HIGH   : set OD1 high before capture |
|        | FIRE_PULSE : make a high pulse on OD1 before capture. |
|        | Use keyword argument pulse_width = x,where x = width of the pulse in uS. default width =10uS |
|        | Use keyword argument pulse_type = 'high_true' or 'low_true' to decide type of pulse |
|        | x,y = p.capture_action('A1',2000,1,'FIRE_PULSE',interval = 250) #Output 250uS pulse on OD1 before starting acquisition |
|        | SET_STATE  : change Digital output immediately after capture starts.|
|        | Use keyword arguments that will be forwarded to the set_state command |
| <hr> |
|return| Arrays X(timestamps in mS),Y(Voltages from chosen input)|

??? tip "x,y = p.capture_action('A1',500,10, 'SET_LOW')"
	```python
	import eyes17.eyes
	p = eyes17.eyes.open()

	from matplotlib import pyplot as plt
	x,y = p.capture_action('A1',2000,1,'SET_LOW') #set OD1 LOW before starting acquisition
	plot(x,y)
	show()

	```

??? code " RL Transient Experiment "
	```python
	import eyes17.eyes
	p = eyes17.eyes.open()

	from matplotlib import pyplot as plt
	import time


	plt.plot([0,.5], [0,0], color='black')
	plt.ylim([-5,5])


	p.set_state(OD1=1)			# OD1 to HIGH
	time.sleep(.5)
	t,v = p.capture_action('A1', 100, 5, 'SET_LOW')

	plt.plot(t,v,linewidth = 2, color = 'red')
	plt.show()

	```

??? code " RC Transient Experiment "
	```python
	import eyes17.eyes
	p = eyes17.eyes.open()
	from matplotlib import pyplot as plt
	import time

	p.set_state(OD1=0)			# OD1 to LOW
	time.sleep(.5)
	t,v = p.capture_action('A1', 100, 5, 'SET_HIGH')
	plt.plot(t,v,linewidth = 2, color = 'blue')

	p.set_state(OD1=1)			# OD1 to LOW
	time.sleep(.5)
	t,v = p.capture_action('A1', 100, 5, 'SET_LOW')

	plt.plot(t,v,linewidth = 2, color = 'red')
	plt.show()

	```

<hr>


## capture2 : 2 Channel Oscilloscope

Blocking call that fetches oscilloscope traces from A1,A2,A3,MIC .

|parameter      |  description  |
|---------      | -------       |
|ns             | Number of samples to fetch. Maximum 2500|
|tg            |  Timegap between samples in microseconds. Minimum 1.75uS|
|TraceOneRemap|   Analog input for channel 1. It is connected to A1 by default.Channel 2-4 always reads CH2-MIC|
| <hr> |
|return| Arrays X1(timestamps in mS),Y1(Voltage at A1),X2(timestamps in mS),Y2(Voltage at A2),X3(timestamps in mS)|

??? tip "t,v1,t2,v2 = p.capture2(1000,2)"
	```python
	import eyes17.eyes
	p = eyes17.eyes.open()

	from matplotlib import pyplot as plt

	p.set_sine(200)

	t,v, tt,vv = p.capture2(500, 20)   # captures A1 and A2

	xlabel('Time(mS)')
	ylabel('Voltage(V)')
	plot([0,10], [0,0], 'black')
	ylim([-4,4])

	plot(t,v,linewidth = 2, color = 'blue')
	plot(tt, vv, linewidth = 2, color = 'red')

	show()

	```

<hr>



## capture4 : 4 Channel Oscilloscope

Blocking call that fetches oscilloscope traces from A1,A2,A3,MIC .

|parameter      |  description  |
|---------      | -------       |
|ns             | Number of samples to fetch. Maximum 2500|
|tg            |  Timegap between samples in microseconds. Minimum 1.75uS|
|TraceOneRemap|   Analog input for channel 1. It is connected to A1 by default.Channel 2-4 always reads CH2-MIC|
| <hr> |
|return| Arrays X1(timestamps in mS),Y1(Voltage at A1),X2(timestamps in mS),Y2(Voltage at A2),X3(timestamps in mS),Y3(Voltage at A3),X4(timestamps in mS),Y4(Voltage at MIC)|

??? tip " t,v1,v2,v3,v4 = p.capture4(1000,2)"
	```python
	from matplotlib import pyplot as plt
	I=eyes17.Interface()
	x,y1,y2,y3,y4 = I.capture4(800,1.75)
	plot(x,y1)
	plot(x,y2)
	plot(x,y3)
	plot(x,y4)
	show()
	```

<hr>














