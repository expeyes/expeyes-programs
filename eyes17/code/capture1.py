#import eyes17.eyes          # uncomment these two lines while running stand-alone
#p = eyes17.eyes.open()

from matplotlib import pyplot as plt
x,y = p.capture1('A1',10,10)
plt.plot(x,y)
plt.show()
