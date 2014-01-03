'''
expEYES data analysis library using numpy and scipy
Author  : Ajith Kumar B.P, bpajith@gmail.com
License : GNU GPL version 3
'''

import sys, time, math
from numpy import *
import numpy.fft
from scipy import optimize 
from scipy.optimize import leastsq


def find_peak(va):
	vmax = 0.0
	size = len(va)
	index = 0
	for i in range(1,size):		# skip first 2 channels, DC
		if va[i] > vmax:
			vmax = va[i]
			index = i
	return index

#-------------------------- Fourier Transform ------------------------------------
def fft(ya, si):
	'''
	Returns positive half of the Fourier transform of the signal ya. 
	Sampling interval 'si', in milliseconds
	'''
	np = len(ya)
	if np %2 == 1:  # odd values of np give exceptions
		np=np-1 # make it even
		ya=ya[:-1]
	v = array(ya)
	tr = abs(numpy.fft.fft(v))/np
	frq = numpy.fft.fftfreq(np, si * 1.0e-3)
	x = frq.reshape(2,np/2)
	y = tr.reshape(2,np/2)
	return x[0], y[0]    

def find_frequency(x,y):		# Returns the fundamental frequency using FFT
	tx,ty = fft(y, x[1]-x[0])
	index = find_peak(ty)
	if index == 0:
		return None
	else:
		return tx[index]
	'''
	m = mean(ty)
	mx = max(ty)
	for i in range(1,len(ty)):
		if ty[i] != 0:
			print 'FF', tx[i], ty[i]
		if ty[i] > 5*m:
			return tx[i]
	return None					# Could not find FFT Peak
	'''
#-------------------------- Sine Fit ------------------------------------------------
def sine_erf(p,y,x):					
	return y - p[0] * sin(2*pi*p[1]*x+p[2])+p[3]

def sine_eval(x,p):			# y = a * sin(2*pi*f*x + phi)+ offset
	return p[0] * sin(2*pi*p[1]*x+p[2])-p[3]

def fit_sine(xlist,ylist, freq = 0):	# Time in mS, V in volts, freq in Hz
	size = len(xlist)
	xa = array(xlist, dtype=float)
	ya = array(ylist, dtype=float)
	amp = (max(ya)-min(ya))/2
	if freq == 0:						# Guess frequency not given
		freq = find_frequency(xa,ya)
	if freq == None:
		return None
	#print 'guess a & freq = ', amp, freq
	par = [abs(amp), freq*0.001, 0.0, 0.0] # Amp, freq, phase , offset
	plsq = leastsq(sine_erf, par,args=(ya,xa))
	if plsq[0][0] < 0:
		par = [abs(amp), freq*0.001, 3.14, 0.0] # Amp, freq, phase , offset
		plsq = leastsq(sine_erf, par,args=(ya,xa))
	if plsq[1] > 4:
		return None
	yfit = sine_eval(xa, plsq[0])
	#if plsq[0][0] < 0:
	    #print plsq[0]
	    #plsq[0][0] *= -1
	    #plsq[0][2] += pi
	    #print plsq[0]
	return yfit,plsq[0]

#--------------------------Damped Sine Fit ------------------------------------------------
def dsine_erf(p,y,x):
	return y - p[0] * sin(2*pi*p[1]*x+p[2]) * exp(-p[4]*x) + p[3]

def dsine_eval(x,p):
	return     p[0] * sin(2*pi*p[1]*x+p[2]) * exp(-p[4]*x) - p[3]

