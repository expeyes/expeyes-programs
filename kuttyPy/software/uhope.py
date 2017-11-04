#from __future__ import print_function

import sys, os, time, inspect, os.path

PQT5=False # use Qt4 by default

utilsPaths=["../../eyes17", "/usr/share/eyes17"]
for path in utilsPaths:
        # consider utils.py first in development environment, then in
        # installed package, when this file may exist
        if os.path.exists(path):
                sys.path = [path] + sys.path
                import utils
                PQT5=utils.PQT5
                break

if PQT5 == True:
	from PyQt5.QtCore import Qt, QTimer, \
	        QTranslator, QLocale, QLibraryInfo
	from PyQt5.QtWidgets import QApplication,QWidget, QLabel, QTextEdit, QVBoxLayout,QHBoxLayout, QPushButton
	from PyQt5.QtGui import QPalette, QColor, QFont
else:
	from PyQt4.QtCore import Qt, QTimer, \
	        QTranslator, QLocale, QLibraryInfo
	from PyQt4.QtGui import QPalette, QColor, QFont, QApplication, QWidget,\
	QTextEdit, QLabel, QVBoxLayout, QPushButton,QHBoxLayout, QFileDialog
	


class Expt(QWidget):
	filename = ''
	TIMER = 500
	WIDTH = 900
	HEIGHT = 550

	def __init__(self, device=None):
		QWidget.__init__(self)

		self.Edit = QTextEdit(width=self.WIDTH)	
		full = QVBoxLayout()
		full.addWidget(self.Edit)
		H = QHBoxLayout()
		b = QPushButton(self.tr("Load"))
		b.setMaximumWidth(100)
		b.clicked.connect(self.loadCode)				
		H.addWidget(b)
		b = QPushButton(self.tr("Save"))
		b.setMaximumWidth(100)
		b.clicked.connect(self.saveCode)				
		H.addWidget(b)
		b = QPushButton(self.tr("SaveAs"))
		b.setMaximumWidth(100)
		b.clicked.connect(self.saveCode)				
		H.addWidget(b)
		b = QPushButton(self.tr("Run"))
		b.clicked.connect(self.runCode)				
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

		#----------------------------- end of init ---------------

	def saveCode(self):
		f = open(self.filename,'w')
		f.write(s)
		f.close()
		self.msg(self.tr('Code saved to ') + str(fn))

	def saveCodeAs(self):
		fn = QFileDialog.getSaveFileName()
		s =str(self.Edit.toPlainText())		
		f = open(fn,'w')
		f.write(s)
		f.close()
		self.msg(self.tr('Code saved to ') + str(fn))

	def loadCode(self):
		fn = QFileDialog.getOpenFileName()
		f = open(fn,'r')
		s = f.read()
		f.close()
		self.Edit.setText(s)
		self.filename = fn
		
	def runCode(self):
		self.msg('run')
		
			
	def msg(self, m):
		self.msgwin.setText(self.tr(m))
		

if __name__ == '__main__':
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

	mw = Expt()
	mw.show()
	sys.exit(app.exec_())
	
