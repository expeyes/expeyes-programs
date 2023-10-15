


## Code Examples

### Capture1 : Single Channel Oscilloscope

```python
import eyes17.eyes
p = eyes17.eyes.open()

from matplotlib import pyplot as plt
x,y = p.capture1('A1',10,10)
plot(x,y)
show()

```