def fit_dsine(xlist, ylist, freq = 0, mode="kHz"):
	"""
	Fits a damped sinusoidal signal
	@param xlist the time series
	@param ylist the signal series
	@param freq the frequency to use for the fit. If zero, a FFT will be
	called to find a suitable frequency
	@param mode "kHz" (default) or "Hz". When the data in xlist are
	milliseconds, you may let mode to be "kHz", which is the default.
	However when the data in xlist are seconds, you must choose the
	mode "Hz".
	@return a vector of fitted data, and a quality value. If the quality
	is too bad, returns None.
	"""
	size = len(xlist)
	xa = array(xlist, dtype=float)
	ya = array(ylist, dtype=float)
	amp = (max(ya)-min(ya))/2
	if freq == 0:
		freq = find_frequency(xa,ya)
		if mode=="Hz":
			freq=freq/1000
	print freq
	par = [amp, freq, 0.0, 0.0, 0.1] # Amp, freq, phase , offset, decay constant
	plsq = leastsq(dsine_erf, par,args=(ya,xa))
	if plsq[1] > 4:
		return None
	yfit = dsine_eval(xa, plsq[0])
	return yfit,plsq[0]

#-------------------------- Exponential Fit ----------------------------------------
def exp_erf(p,y,x):
	return y - p[0] * exp(p[1]*x) + p[2]

def exp_eval(x,p):
	return p[0] * exp(p[1]*x)  -p[2]

def fit_exp(xlist, ylist):
	size = len(xlist)
	xa = array(xlist, dtype=float)
	ya = array(ylist, dtype=float)
	maxy = max(ya)
	halfmaxy = maxy / 2.0
	halftime = 1.0
	for k in range(size):
		if abs(ya[k] - halfmaxy) < halfmaxy/100:
			halftime = xa[k]
			break 
	par = [maxy, -halftime,0] 					# Amp, decay, offset
	plsq = leastsq(exp_erf, par,args=(ya,xa))
	if plsq[1] > 4:
		return None
	yfit = exp_eval(xa, plsq[0])
	return yfit,plsq[0]

#-------------------------- Gauss Fit ----------------------------------------
def gauss_erf(p,y,x):#height, mean, sigma
	return y - p[0] * exp(-(x-p[1])**2 /(2.0 * p[2]**2))

def gauss_eval(x,p):
	return p[0] * exp(-(x-p[1])**2 /(2.0 * p[2]**2))

def fit_gauss(xlist, ylist):
	size = len(xlist)
	xa = array(xlist, dtype=float)
	ya = array(ylist, dtype=float) 
	maxy = max(ya)
	halfmaxy = maxy / 2.0
	for k in range(size):
		if abs(ya[k] - maxy) < maxy/100:
			mean = xa[k]
			break
	for k in range(size):
		if abs(ya[k] - halfmaxy) < halfmaxy/10:
			halfmaxima = xa[k]
			break                      
	sigma = mean - halfmaxima
	par = [maxy, halfmaxima, sigma] # Amplitude, mean, sigma
	plsq = leastsq(gauss_erf, par,args=(ya,xa))
	if plsq[1] > 4:
		return None
	yfit = gauss_eval(xa, plsq[0])
	return yfit,plsq[0]

#-------------------------- liniar Fit ------------------------------------------------
def line_erf(p,y,x):					
	return y - p[0] * x - p[1]

def line_eval(x,p):			# y = a * x + b
	return p[0] * x + p[1]

def fit_line(xlist,ylist):	# Time in mS, V in volts
	size = len(xlist)
	xa = array(xlist, dtype=float)
	ya = array(ylist, dtype=float)
	par = [1,1] # m, c
	plsq = leastsq(line_erf, par,args=(ya,xa))
	if plsq[1] > 4:
		return None
	yfit = line_eval(xa, plsq[0])
	return yfit,plsq[0]

#-------------------------- Quadratic Fit ----------------------------------------
def qdr_erf(p,y,x):
	return y - (p[0] * x**2 +p[1]*x + p[2]) # ax^2 + bx + c

def qdr_eval(x,p):
	return p[0] * x**2 +p[1]*x + p[2]

def fit_qdr(xlist, ylist):
	size = len(xlist)
	xa = array(xlist, dtype=float)
	ya = array(ylist, dtype=float)
	par = [1, 1, 1] 					# a,b,c
	plsq = leastsq(qdr_erf, par,args=(ya,xa))
	if plsq[1] > 4:
		return None
	yfit = qdr_eval(xa, plsq[0])
	return yfit,plsq[0]

