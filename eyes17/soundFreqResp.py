# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
import sys, time, math, os.path
import utils

from QtVersion import *

import pyqtgraph as pg
import numpy as np
import eyes17.eyemath17 as em


class Expt(QWidget):
	MINTIMER = 85
	TIMER = MINTIMER
	RPWIDTH = 300
	RPGAP = 4
	running = False
	AWGmin = 1
	AWGmax = 5000
	AWGval = 1000
	
	FMIN = 1000
	FMAX = 4000
	FREQ = FMIN
	STEP = 20
	VMIN = 0		# filter amplitude Gain
	VMAX = 4.0
	data = [ [], [] ]
	currentTrace = None
	traces = []
	history = []		# Data store	
	sources = ['A1','A2','A3', 'MIC']
	trial = 0
	
	def __init__(self, device=None):
		QWidget.__init__(self)
		self.p = device								# connection to the device hardware 
		try:
			self.p.configure_trigger(0, 'A1', 0)
			self.p.select_range('A1',4.0)
		except:
			pass
		self.traceCols = utils.makeTraceColors()
			
		self.pwin = pg.PlotWidget()							# pyqtgraph window
		self.pwin.showGrid(x=True, y=True)					# with grid
		ax = self.pwin.getAxis('bottom')
		ax.setLabel(self.tr('Frequency (Hz)'))	
		ax = self.pwin.getAxis('left')
		ax.setLabel(self.tr('Amplitude (V)'))
		self.pwin.disableAutoRange()
		self.pwin.setXRange(self.FMIN, self.FMAX)
		self.pwin.setYRange(self.VMIN, self.VMAX)
		self.pwin.hideButtons()								# Do not show the 'A' button of pg

		right = QVBoxLayout()							# right side vertical layout
		right.setAlignment(Qt.AlignmentFlag(0x0020)) #Qt.AlignTop
		right.setSpacing(self.RPGAP)
		 
		H = QHBoxLayout()
		l = QLabel(text=self.tr('Starting'))
		l.setMaximumWidth(80)
		H.addWidget(l)
		self.AWGstart = utils.lineEdit(60, self.FMIN, 6, None)
		H.addWidget(self.AWGstart)
		l = QLabel(text=self.tr('Hz'))
		l.setMaximumWidth(30)
		H.addWidget(l)
		right.addLayout(H)

		H = QHBoxLayout()
		l = QLabel(text=self.tr('Ending'))
		l.setMaximumWidth(80)
		H.addWidget(l)
		self.AWGstop = utils.lineEdit(60, self.FMAX, 6, None)
		H.addWidget(self.AWGstop)
		l = QLabel(text=self.tr('Hz'))
		l.setMaximumWidth(30)
		H.addWidget(l)
		right.addLayout(H)
		 
		H = QHBoxLayout()
		l = QLabel(text=self.tr('Total time'))
		l.setMaximumWidth(80)
		H.addWidget(l)
		self.totalTimeW = utils.lineEdit(60, 20, 6, None)
		H.addWidget(self.totalTimeW)
		l = QLabel(text=self.tr('Sec'))
		l.setMaximumWidth(30)
		H.addWidget(l)
		right.addLayout(H)

		b = QPushButton(self.tr("Start"))
		right.addWidget(b)
		b.clicked.connect(self.start)		
		
		H = QHBoxLayout()
		self.updateLabel = QLabel(text='')
		self.updateLabel.setMaximumWidth(200)
		H.addWidget(self.updateLabel)
		right.addLayout(H)

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
		if err/sum > 0.01:
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
		TG = 1.e6/self.FREQ/50   # 50 points per wave
		TG = int(TG)//2 * 2
		if TG > 500:
			TG = 500
		elif TG < 2:
			TG = 2
		NP = 500
		MAXTIME = 200000.  # .2 seconds
		if NP * TG > MAXTIME:
			NP = int(MAXTIME/TG)
		if NP % 2: NP += 1  # make it an even number
		
		goodFit = False
		for k in range(3):	          # try 3 times
			try:
				t,v   = self.p.capture1('MIC', NP, TG)	
			except:
				self.comerr()
				return
			try:
				fa = em.fit_sine(t,v)
			except Exception as err:
				print('fit_sine error:', err)
				fa=None
			if fa != None:
				if self.verify_fit(v,fa[0]) == False:	#compare trace with the fitted curve
					continue
				self.updateLabel.setText(self.tr('Frequency = %5.0f Hz V = %5.3f') %(fr,abs(fa[1][0])))
				self.data[0].append(fr)
				self.data[1].append(abs(fa[1][0]))
				goodFit = True
				break
		
		self.FREQ += self.STEP
		if goodFit == False:
			return

		if self.FREQ > self.FMAX:
			self.running = False
			elapsed = time.time() - self.startTime
			
			self.history.append(self.data)
			self.traces.append(self.currentTrace)
			try:
				self.p.set_sine(0)
				ss = '%5.1f'%elapsed
				self.msg(self.tr('Completed in ') + ss + self.tr(' Seconds'))
			except:
				self.comerr()
			return

		if self.index > 1:			  # Draw the line
			self.currentTrace.setData(self.data[0], self.data[1])
		self.index += 1


	def start(self):
		if self.running == True: return
		try:
			self.p.select_range('A1',4)
		except:
			self.comerr()
			return
		try:
			self.FMIN = float(self.AWGstart.text())
			self.FMAX = float(self.AWGstop.text())
		except:
			self.msg(self.tr('Invalid Frequency limits'))
			return
			
		try:
			self.totalTime = float(self.totalTimeW.text())
		except:
			self.msg(self.tr('Invalid Time interval'))
			return

		nstep = (self.FMAX - self.FMIN)/self.STEP
		tgap = self.totalTime*1000/nstep
		mt = nstep * self.MINTIMER /1000 + 1
		
		if tgap > self.MINTIMER:
			self.TIMER = tgap	
			self.timer.stop()
			self.timer.start(self.TIMER)
		else:
			ss = '%4.0f'%mt
			self.msg(self.tr('Increase time interval to ') + ss + self.tr(' or Reduce frequency span'))
			return
			
		self.pwin.setXRange(self.FMIN, self.FMAX)
		self.pwin.setYRange(self.VMIN, self.VMAX)
		self.running = True
		self.data = [ [], [] ]
		self.FREQ = self.FMIN
		self.currentTrace = self.pwin.plot([0,0],[0,0], pen = self.traceCols[self.trial%5])
		self.index = 0
		self.trial += 1
		ss = '%4.0f'%tgap
		self.msg(ss + self.tr(' mS at each step'))
		self.startTime = time.time()


	def stop(self):
		if self.running == False: return
		self.running = False
		self.history.append(self.data)
		self.traces.append(self.currentTrace)
		self.msg(self.tr('User Stopped'))
		try:
			self.p.set_sine(0)
		except:
			self.comerr()

	def clear(self):
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
			self.msg(self.tr('No Traces available for saving'))
			return
		fn = QFileDialog.getSaveFileName()
		if fn != '':
			self.p.save(self.history, fn)
			ss = fn
			self.msg(self.tr('Traces saved to ') + ss)

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
	
