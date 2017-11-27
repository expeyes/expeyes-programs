# Setup PWM using TC2 and change PWM width interactively
import sys
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QWidget, QSlider, QApplication, QVBoxLayout
from kuttyPy import *


class mwin(QWidget):
	
	def __init__(self):
		QWidget.__init__(self)
		self.resize(400, 100)
		self.setWindowTitle('Control Duty Cycle of PWM0')
		
		sl = QSlider(Qt.Horizontal)
		sl.setMinimum(0)
	
		sl.setMaximum(255)	
		sl.setValue(128)
		sl.valueChanged.connect(self.set_pwm)		

		layout = QVBoxLayout()	
		layout.addWidget(sl)	
		self.setLayout(layout)		
		self.init_pwm()

	def init_pwm(self):
		# Initialize PWM2
		WGM21=3
		WGM20=6
		COM21=5
		csb = 1 		# Clock select bits uint8_t
		setReg( TCCR2 , (1 << WGM21) | (1 << WGM20) | (1 << COM21) | csb )
		setReg(TCNT2, 0)		
		setReg(DDRD,255)		
	
	def set_pwm(self, val):
		setReg(OCR2 , int(val)&255)
		
app = QApplication(sys.argv)
mw = mwin()
mw.show()
sys.exit(app.exec_())


