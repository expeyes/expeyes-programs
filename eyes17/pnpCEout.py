# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
import sys, time, math, os.path
import utils
from QtVersion import *

import pyqtgraph as pg
import numpy as np
import eyes17.eyemath17 as em


class Expt(QWidget):
	TIMER = 50
	RPWIDTH = 300
	RPGAP = 4
	running = False
	
	VMIN = 0
	VMAX = -5.0
	VSET = VMIN
	IMIN = 0
	IMAX = -5.0
	STEP = -0.050	   # 50 mV
	data = [ [], [] ]
	currentTrace = None
	traces = []
	legends = []
	history = []		# Data store	
	
	def __init__(self, device=None):
		QWidget.__init__(self)
		self.p = device										# connection to the device hardware 

		self.traceCols = utils.makeTraceColors()
		self.resultCols = utils.makeResultColors()
		self.trial = 0
		
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
		right.setAlignment(Qt.AlignmentFlag(0x0020)) #Qt.AlignTop
		right.setSpacing(self.RPGAP)
		
		H = QHBoxLayout()
		l = QLabel(text=self.tr('Vbase (via 100kOhm)'))
		l.setMaximumWidth(140)
		H.addWidget(l)
		self.VBtext = utils.lineEdit(40, -1.0, 6, None)
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

		self.SaveButton = QPushButton(self.tr("Save Data"))
		self.SaveButton.clicked.connect(self.save_data)		
		right.addWidget(self.SaveButton)

		#------------------------end of right panel ----------------
		
		top = QHBoxLayout()
		top.addWidget(self.pwin)
		top.addLayout(right)
		
		full = QVBoxLayout()
		full.addLayout(top)
		self.msgwin = QLabel(text=self.tr(''))
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
		if self.VSET < self.VMAX:
			self.running = False
			self.history.append(self.data)
			self.traces.append(self.currentTrace)
			self.msg(self.tr('Completed plotting I-V'))
			l = pg.TextItem(text=self.ibtxt, color= self.resultCols[self.trial])
			self.trial += 1
			l.setPos(va,i)
			self.pwin.addItem(l)
			self.legends.append(l)
			return
		if self.index > 1:			  # Draw the line
			self.currentTrace.setData(self.data[0], self.data[1])
		self.index += 1


	def start(self):
		if self.running == True: 
			return
		text = self.VBtext.text()
		try:
			vbset = float(text)
			if vbset > -0.5 or vbset < -3.0:
				self.msg(self.tr('Base voltage should be from -0.5 to -3'))
		except:
			self.msg(self.tr('Invalid Base voltage, should be from -0.5 to -3'))
			return
				
		try:
			self.p.set_pv1(-5.0)			# Collector to 5V
			self.p.set_pv2(vbset)		# Set base bias on PV2, via 100 KOhm series resistance
			vb = self.p.get_voltage('A2')    # base voltage
		except:
			self.comerr()
			return 

		if vb > -0.5 or vb < -0.7:
			vb = -0.6
		ibase = (vbset-vb)/100.0e-3    # uA
		self.ibtxt = 'Ib = %5.3f uA'%ibase
		self.running = True
		self.data = [ [], [] ]
		self.VSET = self.VMIN
		self.currentTrace = self.pwin.plot([0,0],[0,0], pen = self.traceCols[self.trial%5])
		self.index = 0
		self.msg(self.tr('Started'))

	def stop(self):
		if self.running == False: return
		self.running = False
		self.history.append(self.data)
		self.traces.append(self.currentTrace)
		self.msg(self.tr('User Stopped'))

	def clear(self):
		for k in self.legends:
			self.pwin.removeItem(k)
		for k in self.traces:
			self.pwin.removeItem(k)
		self.history = []
		self.trial = 0
		self.msg(self.tr('Cleared Traces and Data'))

	def save_data(self):
		if self.history == []:
			self.msg(self.tr('No data to save'))
			return
		fn = QFileDialog.getSaveFileName()
		if fn != '':
			self.p.save(self.history, fn)
			self.msg(self.tr('Traces saved to ') + fn)				
		
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
	
