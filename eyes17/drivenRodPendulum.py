# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
import sys, time, math, os.path
import utils

from QtVersion import *

import pyqtgraph as pg
import numpy as np
import eyes17.eyemath17 as em
import utils

class Expt(QWidget):
	TIMER = 5
	RPWIDTH = 300
	RPGAP = 4
	running = False
	
	NMIN = 0
	NMAX = 10
	TMIN = 0
	TMAX = 2000		# milliseconds
	data = [ [], [] ]
	currentTrace = None
	traces = []
	history = []		# Data store	
	sources = ['A1','A2','A3', 'MIC']
	trial = 0
	
	def __init__(self, device=None):
		QWidget.__init__(self)
		self.p = device										# connection to the device hardware 

		self.traceCols = utils.makeTraceColors()
		
		self.pwin = pg.PlotWidget()							# pyqtgraph window
		self.pwin.showGrid(x=True, y=True)					# with grid
		ax = self.pwin.getAxis('bottom')
		ax.setLabel(self.tr('Trials'))	
		ax = self.pwin.getAxis('left')
		ax.setLabel(self.tr('Time Period (mSec)'))
		self.pwin.disableAutoRange()
		self.pwin.setXRange(self.NMIN, self.NMAX)
		self.pwin.setYRange(self.TMIN, self.TMAX)
		self.pwin.hideButtons()								# Do not show the 'A' button of pg

		right = QVBoxLayout()							# right side vertical layout
		right.setAlignment(Qt.AlignmentFlag(0x0020)) #Qt.AlignTop
		right.setSpacing(self.RPGAP)

		'''
		b = QPushButton(self.tr("Analyze last Trace"))
		right.addWidget(b)
		b.clicked.connect(self.fit_curve)		
		'''
		
		H = QHBoxLayout()
		l = QLabel(text=self.tr('Pendulum length'))
		l.setMaximumWidth(110)
		H.addWidget(l)
		self.PLENtext = utils.lineEdit(40, self.NMAX, 6, None)
		H.addWidget(self.PLENtext)
		l = QLabel(text=self.tr('cm'))
		l.setMaximumWidth(20)
		H.addWidget(l)
		right.addLayout(H)

		b = QPushButton(self.tr("Clear Data and Traces"))
		right.addWidget(b)
		b.clicked.connect(self.clear)		

		self.SaveButton = QPushButton(self.tr("Save Data"))
		self.SaveButton.clicked.connect(self.save_data)		
		right.addWidget(self.SaveButton)

		b = QPushButton(self.tr("Start"))
		right.addWidget(b)
		b.clicked.connect(self.start)		
		
		b = QPushButton(self.tr("Stop"))
		right.addWidget(b)
		b.clicked.connect(self.stop)		

		H = QHBoxLayout()
		l = QLabel(text=self.tr('Set SQ1'))
		H.addWidget(l)
		self.SQ1slider = utils.slider(100, 10000, 2000, 1000,self.sq1_slider)
		H.addWidget(self.SQ1slider)
		right.addLayout(H)

		H = QHBoxLayout()
		l = QLabel(text=self.tr('Set WG'))
		H.addWidget(l)
		self.SINEslider = utils.slider(100, 10000, 2000, 1000,self.sine_slider)
		H.addWidget(self.SINEslider)
		right.addLayout(H)

					
		H = QHBoxLayout()
		l = QLabel(text=self.tr('Number of trials'))
		l.setMaximumWidth(110)
		H.addWidget(l)
		self.NMAXtext = utils.lineEdit(40, self.NMAX, 6, None)
		H.addWidget(self.NMAXtext)
		right.addLayout(H)

		H = QHBoxLayout()
		self.Results = QTextEdit()	
		self.Results.setMaximumWidth(self.RPWIDTH/2-5)
		H.addWidget(self.Results)
		self.gResults = QTextEdit()	
		self.gResults.setMaximumWidth(self.RPWIDTH/2-5)
		H.addWidget(self.gResults)
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
	
	def fit_curve(self):
		if self.running == True or self.data[0]==[]:
			return
		return
		# Make histogram to be added

		if (len(self.data[0])%2) == 1:			# make it an even size, for fitting
			self.data[0] = self.data[0][:-1]
			self.data[1] = self.data[1][:-1]
			
		fa = em.fit_dsine(self.data[0], self.data[1])
		if fa != None:
			pa = fa[1]
			self.traces.append(self.pwin.plot(self.data[0], fa[0], pen = self.traceCols[self.trial%5]))
			self.trial += 1
			ss1 = '%5.2f'%pa[1]
			ss2 = '%5.3f'%pa[4]
			self.msg(self.tr('Frequency of Oscillation = ') +  ss1 + self.tr(' Hz. Damping Factor = ') + ss2)
		else:
			self.msg(self.tr('Analysis failed. Could not fit data'))

	def sq1_slider(self, val):
		try:
			res = self.p.set_sqr1(val*0.001)
			ss = '%5.2f'%res
			self.msg(self.tr('sqr1 set to ') + ss + self.tr(' Hz'))
		except:
			self.comerr()

	def sine_slider(self, val):
		try:
			res = self.p.set_sine(val*0.001)
			ss = '%5.2f'%res
			self.msg(self.tr('sqr1 set to ') + ss + self.tr(' Hz'))
		except:
			self.comerr()

				
	def update(self):
		if self.running == False:
			return
		if self.p == None:
			self.comerr()
			return
		try:
			T = self.p.multi_r2rtime('SEN', 2,5)
		except:
			self.comerr()
		
		if T < 0:
			s = self.tr('Timeout')
			gs = '--'
		else:
			s ='%f'%T
			gs = '%5.0f'%(8*math.pi**2*self.PLEN/3/T**2)
		self.Results.append(self.tr(s))
		self.gResults.append(self.tr(gs))
 
		T *= 1000			#seconds  to milliseconds
		self.data[0].append(self.index)
		self.data[1].append(T)
		if self.index >= self.NMAX:
			self.running = False
			self.history.append(self.data)
			self.traces.append(self.currentTrace)
			self.msg(self.tr('Completed'))
			return
		if self.index > 1:			  # Draw the line
			self.currentTrace.setData(self.data[0], self.data[1])
		self.index += 1


	def start(self):
		if self.p == None:
			self.comerr()
			return
		
		if self.running == True: return
		try:
			val = float(self.NMAXtext.text())
		except:
			self.msg(self.tr('Invalid Number of trials'))
			return
		self.NMAX = val
		try:
			val = float(self.PLENtext.text())
		except:
			self.msg(self.tr('Invalid Length'))
			return
		self.PLEN = val

		try:
			self.p.set_state(SQR2=1)						# Light the LED
			T = self.p.multi_r2rtime('SEN', 2)		# Timeout in first call ??
		except:
			self.mcomerr()
		
		self.pwin.setXRange(self.NMIN, self.NMAX)
		self.pwin.setYRange(self.TMIN, self.TMAX)
		self.running = True
		self.data = [ [], [] ]
		self.currentTrace = self.pwin.plot([0,0],[0,0], pen = self.traceCols[self.trial%5])
		self.index = 0
		self.trial += 1
		self.p.set_state(SQR2=1)
		self.msg(self.tr('Started Measurements'))
		

	def stop(self):
		if self.running == False: return
		self.running = False
		self.history.append(self.data)
		self.traces.append(self.currentTrace)
		try:
			self.p.set_sqr1(-1)						# trurn off the LED
			self.msg(self.tr('User Stopped'))
		except:
			self.comerr()

	def clear(self):
		for k in self.traces:
			self.pwin.removeItem(k)
		self.history = []
		self.trial = 0
		self.Results.setText('')
		self.gResults.setText('')
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
	
