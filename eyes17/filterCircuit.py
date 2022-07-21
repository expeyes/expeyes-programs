# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
from __future__ import print_function
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
	MINDEL = 1			# minimum time between samples, in usecs
	MAXDEL = 1000
	
	FMIN = 200
	FMAX = 4900
	FREQ = FMIN
	NSTEP = 100
	STEP = 10	  # 10 hz
	Rload = 560.0
	data = [ [], [] ]
	currentTrace = None
	traces = []
	history = []		# Data store	
	sources = ['A1','A2','A3', 'MIC']
	trial = 0
	Ranges12 = ['16 V', '8 V','4 V', '2.5 V', '1 V', '.5V']	# Voltage ranges for A1 and A2
	RangeVals12 = [16., 8., 4., 2.5, 1., 0.5]
	Range = 2	
	Wgains = ['80 mV','1V','3V']
	wgainindex = 1
		
	def __init__(self, device=None):
		QWidget.__init__(self)
		self.p = device										# connection to the device hardware 
		try:
			self.p.set_sine(1000)
			self.p.set_sine_amp(self.wgainindex)
			print (index)
		except:
			pass
			
		self.traceCols = utils.makeTraceColors()
		
		self.pwin = pg.PlotWidget()							# pyqtgraph window
		self.pwin.showGrid(x=True, y=True)					# with grid
		ax = self.pwin.getAxis('bottom')
		ax.setLabel(self.tr('Frequency (Hz)'))	
		ax = self.pwin.getAxis('left')
		ax.setLabel(self.tr('Amplitude'))
		self.pwin.disableAutoRange()
		self.pwin.setXRange(self.FMIN, self.FMAX)
		self.pwin.setYRange(0, self.RangeVals12[self.Range])
		self.pwin.hideButtons()								# Do not show the 'A' button of pg

		right = QVBoxLayout()							# right side vertical layout
		right.setAlignment(Qt.AlignmentFlag(0x0020)) #Qt.AlignTop
		right.setSpacing(self.RPGAP)

		H = QHBoxLayout()
		l = QLabel(text=self.tr('WG range '))
		l.setMaximumWidth(100)
		H.addWidget(l) 
		self.Xslider = utils.slider(0, len(self.Wgains)-1, self.wgainindex, 100, self.select_amplitude)
		H.addWidget(self.Xslider)
		self.amplitudeLabel = QLabel(text=self.tr(self.Wgains[self.wgainindex]))
		self.amplitudeLabel.setMaximumWidth(60)
		self.amplitudeLabel.setMinimumWidth(40)
		H.addWidget(self.amplitudeLabel)
		right.addLayout(H)
		
		H = QHBoxLayout()
		l = QLabel(text=self.tr('A2 range'))
		l.setMaximumWidth(100)
		H.addWidget(l) 
		self.Xslider = utils.slider(0, len(self.RangeVals12)-1, self.Range, 100, self.select_range)
		H.addWidget(self.Xslider)
		self.rangeLabel = QLabel(text=self.tr(self.Ranges12[self.Range]))
		self.rangeLabel.setMaximumWidth(60)
		self.rangeLabel.setMinimumWidth(40)
		H.addWidget(self.rangeLabel)
		right.addLayout(H)
		
		H = QHBoxLayout()
		l = QLabel(text=self.tr('Starting'))
		l.setMaximumWidth(70)
		H.addWidget(l)
		self.AWGstart = utils.lineEdit(60, self.FMIN, 6, None)
		H.addWidget(self.AWGstart)
		l = QLabel(text=self.tr('Hz'))
		l.setMaximumWidth(20)
		H.addWidget(l)
		right.addLayout(H)

		H = QHBoxLayout()
		l = QLabel(text=self.tr('Ending'))
		l.setMaximumWidth(70)
		H.addWidget(l)
		self.AWGstop = utils.lineEdit(60, self.FMAX, 6, None)
		H.addWidget(self.AWGstop)
		l = QLabel(text=self.tr('Hz'))
		l.setMaximumWidth(20)
		H.addWidget(l)
		right.addLayout(H)
		 
		H = QHBoxLayout()
		l = QLabel(text=self.tr('Steps'))
		l.setMaximumWidth(70)
		H.addWidget(l)
		self.NSTEPtext = utils.lineEdit(60, self.NSTEP, 6, None)
		H.addWidget(self.NSTEPtext)
		l = QLabel(text=self.tr(''))
		l.setMaximumWidth(20)
		H.addWidget(l)
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
	def select_amplitude(self,index):
		self.wgainindex = index
		try:
			self.p.set_sine_amp(self.wgainindex)
			print (index)
		except:
			self.comerr()
			return		
		self.amplitudeLabel.setText(self.Wgains[self.wgainindex])
				
	def select_range(self,index):
		self.Range = index
		x = self.Ranges12[self.Range]
		try:
			self.p.select_range('A2', self.RangeVals12[self.Range])
		except:
			self.comerr()
			return		
		self.rangeLabel.setText(self.Ranges12[self.Range])
		self.pwin.setYRange(0, self.RangeVals12[self.Range])

	def verify_fit(self,y,y1):
		sum = 0.0
		for k in range(len(y)):
			sum += abs((y[k] - y1[k])/y[k])
		err = sum/len(y)
		if err > .5:
			return False
		else:
			return True

	def analyze(self, data):
		freq = data[0]
		amp = data[1]
		N = len(freq)
		peak = np.argmax(amp)
		fp = freq[peak]
		ap = amp[peak]
		'''
		for k in range(peak):
			if amp[k] >= ap/2:
				f1 = freq[k]
				a1 = amp[k]
				break
		for k in range(peak, len(freq)):
			if amp[k] <= ap/2:
				f2 = freq[k]
				a2 = amp[k]
				break
		q = (f2-f1)/fp
		'''
		self.msg(self.tr('Peak = %5.3f V at %4.1f Hz.'%(ap, fp)))	
				
		
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
				t,v = self.p.capture1('A2', NP, int(self.TG))	
			except:
				self.comerr()
				return 
			try:
				fa = em.fit_sine(t,v)
				if self.verify_fit(v,fa[0]) == False:	#compare trace with the fitted curve
					continue
			except:
				self.msg(self.tr('Fit failed'))	
				continue
				
			if fa != None:
				self.data[0].append(fr)
				self.data[1].append(abs(fa[1][0]))
				break
		
		self.FREQ += self.STEP
		if self.FREQ > self.FMAX:
			self.running = False
			self.history.append(self.data)
			self.traces.append(self.currentTrace)
			self.analyze(self.data)
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
		self.STEP = (self.FMAX - self.FMIN)/ self.NSTEP

		try:	
			self.p.select_range('A1',4)
			self.p.select_range('A2', self.RangeVals12[self.Range])	
			self.p.set_sine(1000)
			t,v = self.p.capture1('A1', 1000, 5)	
		except:
			self.comerr()
			return 
		try:
			fa = em.fit_sine(t,v)
			amplitude = abs(fa[1][0])
			self.msg(self.tr('Starting. Input Vp = %4.2f Volts at 1kHz'%amplitude))	
		except:
			self.msg(self.tr('fit err.No proper input on A1'))	
			
		self.running = True
		self.data = [ [], [] ]
		self.FREQ = self.FMIN
		self.currentTrace = self.pwin.plot([0,0],[0,0], pen = self.traceCols[self.trial%5])
		self.index = 0
		self.trial += 1
		self.gainMax = 0.0


	def stop(self):
		if self.running == False: return
		self.running = False
		self.history.append(self.data)
		self.traces.append(self.currentTrace)
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
	
