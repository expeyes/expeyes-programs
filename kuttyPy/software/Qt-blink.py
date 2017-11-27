import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from kuttyPy import *


class mwin(QWidget):
	def __init__(self):
		QWidget.__init__(self)
		self.resize(300,200)	
		layout = QVBoxLayout()	
		self.cb = QCheckBox(text='Control PortB')
		layout.addWidget(self.cb)	
		self.cb.stateChanged.connect(self.action)
		self.setLayout(layout)
		setReg(DDRB, 255)
				
	def action(self):
		if self.cb.isChecked() == True:
			setReg(PORTB, 255)
		else: 
			setReg(PORTB, 0)
		
app = QApplication(sys.argv)
mw = mwin()
mw.show()
sys.exit(app.exec_())


