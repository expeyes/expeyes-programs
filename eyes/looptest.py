from __future__ import print_function

import gettext
gettext.bindtextdomain("expeyes")
gettext.textdomain('expeyes')
_ = gettext.gettext

import expeyes.eyes as eyes
p = eyes.open()

NP =1800

x = 1
while 1:
	t,v = p.capture(0,NP,20)
	if len(t) != NP:
		print (_('Error..'),)
	print (x, len(t))
	x += 1
