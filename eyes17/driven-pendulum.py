#from __future__ import print_function
import os, sys, time, utils, inspect

if utils.PQT5 == True:
	from PyQt5.QtCore import Qt, QTimer, QFont
	from PyQt5.QtWidgets import QApplication,QWidget, QLabel, QTextEdit, QVBoxLayout,QHBoxLayout 
	from PyQt5.QtGui import QPalette, QColor
else:
	from PyQt4.QtCore import Qt, QTimer
	from PyQt4.QtGui import QPalette, QColor, QFont, QApplication, QWidget,\
	QTextEdit, QLabel, QVBoxLayout, QPushButton,QHBoxLayout, QFileDialog
	
class ListStream:
    def __init__(self):
        self.data = ''
    def write(self, s):
        self.data += s


class Expt(QWidget):
	functionList = {}
	mycode = ''
	TIMER = 500
	
	def __init__(self, device=None):
		QWidget.__init__(self)
		self.p = device										# connection to the device hardware 		


		full = QVBoxLayout()
		
		self.Edit = QTextEdit()	
		full.addWidget(self.Edit)
		font = QFont()
		font.setPointSize(16)
		self.Edit.setFont(font)

		s=tr('This program sets SQ1 to high resolution mode. WG will be disabled.\
Frequency can be changed from 0.1 Hz to 50Hz')
		self.Edit.setText(s)	
	
		H = QHBoxLayout()
		l = QLabel(text=self.tr('Set SQ1'))
		l.setMaximumWidth(60)
		H.addWidget(l)

		self.SQ1slider = utils.slider(10, 5000, 100, 1000,self.sq1_slider)
		H.addWidget(self.SQ1slider)
		full.addLayout(H)

		self.msgwin = QLabel(text=self.tr(''))
		self.msgwin.setStyleSheet('background-color: white')
		full.addWidget(self.msgwin)
				
		self.setLayout(full)	
		self.timer = QTimer()

		#----------------------------- end of init ---------------

	def sq1_slider(self, val):
		try:
			res = self.p.set_sqr1(val*0.01)
			self.msg('sqr1 set to %5.1f Hz'%res)
		except:
			self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		
			
			
	def msg(self, m):
		self.msgwin.setText(self.tr(str(m)))
		

if __name__ == '__main__':
	import eyes17.eyes
	dev = eyes17.eyes.open()
	app = QApplication(sys.argv)
	mw = Expt(dev)
	mw.show()
	sys.exit(app.exec_())
	
