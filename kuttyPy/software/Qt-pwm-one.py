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
	
		sl.setMaximum(65535)	
		sl.setValue(0)
		sl.valueChanged.connect(self.set_pwm)		

		layout = QVBoxLayout()	
		layout.addWidget(sl)	
		self.setLayout(layout)		
		self.init_pwm()
	
	def set_pwm(self, val):
		setReg (OCR1AH , (val>>8)&0x3)   #Output Compare register values
		setReg (OCR1AL , val&0xFF)   #Output Compare register values
		
	def init_pwm(self):
		# Initialize PWM1
		csb = 1 # Clock select bits uint8_t
		COM1A1 = 7
		WGM11  = 1
		WGM10  = 0
		setReg(TCCR1A , (1 << COM1A1) | (1 << WGM11) |(1 << WGM10)  )#Set 10bit PWM mode
		setReg(TCCR1B , csb)		
		setReg(DDRD,255)
		
			
		
app = QApplication(sys.argv)
mw = mwin()
mw.show()
sys.exit(app.exec_())


