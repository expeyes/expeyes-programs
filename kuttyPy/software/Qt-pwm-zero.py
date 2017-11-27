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
		# Initialize PWM0
		setReg(DDRB,255)
		csb = 1 		# Clock select bits uint8_t
		WGM01=3
		WGM00=6
		COM01=5
		setReg( TCCR0 , (1 << WGM01) | (1 << WGM00) | (1 << COM01) | csb )
		
	
	def set_pwm(self, val):
		setReg(OCR0 , int(val)&255)
		
app = QApplication(sys.argv)
mw = mwin()
mw.show()
sys.exit(app.exec_())


