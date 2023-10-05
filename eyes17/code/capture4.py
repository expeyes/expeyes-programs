#import eyes17.eyes          # uncomment these two lines while running stand-alone
#p = eyes17.eyes.open()

from matplotlib import pyplot as plt

p.set_sine(200)

res = p.capture4(500, 20)   # captures A1, A2,A3 and MIC

plt.plot(res[0], res[1], linewidth = 2, color = 'blue')
plt.plot(res[6], res[7], linewidth = 2, color = 'red')
plt.show()
