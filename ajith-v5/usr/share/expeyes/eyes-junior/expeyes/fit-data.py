fi = open('bi-decay.dat','r')
x = []
y = []

while(1):
	s = fi.readline()
	if s == '': break
	ss = s.split()
	time = float(ss[0])
	cnt = float(ss[1])
	x.append(time)
	y.append(cnt)

print x,y

y1, par = em.fitexp(x,y)
print par
