import eyes17.eyes
p = eyes17.eyes.open()

# Connect WG to A1

from matplotlib import pyplot as plt

p.set_wave(500,'tria')
x,y = p.capture1('A1', 500,10)
plot(x,y)
show()
