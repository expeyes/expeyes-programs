#from __future__ import print_function
import os, sys, time, inspect, os.path
import utils

from QtVersion import *

class ListStream:
    def __init__(self):
            self.data = ''
    def write(self, s):
            self.data += s


class Expt(QWidget):
	functionList = {}
	mycode = ''
	TIMER = 500
	ht = 40
	info = 'Gravity by Time of Flight.\nConnect the electromagnet to OD1 and Attach the ball.\nPlace the contact sensor below and connect it between SEN and GND.\nPress the Measure button.'
	
	def __init__(self, device=None):
		QWidget.__init__(self)
		self.p = device										# connection to the device hardware 		
		try:
			self.p.set_state(OD1=1)
		except:
			print('could not set OD1 to 5V')
			pass

		full = QVBoxLayout()
		
		self.Edit = QTextEdit()	
		full.addWidget(self.Edit)
		font = QFont()
		font.setPointSize(16)
		self.Edit.setFont(font)

		s=self.tr(self.info)
		self.Edit.setText(s)
			
		H = QHBoxLayout()
		b = QPushButton(self.tr("Measure"))
		H.addWidget(b)
		b.clicked.connect(self.measure_tof)		
		H.addWidget(b)
		full.addLayout(H)


		self.msgwin = QLabel(text='')
		self.msgwin.setStyleSheet('background-color: white')
		full.addWidget(self.msgwin)
				
		self.setLayout(full)	
		self.timer = QTimer()

		#----------------------------- end of init ---------------

	def ht_text(self, text):
		try:
			val = float(text)
		except:
			return
		val = float(text)
		print (val)
			
		
	def measure_tof(self):
		self.msg(self.tr('start..'))
		res = self.p.SinglePinEdges('SEN','falling',1,OD1=0)
		self.p.set_state(OD1=1)
		try:
			t = res[0]
			ss = '%5.3f'%t
			self.msg(self.tr('Time of flight =') + ss + self.tr(' Seconds'))
		except:
			self.msg(self.tr('Error. Try again'))
			
	def sq1_slider(self, val):
		try:
			res = self.p.set_sqr1(val*0.01)
			ss = '%5.2f'%res
			self.msg(self.tr('sqr1 set to ') + ss + self.tr(' Hz'))
		except:
			self.comerr()
					
	def msg(self, m):
		self.msgwin.setText(self.tr(m))
		
	def comerr(self):
		self.msgwin.setText('<font color="red">' + self.tr('Error. Try Device->Reconnect'))

if __name__ == '__main__':
	import eyes17.eyes
	dev = eyes17.eyes.open()
	app = QApplication(sys.argv)

	# translation stuff
	lang=QLocale.system().name()
	t=QTranslator()
	t.load("lang/"+lang, os.path.dirname(__file__))
	app.installTranslator(t)
	t1=QTranslator()
	t1.load("qt_"+lang,
	        QLibraryInfo.location(QLibraryInfo.TranslationsPath))
	app.installTranslator(t1)

	mw = Expt(dev)
	mw.show()
	sys.exit(app.exec_())
	
