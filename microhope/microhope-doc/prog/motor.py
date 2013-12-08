import phm, time
p=phm.phm()


p.set_ddr(0,255)
pos = 0
seq = [12, 6, 3, 9]

i = 0
while(1):
	p.set_port(0,seg[i%3])
	i += 1
