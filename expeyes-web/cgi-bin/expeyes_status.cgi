#!C:\Python27\python.exe
"""
CGI script for reading status of input pins of expEYES Junior connected to server
Copyright 2016,  Authors : Manoj.S.Nair(manojsnair007@gmail.com), Jishnu R(jishnu47@gmail.com), Rakesh K M(rakeshkm2203@gmail.com) [Amrita School of Engineering, Amritapuri Campus, Kollam 690525, Kerala]
License : GNU GPL version 3
"""
import sys,os,json
sys.path.insert(0,"C:\\Python27\\expeyes-3.0.0\\expeyes-3.0.0\\eyes-junior")#path to eyes-junior folder
import expeyes.eyesj as eyes
from contextlib import contextmanager
@contextmanager)# prevent header crash because of connection errors etc
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:  
            yield
        finally:
            sys.stdout = old_stdout		
			
with suppress_stdout():#open expEYES
    p=eyes.open()
	
a1 = p.get_voltage(1)#get status of A1
a2 = p.get_voltage(2)#get status of A2
in1 = p.get_voltage(3)#get status of IN1
in2 = p.get_voltage(4)#get status of IN2

data = {}#creating results
data['a1'] = float("{0:.4f}".format(a1))
data['a2'] = float("{0:.4f}".format(a2))
data['in1'] = float("{0:.4f}".format(in1))
data['in2'] = float("{0:.4f}".format(in2))
json_data = json.dumps(data)#parsing to JSON format
	
sys.stdout.write('Content-Type: application/json \r\n\r\n')#header info
sys.stdout.write(unicode('%s\r\n\r\n'%(json_data)))#print data
sys.stdout.flush()#flush buffers
