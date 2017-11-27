# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
import sys, time, utils, math, os.path

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

	tbvals = [0.05, 0.200, 0.500, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0]	# allowed mS/div values
	NP = 500			# Number of samples
	TG = 2				# Number of channels
	MINDEL = 1			# minimum time between samples, in usecs
	MAXDEL = 1000
	delay = MINDEL		# Time interval between samples
	TBval = 2			# timebase list index
	
	VMIN = -5
	VMAX = 5
	MAXCHAN = 1
	timeData    = [None]*MAXCHAN
	voltData    = [None]*MAXCHAN
	voltDataFit = [None]*MAXCHAN
	traceWidget = [None]*MAXCHAN
	traceWidget = [None]*MAXCHAN
	history = []		# Data store	
	traces = []
	trial = 2

	sources = ['A1','A2','A3', 'MIC']
	chanpens = ['y','g','w','m']     #pqtgraph pen colors

	
	def __init__(self, device=None):
		QWidget.__init__(self)
		self.p = device										# connection to the device hardware 
		try:
			self.p.select_range('A1',8.0)
		except:
			pass	
			
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
		self.SaveButton = QPushButton(self.tr("Save Data to"))
		self.SaveButton.setMaximumWidth(90)
		self.SaveButton.clicked.connect(self.save_data)		
		H.addWidget(self.SaveButton)
		self.Filename = utils.lineEdit(150, self.tr('RCtransient.txt'),20,None )
		H.addWidget(self.Filename)
		right.addLayout(H)
					
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

		b = QPushButton(self.tr("Analyse last Trace"))
		b.clicked.connect(self.fit_curve)		
		right.addWidget(b)

		b = QPushButton(self.tr("Clear Data & Traces"))
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
	def getSP(self, ya):
		if min(ya) < 0.1:           #discharge
			minval = 0
			minIndex = 0
		for k in range(len(ya)):
			if ya[k] < minval:
				minval = ya[k]
				minIndex = k
		if minIndex > 1: minIndex -= 1
		if (minIndex % 2) != 0: minIndex +=1    #odd number not good
		return minIndex
		
	def fit_curve(self):
		try:
			Rext = float(self.Rextext.text())
		except:
			self.msg(self.tr('Enter a valid Resistance'))
			return
		if self.history != []:
			sp = self.getSP(self.history[-1][1])
			ta = self.history[-1][0][sp:]
			va = self.history[-1][1][sp:]
			fa = em.fit_exp(ta,va)
		else:
			self.msg(self.tr('No data to analyze.'))
			return
		if fa != None:
			try:
				self.p.set_state(OD1=1)			# Do some DC work to find the resistance of the Inductor
				time.sleep(.5)
				v = self.p.get_voltage('A2')
				Vind = self.p.get_voltage('A1')     # voltage across the Inductor
			except:
				self.comerr()
				return	
			if v > 4.0:					# Means user has connected OD1 to A2
				vtotal = v
			else:
				vtotal = 5.0			# Assume OD1 = 5 volts
			i = (vtotal - Vind)/Rext
			Rind = Vind/i
			pa = fa[1]
			par1 = abs(1.0 / pa[1])
			ss1 = '%5.3f'%par1
			ss2 = '%5.0f'%Rind
			ss3 = '%5.1f'%((Rext+Rind)*par1)
			self.msg(self.tr('L/R = ') + ss1 + self.tr(' mSec : Rind = ') + ss2 + self.tr(' Ohm : L = ') + ss3 +  self.tr(' mH'))
			self.traces.append(self.pwin.plot(ta,va, pen = self.trial*2))
		else:
			self.msg(self.tr('Failed to fit the curve with V=Vo*exp(-t*L/R)'))
	
	def charge(self):
		try:
			self.p.set_state(OD1=0)		# OD1 to LOW
			time.sleep(self.tbvals[self.TBval]*0.01)
			t,v = self.p.capture_action('A1',self.NP, self.TG,'SET_HIGH')
		except:
			self.comerr()
			return		
		self.traces.append(self.pwin.plot(t,v, pen = self.trial*2))
		self.history.append((t,v))
		self.trial += 1

	def discharge(self):
		try:
			self.p.set_state(OD1=1)		# OD1 to HIGH
			time.sleep(self.tbvals[self.TBval]*0.01)
			t,v = self.p.capture_action('A1',self.NP, self.TG,'SET_LOW')
		except:
			self.comerr()
			return
		self.traces.append(self.pwin.plot(t,v, pen = self.trial*2))
		self.history.append((t,v))
		self.trial += 1

	def clear(self):
		for k in self.traces:
			self.pwin.removeItem(k)
		self.history = []
		self.trial = 2

	def save_data(self):
		fn = self.Filename.text()
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
	
