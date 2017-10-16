import sys
from functools import partial
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from kuttyPy import *


class mwin(QWidget):
	WIDTH  = 400
	HEIGHT = 300
	bits = [None]*8
	PBdata = 0
	
	def __init__(self):
		QWidget.__init__(self)
		self.setMinimumSize(self.WIDTH, self.HEIGHT)
		self.setWindowTitle('Measurements & Controls')
		
		layout = QVBoxLayout()	
		H = QHBoxLayout()
		for k in range(8):
			self.bits[k] = QCheckBox('PortB-%3d'%k)
			self.bits[k].stateChanged.connect(partial (self.setbit, k))
			H.addWidget(self.bits[k])
			
		layout.addLayout(H)	
		self.cb = QCheckBox(text='Port B')
		layout.addWidget(self.cb)	
		self.cb.stateChanged.connect(self.setportB)
		self.setLayout(layout)
		
		setReg(DDRB, 255)
		
	def setbit(self, bit):
		print bit
		self.PBdata = 0
		if self.bits[bit].isChecked() == True:
			setBits(PORTB, 1 << bit)
		else:
			clrBits(PORTB, 1 << bit)
		
	def setportB(self):
		if self.cb.isChecked() == True:
			setReg(PORTB, 255)
		else: 
			setReg(PORTB, 0)
		
app = QApplication(sys.argv)
mw = mwin()
mw.show()
sys.exit(app.exec_())


