
import sys
class ListStream:
    def __init__(self):
        self.data = []
    def write(self, s):
        self.data.append(s)

sys.stdout = x = ListStream()

for i in range(2):
    print ('i = ', i)

sys.stdout = sys.__stdout__
print(x.data)
