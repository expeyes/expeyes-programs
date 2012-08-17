#Author : Jithin B.P., jithinbp@gmail.com
#Distributed under GNU General Public License, GPL-3

import gettext
gettext.bindtextdomain("expeyes")
gettext.textdomain('expeyes')
_ = gettext.gettext

sa2=261.63
re2=277.03
RE2=294.35
ga2=314.02
GA2=328.49
ma2=348.83
MA2=369.36
pa2=392.46
dha2=415.55
DHA2=441.54
ni2=233.08
NI2=246.94


sa=261.63
re=277.03
RE=294.35
ga=314.02
GA=328.49
ma=348.83
MA=369.36
pa=392.46
dha=415.55
DHA=441.54
ni=471.04
NI=492.75
SA=523.26


jan=[sa,RE,GA,GA,GA,GA,GA,GA,GA,2,GA,GA,RE,GA,ma,2,GA,2,GA,GA,RE,2,RE,RE,NI2,RE,
sa,2,7,sa,2,pa,2,pa,pa,2,pa,pa,pa,pa,2,pa,pa,MA,DHA,pa,ma,ma,2,ma,ma,
ma,2,ma,GA,RE,ma,GA,2,0,2,GA,2,GA,GA,GA,2,GA,RE,pa,pa,pa,ma,ma,ma,ma,2,GA,2,GA,GA
,RE,RE,RE,RE,NI2,RE,sa,8,sa,RE,GA,GA,GA,2,GA,2,RE,GA,ma,8,GA,ma,pa,pa,pa,ma,ma
,GA,RE,ma,GA,4,0,2,GA,2,GA,RE,RE,RE,RE,RE,NI2,RE,sa,8,pa,pa,pa,pa,pa,2,pa,pa,pa,2,
pa,pa,MA,DHA,pa,ma,ma,2,ma,ma,ma,2,ma,GA,RE,ma,GA,8,
SA,NI,SA,8,NI,DHA,NI,8,pa,pa,DHA,8,0,2,sa,sa,
RE,RE,GA,GA,RE,GA,ma,4]


#jan=[sa,RE,GA,GA,GA]

index = 0
TIMER = 240		# milliseconds

def put_freq():
	global jan, index, size
	if index >= size:
		 quit()
	a = jan[index]
	if(a < 11):				# it is a delay
		time.sleep(float(a)/100)
	else :
		p.set_sqr1(a);
	index += 1
	root.after(TIMER, put_freq)

def quit():
	print _('Exiting')
	p.set_sqr1(0)
	sys.exit()

import expeyes.eyes as eyes, time
from Tkinter import *

root = Tk()
p=eyes.open()
size = len(jan)

cf = Frame(root)
cf.pack(side=TOP,  fill = BOTH, expand = 1)
b3 = Label(cf, text = _('Playing Music'))
b3.pack(side = LEFT, anchor = SW)

b5 = Button(cf, text = _('QUIT'), command = quit)
b5.pack(side = RIGHT, anchor = N)

root.after(TIMER, put_freq)
root.mainloop()


