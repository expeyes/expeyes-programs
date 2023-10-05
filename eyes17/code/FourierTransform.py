#import eyes17.eyes          # uncomment these two lines while running stand-alone
#p = eyes17.eyes.open()

from matplotlib import pyplot as plt
import eyes17.eyemath17 as em

p.set_sine(1000)
p.set_sqr1(500)

t,v, tt,vv = p.capture2(5000, 20)   # captures A1 and A2

plt.xlabel('Freq')
plt.ylabel('Amplitude')
plt.xlim([0,10000])

xa,ya = em.fft(v,20*0.001)
plt.plot(xa,ya, linewidth = 2, color = 'blue')

xa,ya = em.fft(vv, 20*0.001)
plt.plot(xa, ya, linewidth = 2, color = 'red')

plt.show()
