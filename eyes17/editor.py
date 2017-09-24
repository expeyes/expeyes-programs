#from __future__ import print_function
import os, sys, time, utils, inspect

if utils.PQT5 == True:
	from PyQt5.QtCore import Qt, QTimer, QFont
	from PyQt5.QtWidgets import QApplication,QWidget, QLabel, QTextEdit, QVBoxLayout 
	from PyQt5.QtGui import QPalette, QColor
else:
	from PyQt4.QtCore import Qt, QTimer
	from PyQt4.QtGui import QPalette, QColor, QFont, QApplication, QWidget,\
	QTextEdit, QLabel, QVBoxLayout, QPushButton
	
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

		#self.functionList['print']= self.msg				# for redirecting print
		for a in dir(self.p):
			attr = getattr(self.p, a)
			if inspect.ismethod(attr) and a!='__init__':
				self.functionList[a] = attr
		

		self.Edit = QTextEdit()	
		full = QVBoxLayout()
		full.addWidget(self.Edit)
		b = QPushButton(self.tr("Execute Code"))
		full.addWidget(b)

		font = QFont()
		font.setPointSize(14)
		self.Edit.setFont(font)

		b.clicked.connect(self.runCode)				
		self.msgwin = QLabel(text=self.tr(''))
		self.msgwin.setStyleSheet('background-color: white')
		full.addWidget(self.msgwin)
				
		self.setLayout(full)
		
		self.timer = QTimer()
		self.timer.timeout.connect(self.update)
		self.timer.start(self.TIMER)

		#----------------------------- end of init ---------------

	def runCode(self):
		self.msg('')

		sys.stdout = x = ListStream()
		s =str(self.Edit.toPlainText())		
		try:
			submitted = compile(s.encode(), '<string>', mode='exec')
			exec(submitted, self.functionList)
			sys.stdout = sys.__stdout__
			self.msg(x.data)
		except Exception as e:
			self.msg('<font color="red">' +str(e))
		
	def update(self):
		fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'code', self.mycode+'.py')
		f = open(fn)
		s = f.read()
		self.Edit.setText(s)	
		self.timer.stop()
			
	def msg(self, m):
		self.msgwin.setText(self.tr(str(m)))
		

if __name__ == '__main__':
	import eyes17.eyes
	dev = eyes17.eyes.open()
	app = QApplication(sys.argv)
	mw = Expt(dev)
	mw.show()
	sys.exit(app.exec_())
	
