#import eyes17.eyes          # uncomment these two lines while running stand-alone
#p = eyes17.eyes.open()

# Connect WG to A1

from matplotlib import pyplot as plt

def f1(x):                         #
	return sin(x) + sin(3*x)/3

p.load_table(abs(arange(-256,256)))
p.set_wave(400)

x,y = p.capture1('A1', 500,10)
plt.plot(x,y)
plt.show()
