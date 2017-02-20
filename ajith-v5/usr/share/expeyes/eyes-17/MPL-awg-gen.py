# connect sine1 to CH1, sine2 to CH2

from pylab import *
import expeyes.eyes17
dev=expeyes.eyes17.open()

dev.select_range('A1', 4)

dev.configure_trigger(0,'A1', 0.)
'''
def sqr(x):      # generates the table for square
	y = zeros(512)
	for k in range(256): y[k] = 256
	return y
'''
	
def sqr(x):      # generates the table for square
	return [0]*256 + [1]*256

fn1 = lambda x: abs(x-256)	 					    # Triangular wave
fn2 = lambda x: sin(x) +sin(3*x)/2 + sin(5*x)/5		# Fourier series

dev.load_equation(sqr, [0,512])
#dev.load_equation(fn2, [-pi,pi])
dev.set_wave(3000)

#dev.set_sine(600)


NP = 3000
tg = 2
t,v1 = dev.capture1('A1',NP, tg)

#fr,amp = amp_spectrum(v2, tg*1.e-6)
#plot(fr, amp)

plot(t, v1, label='A1')
#plot(t, v2, label='CH2')
#plot(v1,v2)
legend(framealpha=0.5)
show()

