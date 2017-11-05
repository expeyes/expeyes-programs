# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
from __future__ import print_function
import sys, time, utils, math, os.path

from QtVersion import *

import pyqtgraph as pg
import numpy as np
import eyes17.eyemath17 as em


class Expt(QWidget):
	TIMER = 50
	RPWIDTH = 300
	RPGAP = 4
	running = False
	MINDEL = 1			# minimum time between samples, in usecs
	MAXDEL = 1000
	
	FMIN = 200
	FMAX = 4900
	FREQ = FMIN
	NSTEP = 100
	STEP = 10	  # 10 hz
	GMIN = 0.0		# filter amplitude Gain
	GMAX = 3.0
	Rload = 560.0
	data = [ [], [] ]
	currentTrace = None
	traces = []
	history = []		# Data store	
	sources = ['A1','A2','A3', 'MIC']
	trial = 0
	
	def __init__(self, device=None):
		QWidget.__init__(self)
		self.p = device										# connection to the device hardware 
		try:
			self.p.select_range('A1',4.0)
			self.p.select_range('A2',4.0)	
			self.p.configure_trigger(0, 'A1', 0)
		except:
			pass	

		self.traceCols = utils.makeTraceColors()
		
		self.pwin = pg.PlotWidget()							# pyqtgraph window
		self.pwin.showGrid(x=True, y=True)					# with grid
		ax = self.pwin.getAxis('bottom')
		ax.setLabel(self.tr('Frequency (Hz)'))	
		ax = self.pwin.getAxis('left')
		ax.setLabel(self.tr('Amplitude Gain'))
		self.pwin.disableAutoRange()
		self.pwin.setXRange(self.FMIN, self.FMAX)
		self.pwin.setYRange(self.GMIN, self.GMAX)
		self.pwin.hideButtons()								# Do not show the 'A' button of pg

		right = QVBoxLayout()							# right side vertical layout
		right.setAlignment(Qt.AlignTop)
		right.setSpacing(self.RPGAP)

		'''
		H = QHBoxLayout()
		l = QLabel(text=self.tr('Rload ='))
		l.setMaximumWidth(50)
		H.addWidget(l)
		self.LoadRes = utils.lineEdit(60, self.Rload, 6, None)
		H.addWidget(self.LoadRes)
		l = QLabel(text=self.tr('Ohm'))
		l.setMaximumWidth(40)
		H.addWidget(l)
		right.addLayout(H)
		'''

		H = QHBoxLayout()
		l = QLabel(text=self.tr('From'))
		l.setMaximumWidth(35)
		H.addWidget(l)
		self.AWGstart = utils.lineEdit(60, self.FMIN, 6, None)
		H.addWidget(self.AWGstart)
		l = QLabel(text=self.tr('to'))
		l.setMaximumWidth(20)
		H.addWidget(l)
		self.AWGstop = utils.lineEdit(60, self.FMAX, 6, None)
		H.addWidget(self.AWGstop)
		l = QLabel(text=self.tr('Hz'))
		l.setMaximumWidth(20)
		H.addWidget(l)
		right.addLayout(H)
		 
		H = QHBoxLayout()
		l = QLabel(text=self.tr('Number of Steps ='))
		l.setMaximumWidth(120)
		H.addWidget(l)
		self.NSTEPtext = utils.lineEdit(60, self.NSTEP, 6, None)
		H.addWidget(self.NSTEPtext)
		right.addLayout(H)

		b = QPushButton(self.tr("Start"))
		right.addWidget(b)
		b.clicked.connect(self.start)		
		
		self.FreqLabel = QLabel(self.tr(""))
		right.addWidget(self.FreqLabel)

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
		self.msgwin = QLabel(text='')
		full.addWidget(self.msgwin)
				
		self.setLayout(full)
		
		self.timer = QTimer()
		self.timer.timeout.connect(self.update)
		self.timer.start(self.TIMER)
		

		#----------------------------- end of init ---------------

	def verify_fit(self,y,y1):
		sum = 0.0
		for k in range(len(y)):
			sum += abs((y[k] - y1[k])/y[k])
		err = sum/len(y)
		if err > .5:
			return False
		else:
			return True
				
	def update(self):
		if self.running == False:
			return
		try:	
			fr=self.p.set_sine(self.FREQ)
		except:
			self.comerr()
			return 

		time.sleep(0.02)	
		self.TG = 1.e6/self.FREQ/50   # 50 points per wave
		self.TG = int(self.TG)//2 * 2
		NP = 500
		MAXTIME = 200000.  # .2 seconds
		if NP * self.TG > MAXTIME:
			NP = int(MAXTIME/self.TG)
		if NP % 2: NP += 1  # make it an even number
		ss = '%5.1f'%fr
		self.FreqLabel.setText(self.tr('Frequency = ') + ss + self.tr(' Hz'))
		if self.TG < self.MINDEL:
			self.TG = self.MINDEL
		elif self.TG > self.MAXDEL:
			self.TG = self.MAXDEL

		goodFit = False
		for k in range(3):	          # try 3 times
			try:
				t,v, tt,vv = self.p.capture2(NP, int(self.TG))	
			except:
				self.comerr()
				return 
			try:
				fa = em.fit_sine(t,v)
			except:
				self.msg(self.tr('Fit failed'))
				fa = None
			if fa != None:
				if self.verify_fit(v,fa[0]) == False:	#compare trace with the fitted curve
					continue
				try:
					fb = em.fit_sine(tt,vv)
				except:
					self.msg(self.tr('Fit failed'))
					fb = None
				if fb != None:
					if self.verify_fit(vv,fb[0]) == False:     
						continue
					self.data[0].append(fr)
					gain = abs(fb[1][0]) #/fa[1][0])
					self.data[1].append(gain)
					if self.gainMax < gain:
						self.gainMax = gain
						self.peakFreq = fr
					goodFit = True
					break
		
		self.FREQ += self.STEP
		#if goodFit == False: return

		if self.FREQ > self.FMAX:
			print ('Done')
			self.running = False
			self.history.append(self.data)
			self.traces.append(self.currentTrace)
			im = self.gainMax/self.Rload * 1000
			self.msg(self.tr('completed'))
			return

		if self.index > 1:			  # Draw the line
			self.currentTrace.setData(self.data[0], self.data[1])
		self.index += 1


	def start(self):
		if self.running == True: return
		
		try:
			self.FMIN = float(self.AWGstart.text())
			self.FMAX = float(self.AWGstop.text())
			self.NSTEP = float(self.NSTEPtext.text())
		except:
			self.msg(self.tr('Invalid Frequency limits'))
			return
		
		self.pwin.setXRange(self.FMIN, self.FMAX)
		self.pwin.setYRange(self.GMIN, self.GMAX)
		self.STEP = (self.FMAX - self.FMIN)/ self.NSTEP

		try:	
			self.p.select_range('A1',4)
			self.p.select_range('A2',4)
		except:
			self.comerr()
			return 
		self.running = True
		self.data = [ [], [] ]
		self.FREQ = self.FMIN
		self.currentTrace = self.pwin.plot([0,0],[0,0], pen = self.traceCols[self.trial%5])
		self.index = 0
		self.trial += 1
		self.gainMax = 0.0
		self.msg(self.tr('Started'))


	def stop(self):
		if self.running == False: return
		self.running = False
		self.history.append(self.data)
		self.traces.append(self.currentTrace)
		im = self.gainMax/self.Rload * 1000
		self.msg(self.tr('user Stopped'))

	def clear(self):
		if self.running == True:
			self.msg(self.tr('Measurement in progress'))
			return
		for k in self.traces:
			self.pwin.removeItem(k)
		self.history = []
		self.trial = 0
		self.msg(self.tr('Cleared Traces and Data'))
		
	def save_data(self):
		if self.running == True:
			self.msg(self.tr('Measurement in progress'))
			return
		if self.history == []:
			self.msg(self.tr('No data to save'))
			return
		fn = QFileDialog.getSaveFileName()
		if fn != '':
			self.p.save(self.history, fn)
			self.msg(self.tr('Traces saved to ') + unicode(fn))

		
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
	
