import eyes17.eyes, time
import eyes17.eyemath17 as em

from pylab  import *

p = eyes17.eyes.open()

p.set_state(OD1=1)		# OD1 to HIGH

time.sleep(.5)

t,v = p.capture_action('A1', 300, 2,'SET_LOW')

plot(t,v)

fa = em.fit_exp(t,v)

plot(t, fa[0])

pa = fa[1]

par1 = abs(1.0 / pa[1])

print fa[1], par1

#self.msg('L/R = %5.3f mSec : Rind = %5.0f Ohm : L = %5.1f mH'%(par1, Rind, (Rext+Rind)*par1))

show()
