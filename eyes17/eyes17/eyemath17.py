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
import scipy.optimize as optimize


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
	v = array(ya)
	tr = abs(numpy.fft.fft(v))/np
	frq = numpy.fft.fftfreq(np, si * 1.0e-3)
        # the arguments for reshape must be integers: enforcing
        # the integer division by two.
	x = frq.reshape(2,np//2)
	y = tr.reshape(2,np//2)
	return x[0], y[0]    

def find_frequency(x,y):		# Returns the fundamental frequency using FFT
	tx,ty = fft(y, x[1]-x[0])
	index = find_peak(ty)
	if index == 0:
		return None
	else:
		return tx[index]

#-------------------------- Sine Fit ------------------------------------------------
def sine_erf(p,y,x):					
	return y - p[0] * sin(2*pi*p[1]*x+p[2])+p[3]

def sine_eval(x,p):			# y = a * sin(2*pi*f*x + phi)+ offset
	return p[0] * sin(2*pi*p[1]*x+p[2])-p[3]

def sineFunc(x, a1, a2, a3, a4):
    return a4 + a1*sin(abs(a2*(2*pi))*x + a3)

def fit_sine(xa,ya, freq = 0):	# Time in mS, V in volts, freq in Hz, accepts numpy arrays
	size = len(ya)
	mx = max(ya)
	mn = min(ya)
	amp = (mx-mn)/2
	if freq == 0:						# Guess frequency not given
		freq = find_frequency(xa,ya)
	if freq == None:
		return None
	#print 'guess a & freq = ', amp, freq
	par = [abs(amp), freq*0.001, 0.0, 0.0] # Amp, freq, phase , offset
	par, pcov = optimize.curve_fit(sineFunc, xa, ya, par)
	if par[0] < 0:		# Negative amplitude ?
		par[0] *= -1
		par[2] += pi
	yfit = sine_eval(xa, par)
	return yfit,par
	

#--------------------------Damped Sine Fit ------------------------------------------------
def dsine_erf(p,y,x):
	return y - p[0] * sin(2*pi*p[1]*x+p[2]) * exp(-p[4]*x) + p[3]

def dsine_eval(x,p):
	return     p[0] * sin(2*pi*p[1]*x+p[2]) * exp(-p[4]*x) - p[3]

def fit_dsine(xlist, ylist, freq = 0):
	size = len(xlist)
	xa = array(xlist, dtype=float)
	ya = array(ylist, dtype=float)
	amp = (max(ya)-min(ya))/2
	if freq == 0:
		freq = find_frequency(xa,ya)
	par = [amp, freq*0.001, 0.0, 0.0, 0.1] # Amp, freq, phase , offset, decay constant
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

	#-------------------------- Exponential Fit #2----------------------------------------

def exp_func(x, a, b, c):
	return a * exp(-x/ b) + c

def fit_exp2(t,v):    # accepts numpy arrays
	size = len(t)
	v80 = v[0] * 0.8
	for k in range(size-1):
		if v[k] < v80:
			rc = t[k]/.223
			break
	pg = [v[0], rc, 0]
	po, err = optimize.curve_fit(exp_func, t, v, pg)
	if abs(err[0][0]) > 0.1:
		return None, None
	vf = po[0] * exp(-t/po[1]) + po[2]
	return po, vf	


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

