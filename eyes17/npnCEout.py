import sys, time, utils, math, os.path

if utils.PQT5 == True:
	from PyQt5.QtCore import Qt, QTimer, QTranslator, QLocale, QLibraryInfo
	from PyQt5.QtWidgets import QApplication,QWidget, QLabel, QHBoxLayout, QVBoxLayout,\
	QCheckBox, QPushButton 
	from PyQt5.QtGui import QPalette, QColor
else:
	from PyQt4.QtCore import Qt, QTimer, QTranslator, QLocale, QLibraryInfo
	from PyQt4.QtGui import QPalette, QColor, QApplication, QWidget,\
	QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QCheckBox

import pyqtgraph as pg
import numpy as np
import eyes17.eyemath17 as em


class Expt(QWidget):
	TIMER = 50
	RPWIDTH = 300
	RPGAP = 4
	running = False
	
	VMIN = 0
	VMAX = 5
	VSET = VMIN
	IMIN = 0
	IMAX = 5
	STEP = 0.050	   # 50 mV
	data = [ [], [] ]
	currentTrace = None
	traces = []
	legends = []
	history = []		# Data store	
	sources = ['A1','A2','A3', 'MIC']
	pencol = 2
	
	def __init__(self, device=None):
		QWidget.__init__(self)
		self.p = device										# connection to the device hardware 
		
		self.pwin = pg.PlotWidget()							# pyqtgraph window
		self.pwin.showGrid(x=True, y=True)					# with grid
		ax = self.pwin.getAxis('bottom')
		ax.setLabel(self.tr('Voltage (V)'))	
		ax = self.pwin.getAxis('left')
		ax.setLabel(self.tr('Current (mA)'))
		self.pwin.disableAutoRange()
		self.pwin.setXRange(self.VMIN, self.VMAX)
		self.pwin.setYRange(self.IMIN, self.IMAX)
		self.pwin.hideButtons()								# Do not show the 'A' button of pg

		right = QVBoxLayout()							# right side vertical layout
		right.setAlignment(Qt.AlignTop)
		right.setSpacing(self.RPGAP)
		
		H = QHBoxLayout()
		l = QLabel(text=self.tr('Vbase (via 100kOhm)'))
		l.setMaximumWidth(140)
		H.addWidget(l)
		self.VBtext = utils.lineEdit(40, 1.0, 6, None)
		H.addWidget(self.VBtext)
		l = QLabel(text=self.tr('V'))
		l.setMaximumWidth(10)
		H.addWidget(l)
		right.addLayout(H)
		 
		b = QPushButton(self.tr("Start"))
		right.addWidget(b)
		b.clicked.connect(self.start)		
		
		b = QPushButton(self.tr("Stop"))
		right.addWidget(b)
		b.clicked.connect(self.stop)		
		
		b = QPushButton(self.tr("Clear Traces"))
		right.addWidget(b)
		b.clicked.connect(self.clear)		

		H = QHBoxLayout()
		self.SaveButton = QPushButton(self.tr("Save Data to"))
		self.SaveButton.setMaximumWidth(90)
		self.SaveButton.clicked.connect(self.save_data)		
		H.addWidget(self.SaveButton)
		self.Filename = utils.lineEdit(150, self.tr('tran-VI.txt'), 20, None)
		H.addWidget(self.Filename)
		right.addLayout(H)

		#------------------------end of right panel ----------------
		
		top = QHBoxLayout()
		top.addWidget(self.pwin)
		top.addLayout(right)
		
		full = QVBoxLayout()
		full.addLayout(top)
		self.msgwin = QLabel(text='')
		full.addWidget(self.msgwin)
				
		self.setLayout(full)
		
		self.timer = QTimer()
		self.timer.timeout.connect(self.update)
		self.timer.start(self.TIMER)
		#----------------------------- end of init ---------------

				
	def update(self):
		if self.running == False:
			return
		try:
			vs = self.p.set_pv1(self.VSET)	
			time.sleep(0.001)	
			va = self.p.get_voltage('A1')		# voltage across the diode
		except:
			self.comerr()
			return 
		
		i = (vs-va)/1.0 	 		   # in mA, R= 1k
		self.data[0].append(va)
		self.data[1].append(i)
		self.VSET += self.STEP
		if self.VSET > self.VMAX:
			self.running = False
			self.history.append(self.data)
			self.traces.append(self.currentTrace)
			self.msg('Completed plotting I-V')

			l = pg.TextItem(text=self.ibtxt, color= self.pencol)
			l.setPos(va,i)
			self.pwin.addItem(l)
			self.legends.append(l)
			self.pencol += 2
			return
		if self.index > 1:			  # Draw the line
			self.currentTrace.setData(self.data[0], self.data[1])
		self.index += 1

	def start(self):
		if self.running == True: return
		text = self.VBtext.text()
		try:
			vbset = float(text)
			if vbset < .5 or vbset > 3.0:
				self.msg('Base valtage shold be from .5 to 3')
				return
		except:
			self.msg('Invalid Base valtage, shold be from .5 to 3')
			return
				
		try:
			self.p.set_pv1(5.0)			# Collector to 5V
			self.p.set_pv2(vbset)		# Set base bias on PV2, via 100 KOhm series resistance
			vb = self.p.get_voltage('A2')    # base voltage
		except:
			self.comerr()
			return 
		
		if vb < 0.5 or vb > 0.7:
			vb = 0.6
		ibase = (vbset-vb)/100.0e-3    # uA
		self.ibtxt = 'Ib = %5.3f uA'%ibase
		self.running = True
		self.data = [ [], [] ]
		self.VSET = self.VMIN
		self.currentTrace = self.pwin.plot([0,0],[0,0], pen = self.pencol)
		self.index = 0
		self.msg('Started. Vb = %5.3f Ib = %5.1f uA'%(vb,ibase))

	def stop(self):
		if self.running == False: return
		self.running = False
		self.history.append(self.data)
		self.traces.append(self.currentTrace)
		self.msg('User Stopped')

	def clear(self):
		for k in self.legends:
			self.pwin.removeItem(k)
		for k in self.traces:
			self.pwin.removeItem(k)
		self.history = []
		self.pencol = 2
		self.msg('Cleared Traces and Data')
		
	def save_data(self):
		if self.history == []:
			self.msg('No Traces available for saving')
			return
		fn = self.Filename.text()
		self.p.save(self.history, fn)
		self.msg('Traces saved to %s'%fn)
		
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
	
