#!/usr/bin/python
"""
CGI script for setting status for output pins of expEYES Junior connected to server
Copyright 2016,  Authors : , Jishnu R(jishnu47@gmail.com), Rakesh K M(rakeshkm2203@gmail.com), Manoj.S.Nair(manojsnair007@gmail.com) [Amrita School of Engineering, Amritapuri Campus, Kollam 690525, Kerala]
License : GNU GPL version 3
"""
import sys,os,cgi

import expeyes.eyesj as eyes
from contextlib import contextmanager

form= cgi.FieldStorage()#get submitted form

sys.stdout.write('Content-type: text/html \r\n\r\n')#html header

pvs = float(form.getvalue("pvs"))#get input values from get/post method
od1 = int(form.getvalue("od1"))#get input values from get/post method
sqr1 = int(form.getvalue("sqr1"))#get input values from get/post method
sqr2 = int(form.getvalue("sqr2"))#get input values from get/post method

@contextmanager
def suppress_stdout():# prevent header crash because of connection errors etc.
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:  
            yield
        finally:
            sys.stdout = old_stdout		
			
with suppress_stdout():
    p=eyes.open()
	
p.set_state(10,od1)#set OD1
p.set_voltage(pvs)#set PVS
p.set_sqr1(sqr1)#set SQR1
p.set_sqr2(sqr2)#set SQR2

sys.stdout.write(unicode('%s\r\n\r\n'%("Outputs are set")))#return on success execution
sys.stdout.flush()#flush buffers
