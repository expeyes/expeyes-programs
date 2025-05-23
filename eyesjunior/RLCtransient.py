# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
import sys, time, math, os.path
import utils

from QtVersion import *

import pyqtgraph as pg
import numpy as np
import eyesjun.eyemath as em


class Expt(QWidget):
	TIMER = 50
	RPWIDTH = 300
	RPGAP = 4
	AWGmin = 1
	AWGmax = 5000
	AWGval = 1000

	tbvals = [0.1, 0.2, 0.5, 1.0, 2.0, 5.0]	# allowed mS/div values
	NP = 500			# Number of samples
	TG = 2				# Number of channels
	MINDEL = 1			# minimum time between samples, in usecs
	MAXDEL = 1000
	delay = MINDEL		# Time interval between samples
	TBval = 1			# timebase list index
	
	VMIN = -3
	VMAX = 5
	MAXCHAN = 1
	timeData    = [None]*MAXCHAN
	voltData    = [None]*MAXCHAN
	voltDataFit = [None]*MAXCHAN
	traceWidget = [None]*MAXCHAN
	traceWidget = [None]*MAXCHAN
	history = []		# Data store	
	traces = []
	trial = 0

	sources = ['A1','A2','A3', 'MIC']

	
	def __init__(self, device=None):
		QWidget.__init__(self)
		self.p = device										# connection to the device hardware 

		self.traceCols = utils.makeTraceColors()
			
		self.history = []
		self.traces = []
		self.pwin = pg.PlotWidget()							# pyqtgraph window
		self.pwin.showGrid(x=True, y=True)					# with grid
		ax = self.pwin.getAxis('bottom')
		ax.setLabel(self.tr('Time (mS)'))	
		ax = self.pwin.getAxis('left')
		ax.setLabel(self.tr('Voltage'))
		self.pwin.disableAutoRange()
		self.pwin.setYRange(self.VMIN, self.VMAX)
		#self.pwin.hideButtons()								# Do not show the 'A' button of pg

		right = QVBoxLayout()							# right side vertical layout
		right.setAlignment(Qt.AlignTop)
		right.setSpacing(self.RPGAP)
					
		H = QHBoxLayout()
		l = QLabel(text=self.tr('Timebase'))
		l.setMaximumWidth(60)
		H.addWidget(l)
		self.TBslider = utils.slider(0, len(self.tbvals)-1, self.TBval, 150, self.set_timebase)
		H.addWidget(self.TBslider)
		l = QLabel(text=self.tr('mS/div'))
		l.setMaximumWidth(60)
		H.addWidget(l)
		right.addLayout(H)
	
		b = QPushButton(self.tr("5 -> 0V step on OD1"))
		b.clicked.connect(self.discharge)		
		right.addWidget(b)

		H = QHBoxLayout()
		l = QLabel(text=self.tr('Rext ='))
		l.setMaximumWidth(40)
		H.addWidget(l)
		self.Rextext = utils.lineEdit(100, 1000, 6, None)
		H.addWidget(self.Rextext)
		l = QLabel(text=self.tr('Ohm'))
		l.setMaximumWidth(20)
		H.addWidget(l)
		right.addLayout(H)

		b = QPushButton(self.tr("Analyse latest Data"))
		b.clicked.connect(self.fit_curve)		
		right.addWidget(b)

		self.SaveButton = QPushButton(self.tr("Save Data"))
		self.SaveButton.clicked.connect(self.save_data)		
		right.addWidget(self.SaveButton)

		b = QPushButton(self.tr("Clear Data"))
		b.clicked.connect(self.clear)		
		right.addWidget(b)
		
		#------------------------end of right panel ----------------
		
		top = QHBoxLayout()
		top.addWidget(self.pwin)
		top.addLayout(right)
		
		full = QVBoxLayout()
		full.addLayout(top)
		self.msgwin = QLabel(text=self.tr('messages'))
		full.addWidget(self.msgwin)
				
		self.setLayout(full)
		
		self.timer = QTimer()
		self.timer.timeout.connect(self.update)
		self.timer.start(self.TIMER)
		self.set_timebase(self.TBval)

		#----------------------------- end of init ---------------
		
	def fit_curve(self):
		if self.history != []:
			fa = em.fit_dsine(self.history[-1][0], self.history[-1][1],0)
		else:
			self.msg(self.tr('No data to analyze.'))
			return
			
		if fa != None:
			pa = fa[1]
			rc = 1.0 / pa[1]
			damping = pa[4] / (2*math.pi*pa[1]) # unitless damping factor
			ss1 = '%5.2f'%pa[1]
			ss2 = '%5.3f'%damping
			self.msg(self.tr('Resonant Frequency = ') + ss1 + self.tr(' kHz Damping factor= ') + ss2)
			self.traces.append(self.pwin.plot(self.history[-1][0], fa[0], pen = self.traceCols[self.trial%5]))
			self.history.append((self.history[-1][0], fa[0]))			
			self.trial += 1
		else:
			self.msg(self.tr('Failed to fit the curve'))
	
	def charge(self):
		try:
			self.p.set_state(10,0)					# OD1 to LOW
			self.p.enable_set_high(10)				# enable HI on OD1
			time.sleep(self.tbvals[self.TBval]*0.01)
			t,v = self.p.capture(1,self.NP, self.TG)
		except:
			self.comerr()
			return

		self.pwin.setYRange(0,8)
		self.traces.append(self.pwin.plot(t,v, pen = self.traceCols[self.trial%5]))
		self.history.append((t,v))
		self.trial += 1

	def discharge(self):
		try:
			self.p.set_state(10,1)				# OD1 to HI
			self.p.enable_set_low(10)				# enable HI on OD1
			time.sleep(self.tbvals[self.TBval]*0.01)
			t,v = self.p.capture(1, self.NP, self.TG)
		except:
			self.comerr()
			return

		self.pwin.setYRange(-3,5)
		self.traces.append(self.pwin.plot(t, v, pen = self.traceCols[self.trial%5]))
		self.history.append((t,v))
		self.trial += 1

	def clear(self):
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
			self.msg(self.tr('Traces saved to ') + unicode(fn))
			
	def set_timebase(self, tb):
		self.TBval = tb
		self.pwin.setXRange(0, self.tbvals[self.TBval]*10)
		msperdiv = self.tbvals[int(tb)]				#millisecs / division
		totalusec = msperdiv * 1000 * 10.0  	# total 10 divisions
		self.TG = int(totalusec/self.NP)
		if self.TG < self.MINDEL:
			self.TG = self.MINDEL
		elif self.TG > self.MAXDEL:
			self.TG = self.MAXDEL
		
	def msg(self, m):
		self.msgwin.setText(self.tr(m))
		
	def comerr(self):
		self.msgwin.setText('<font color="red">' + self.tr('Error. Try Device->Reconnect'))

if __name__ == '__main__':
	import eyesjun.eyes
	dev = eyesjun.eyes.open()
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
	
