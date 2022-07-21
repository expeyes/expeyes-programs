# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
import sys, time, math, os.path
import utils

from QtVersion import *
	
import pyqtgraph as pg
import numpy as np
import eyes17.eyemath17 as em


class Expt(QWidget):
	TIMER = 20
	RPWIDTH = 300
	RPGAP = 4
	running = False
	
	TMIN = 0
	TMAX = 5
	DMIN = 0
	DMAX = 80
	DLIMIT = 80
	guessTP = 1.0     #time period guess
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
		ax.setLabel(self.tr('Time (Sec)'))	
		ax = self.pwin.getAxis('left')
		ax.setLabel(self.tr('Distance(cm)'))
		self.pwin.disableAutoRange()
		self.pwin.setXRange(self.TMIN, self.TMAX)
		self.pwin.setYRange(self.DMIN, self.DMAX)
		self.pwin.hideButtons()								# Do not show the 'A' button of pg

		right = QVBoxLayout()							# right side vertical layout
		right.setAlignment(Qt.AlignmentFlag(0x0020)) #Qt.AlignTop
		right.setSpacing(self.RPGAP)
					
		H = QHBoxLayout()
		l = QLabel(text=self.tr('Y-axis from 0 to'))
		l.setMaximumWidth(100)
		H.addWidget(l)
		self.DMAXtext = utils.lineEdit(40, self.DMAX, 6, None)
		H.addWidget(self.DMAXtext)
		l = QLabel(text=self.tr('cm'))
		l.setMaximumWidth(50)
		H.addWidget(l)
		right.addLayout(H)

		
		H = QHBoxLayout()
		l = QLabel(text=self.tr('Measure during'))
		l.setMaximumWidth(100)
		H.addWidget(l)
		self.TMAXtext = utils.lineEdit(40, self.TMAX, 6, None)
		H.addWidget(self.TMAXtext)
		l = QLabel(text=self.tr('Secs'))
		l.setMaximumWidth(50)
		H.addWidget(l)
		right.addLayout(H)

		
		b = QPushButton(self.tr("Start"))
		right.addWidget(b)
		b.clicked.connect(self.start)		
		
		b = QPushButton(self.tr("Stop"))
		right.addWidget(b)
		b.clicked.connect(self.stop)		
		
		b = QPushButton(self.tr("Fit Curve using Sine"))
		b.clicked.connect(self.fit_curve)		
		right.addWidget(b)
		
		b = QPushButton(self.tr("Clear Traces"))
		right.addWidget(b)
		b.clicked.connect(self.clear)		
		self.FFT = QPushButton(self.tr("Fourier Transform"))
		#self.FFT.setMaximumWidth(50)
		H.addWidget(self.FFT)
		self.FFT.clicked.connect(self.show_fft)		


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

	
	def fit_curve(self):
		if self.history != []:
			x = self.history[-1][0]
			y = self.history[-1][1]
			if len(x) % 2 != 0:
				x = x[:-1]
				y = y[:-1]
			fa = em.fit_dsine(np.array(x), np.array(y), 1000)# ./self.guessTP)  #Need to fix eyemath, expects kHz
		else:
			self.msg(self.tr('No data to analyze.'))
			return
			
		if fa != None:
			pa = fa[1]
			ss = '%5.2f'%pa[1]
			self.msg(self.tr('Sine Fit Result: Frequency ') + ss + self.tr( 'Hz'))
			self.traces.append(self.pwin.plot(x, fa[0], pen = self.traceCols[self.trial%5]))
			self.trial += 1
		else:
			self.msg(self.tr('Failed to fit the curve'))


	def show_fft(self):
		if self.history != []:
			x = self.history[-1][0]
			y = self.history[-1][1]
			if len(x) % 2 != 0:
				x = x[:-1]
				y = y[:-1]
			fa = em.fit_dsine(np.array(x), np.array(y), 1000)# ./self.guessTP)  #Need to fix eyemath, expects kHz
		else:
			self.msg(self.tr('No data to analyze.'))
			return
			
		if fa != None:
			if len(self.data[0])%2: #odd number
				self.data[0] = self.data[0][:-1]
				self.data[1] = self.data[1][:-1]
			pa = fa[1]
			ss = '%5.2f'%pa[1]
			self.msg(self.tr('Sine Fit Result: Frequency ') + ss + self.tr( 'Hz'))
			self.traces.append(self.pwin.plot(x, fa[0], pen = self.traceCols[self.trial%5]))

			fr = pa[1]			# frequency in Hz
			dt = np.average(np.diff(self.data[0]))*1000 #mS

			print('freq:%.2f, dt=%.2e'%(fr,dt))
			xa,ya = em.fft(self.data[1] - np.average(self.data[1]),dt)
			peak = self.peak_index(xa,ya)
			ypos = np.max(ya)
			pop = pg.plot(xa,ya, pen = self.traceCols[self.trial%5])
			pop.showGrid(x=True, y=True)
			txt = pg.TextItem(text=self.tr('Fundamental frequency = %5.1f Hz') %peak, color = 'w')
			txt.setPos(peak, ypos)
			pop.addItem(txt)
			pop.setWindowTitle(self.tr('Frequency Spectrum'))
			self.trial += 1

		else:
			self.msg(self.tr('Failed to fit the curve'))



		
	def peak_index(self, xa, ya):
		peak = 0
		peak_index = 0
		for k in range(2,len(ya)):
			if ya[k] > peak:
				peak = ya[k]
				peak_index = xa[k]
		return peak_index

				
	def update(self):
		if self.running == False:
			return
			
		try:
			t,D = self.p.sr04_distance_time()  # SR04 measurement
		except:
			self.comerr()
			return
			
		if len(self.data[0]) == 0:
			self.start_time = t
			elapsed = 0
		else:
			elapsed = t - self.start_time

		self.data[0].append(elapsed)
		self.data[1].append(D)
		if elapsed > self.TMAX:
			self.running = False
			self.history.append(self.data)
			self.traces.append(self.currentTrace)
			self.msg(self.tr('Time vs Distance plot completed'))
			return
		if self.index > 1:			  # Draw the line
			self.currentTrace.setData(self.data[0], self.data[1])
		self.index += 1


	def start(self):
		if self.running == True: return
		if self.p == None:
			self.comerr()
			return
		try:
			self.TMAX = float(self.TMAXtext.text())
		except:
			self.msg(self.tr('Invalid Duration'))
			return
		try:
			val = float(self.DMAXtext.text())
			if 5 < val <= self.DLIMIT:
				self.DMAX = val
			else:
				self.msg('Set maximum distance between 5cm and %d cm'%self.DLIMIT)	
				return			
		except:
			self.msg('Invalid Maximum Distance')
			return

		self.pwin.setXRange(self.TMIN, self.TMAX)
		self.pwin.setYRange(self.DMIN, self.DMAX)
		self.running = True
		self.data = [ [], [] ]
		self.currentTrace = self.pwin.plot([0,0],[0,0], pen = self.traceCols[self.trial%5])
		self.index = 0
		self.trial += 1
		self.msg(self.tr('Started Measurements'))

	def stop(self):
		if self.running == False: return
		self.running = False
		self.history.append(self.data)
		self.traces.append(self.currentTrace)
		self.msg(self.tr('User Stopped'))

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
	
