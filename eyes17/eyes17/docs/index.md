# Programmer's Manual 

Welcome to the Programmer's Manual for ExpEYES-17, our innovative Test and Measurement Device, which has been specially designed with students in mind. In today's educational landscape, where hands-on learning and practical skills are crucial, this manual is your gateway to exploring the fascinating world of testing and measurement with the simplicity and power of Python.


Our goal is to make learning both enjoyable and educational. With the combined power of ExpEYES and Python, you'll be able to explore a wide range of fascinating experiments and gain practical experience that will serve you well.

Let's dive in .

## Import and connect

the following two lines import the python library, and then attempt to connect to it.
the instance `p` will now be used to access all the functions of ExpEYES. It is our gateway to the device.

!!! example "Connecting to the device"
	```python
	from eyes17 import eyes
	p = eyes.open()
	```

If connected successfully, `p` will be automatically initialized. This process also uploads the unique calibration coefficients from the connected device.

```bash
In [1]: p
Out[1]: <eyes17.eyes.Interface at 0x7fef91b95120>
```

!!! warning " Failure to detect a device "
	If connection fails, `Device opening Error` will be printed, and the `p.connected` variable
	will be set to False. After properly connecting, you can either recreate `p`, or call `p.__init__()`




