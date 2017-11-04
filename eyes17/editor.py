# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
#from __future__ import print_function
import os, sys, time, inspect, os.path

from QtVersion import *

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
		self.p = device
		# connection to the device hardware
		#self.functionList['print']= self.msg
		# for redirecting print

		self.functionList['p'] = self.p

		from pythonSyntax import PythonHighlighter
		self.Edit = QTextEdit()
		self.highlighter=PythonHighlighter(self.Edit.document())
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
		s =unicode(self.Edit.toPlainText())		
		f = open(fn,'w')
		f.write(s)
		f.close()
		self.msg(self.tr('Code saved to ') + unicode(fn))

	def runCode(self):
		self.msg('')
		sys.stdout = x = ListStream()
		s =unicode(self.Edit.toPlainText())		
		self.msg('')
		try:
			submitted = compile(s.encode(), '<string>', mode='exec')
			exec(submitted, self.functionList)
			sys.stdout = sys.__stdout__
			self.msg(x.data)
		except Exception as e:
			self.msg(u'<font color="red">' + u'Err:' + unicode(e))
		
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
