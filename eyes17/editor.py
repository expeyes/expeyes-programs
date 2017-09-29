#from __future__ import print_function
import os, sys, time, utils, inspect, os.path

if utils.PQT5 == True:
	from PyQt5.QtCore import Qt, QTimer, QFont, \
                QTranslator, QLocale, QLibraryInfo
	from PyQt5.QtWidgets import QApplication,QWidget, QLabel, QTextEdit, QVBoxLayout,QHBoxLayout 
	from PyQt5.QtGui import QPalette, QColor
else:
	from PyQt4.QtCore import Qt, QTimer, \
                QTranslator, QLocale, QLibraryInfo
	from PyQt4.QtGui import QPalette, QColor, QFont, QApplication, QWidget,\
	QTextEdit, QLabel, QVBoxLayout, QPushButton,QHBoxLayout, QFileDialog
	
class ListStream:
	data = ':'
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

		self.functionList['p'] = self.p

		self.Edit = QTextEdit()	
		full = QVBoxLayout()
		full.addWidget(self.Edit)
		
		H = QHBoxLayout()
		b = QPushButton(self.tr("Execute Code"))
		b.clicked.connect(self.runCode)				
		H.addWidget(b)
		b = QPushButton(self.tr("Save Code"))
		b.setMaximumWidth(100)
		b.clicked.connect(self.saveCode)				
		H.addWidget(b)
		full.addLayout(H)

		font = QFont()
		font.setPointSize(14)
		self.Edit.setFont(font)

		self.msgwin = QLabel(text='')
		self.msgwin.setStyleSheet('background-color: white')
		full.addWidget(self.msgwin)
				
		self.setLayout(full)
		
		self.timer = QTimer()
		self.timer.timeout.connect(self.update)
		self.timer.start(self.TIMER)

		#----------------------------- end of init ---------------

	def saveCode(self):
		fn = QFileDialog.getSaveFileName()
		s =str(self.Edit.toPlainText())		
		f = open(fn,'w')
		f.write(s)
		f.close()
		self.msg('Code saved to %s'%fn)

	def runCode(self):
		self.msg('')
		sys.stdout = x = ListStream()
		s =str(self.Edit.toPlainText())		
		self.msg('')
		try:
			submitted = compile(s.encode(), '<string>', mode='exec')
			exec(submitted, self.functionList)
			sys.stdout = sys.__stdout__
			self.msg(x.data)
		except Exception as e:
			self.msg('<font color="red">' + 'Err:' + str(e))
		
	def update(self):
		fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'code', self.mycode+'.py')
		f = open(fn)
		s = f.read()
		self.Edit.setText(s)	
		self.timer.stop()
			
	def msg(self, m):
		self.msgwin.setText(self.tr(m))
		

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
	
