import sys
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QWidget, QSlider, QApplication, QVBoxLayout
from kuttyPy import *


class mwin(QWidget):
	
	def __init__(self):
		QWidget.__init__(self)
		self.resize(400, 100)
		self.setWindowTitle('Control Duty Cycle of PWM0')
		
		layout = QVBoxLayout()	

		sl = QSlider(Qt.Horizontal)
		sl.setMinimum(0)
		sl.setMaximum(255)	
		sl.setValue(0)
		sl.valueChanged.connect(self.set_pwm0)		
		layout.addWidget(sl)	
		
		sl = QSlider(Qt.Horizontal)
		sl.setMinimum(0)
		sl.setMaximum(65535)	
		sl.setValue(0)
		sl.valueChanged.connect(self.set_pwm1)		
		layout.addWidget(sl)	
		
		sl = QSlider(Qt.Horizontal)
		sl.setMinimum(0)
		sl.setMaximum(255)	
		sl.setValue(0)
		sl.valueChanged.connect(self.set_pwm2)		
		layout.addWidget(sl)	
		
		self.setLayout(layout)		
		self.init_pwm()
	
	def set_pwm0(self, val):
		setReg(OCR0 , int(val)&255)

	def set_pwm1(self, val):
		setReg (OCR1AH , (val>>8)&0x3)   #Output Compare register values
		setReg (OCR1AL , val&0xFF)   #Output Compare register values

	def set_pwm2(self, val):
		setReg(OCR2 , int(val)&255)
		
	def init_pwm(self):
		# Initialize PWM0
		setReg(DDRB,255)
		csb = 1 		# Clock select bits uint8_t
		WGM01=3
		WGM00=6
		COM01=5
		setReg( TCCR0 , (1 << WGM01) | (1 << WGM00) | (1 << COM01) | csb )
		# Initialize PWM1
		csb = 1 # Clock select bits uint8_t
		COM1A1 = 7
		WGM11  = 1
		WGM10  = 0
		setReg(TCCR1A , (1 << COM1A1) | (1 << WGM11) |(1 << WGM10)  )#Set 10bit PWM mode
		setReg(TCCR1B , csb)		
		setReg(DDRD,255)
		# Initialize PWM2
		WGM21=3
		WGM20=6
		COM21=5
		csb = 1 		# Clock select bits uint8_t
		setReg( TCCR2 , (1 << WGM21) | (1 << WGM20) | (1 << COM21) | csb )
		setReg(TCNT2, 0)		
		setReg(DDRD,255)
			
		
app = QApplication(sys.argv)
mw = mwin()
mw.show()
sys.exit(app.exec_())


