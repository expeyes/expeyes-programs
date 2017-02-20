import expeyes.eyesj
p=expeyes.eyesj.open()

print 'A1 m = ',p.restore_float(0)
print 'A1 c = ',p.restore_float(2)
print 'A2 m = ',p.restore_float(4)
print 'A2 c = ',p.restore_float(6)
print 'Socket Cap = ',p.restore_float(8)
print 'IN1 CF = ',p.restore_float(10)
print 'SEN Pullup =', p.restore_float(12)

