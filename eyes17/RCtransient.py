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
	AWGmin = 1
	AWGmax = 5000
	AWGval = 1000

	tbvals = [0.050, .200, 0.500, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0]	# allowed mS/div values
	NP = 500			# Number of samples
	TG = 2				# Number of channels
	MINDEL = 1			# minimum time between samples, in usecs
	MAXDEL = 1000
	delay = MINDEL		# Time interval between samples
	TBval = 2			# timebase list index
	Res = 1000
	
	VMIN = 0
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
	chanpens = ['y','g','w','m']     #pqtgraph pen colors

	
	def __init__(self, device=None):
		QWidget.__init__(self)
		self.p = device										# connection to the device hardware 
		try:
			self.p.select_range('A1',8.0)
		except:
			pass		
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
		right.setAlignment(Qt.AlignmentFlag(0x0020)) #Qt.AlignTop
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
		
		b = QPushButton(self.tr("0 -> 5V step on OD1"))
		b.clicked.connect(self.charge)		
		right.addWidget(b)
		
		b = QPushButton(self.tr("5 -> 0V step on OD1"))
		b.clicked.connect(self.discharge)		
		right.addWidget(b)

		b = QPushButton(self.tr("Calculate RC"))
		b.clicked.connect(self.fit_curve)		
		right.addWidget(b)

		b = QPushButton(self.tr("Clear Data & Traces"))
		b.clicked.connect(self.clear)		
		right.addWidget(b)
		
		H = QHBoxLayout()
		l = QLabel(self.tr("Resistance ="))
		l.setMaximumWidth(100)
		H.addWidget(l)
		self.Rval = utils.lineEdit(50, self.Res, 10, None)
		H.addWidget(self.Rval)
		l = QLabel(self.tr("Ohm"))
		l.setMaximumWidth(30)
		H.addWidget(l)
		right.addLayout(H)

		self.SaveButton = QPushButton(self.tr("Save Data"))
		self.SaveButton.clicked.connect(self.save_data)		
		right.addWidget(self.SaveButton)

		
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
			fa = em.fit_exp(self.history[-1][0], self.history[-1][1])
		else:
			self.msg(self.tr('No data to analyze.'))
			return
		try:
			rval = float(self.Rval.text())/1000  # convert to kOhms
		except:
			return

		if fa != None:
			pa = fa[1]
			rc = abs(1.0 / pa[1])
			self.traces.append(self.pwin.plot(self.history[-1][0], fa[0], pen = self.traceCols[self.trial%5]))
			self.trial += 1
			ss = '%5.1f'%rc
			self.msg(self.tr('Fitted data with V=Vo*exp(-t/RC). RC = ') + ss + self.tr(' mSec'))
		else:
			self.msg(self.tr('Failed to fit the curve with V=Vo*exp(-t/RC)'))
	
	def charge(self):
		try:
			self.p.set_state(OD1=0)		# OD1 to LOW
			time.sleep(self.tbvals[self.TBval]*0.01)
			t,v = self.p.capture_action('A1',self.NP, self.TG,'SET_HIGH')
		except:
			self.comerr()
			return 

		self.traces.append(self.pwin.plot(t,v, pen = self.traceCols[self.trial%5]))
		self.history.append((t,v))
		self.trial += 1

	def discharge(self):
		try:
			self.p.set_state(OD1=1)		# OD1 to LOW
			time.sleep(self.tbvals[self.TBval]*0.01)
			t,v = self.p.capture_action('A1',self.NP, self.TG,'SET_LOW')
		except:
			self.comerr()
			return 

		self.traces.append(self.pwin.plot(t,v, pen = self.traceCols[self.trial%5]))
		self.history.append((t,v))
		self.trial += 1

	def clear(self):
		for k in self.traces:
			self.pwin.removeItem(k)
		self.history = []
		self.trial = 0
		self.msg(self.tr('Cleared Data and Traces'))

	def save_data(self):
		if self.history == []:
			self.msg(self.tr('No data to save'))
			return
		fn = QFileDialog.getSaveFileName()
		if fn != '':
			self.p.save(self.history, fn)
			self.msg(self.tr('Traces saved to ') + fn)				
			
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

	def set_wave(self):
		try:
			res = self.p.set_sine(self.AWGval)
			ss = '%6.2f'%res
			self.msg(self.tr('AWG set to ') + ss + self.tr(' Hz'))
		except:
			self.comerr()
			return 

	def awg_text(self, text):
		try:
			val = float(text)
		except:
			return	
		if self.AWGmin <= val <= self.AWGmax:
			self.AWGval = val
			self.AWGslider.setValue(self.AWGval)
			self.set_wave()

	def awg_slider(self, val):
		if self.AWGmin <= val <= self.AWGmax:
			self.AWGval = val
			self.AWGtext.setText(val)
			self.set_wave()
		
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
	
