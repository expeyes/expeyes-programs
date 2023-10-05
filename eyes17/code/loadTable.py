#import eyes17.eyes          # uncomment these two lines while running stand-alone
#p = eyes17.eyes.open()

# Connect WG to A1

from matplotlib import pyplot as plt

x = arange(-256, 256)
x = abs(x)
p.load_table(x)
p.set_wave(400)

x,y = p.capture1('A1', 500,10)
plt.plot(x,y)
plt.show()
