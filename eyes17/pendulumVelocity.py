# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
import sys, time, math, os.path
import utils

from QtVersion import *

import pyqtgraph as pg
import numpy as np
import eyes17.eyemath17 as em


class Expt(QWidget):
	TIMER = 5
	RPWIDTH = 300
	RPGAP = 4
	running = False
	
	VMIN = -5
	VMAX = 5
	TMIN = 0
	TMAX = 5
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
			self.p.configure_trigger(0, 'A1', 0)
		except:
			pass	
				
		self.traceCols = utils.makeTraceColors()

		self.pwin = pg.PlotWidget()							# pyqtgraph window
		self.pwin.showGrid(x=True, y=True)					# with grid
		ax = self.pwin.getAxis('bottom')
		ax.setLabel(self.tr('Time (mS)'))	
		ax = self.pwin.getAxis('left')
		ax.setLabel(self.tr('Voltage (V)'))
		self.pwin.disableAutoRange()
		self.pwin.setXRange(self.TMIN, self.TMAX)
		self.pwin.setYRange(self.VMIN, self.VMAX)
		self.pwin.hideButtons()								# Do not show the 'A' button of pg

		right = QVBoxLayout()							# right side vertical layout
		right.setAlignment(Qt.AlignmentFlag(0x0020)) #Qt.AlignTop
		right.setSpacing(self.RPGAP)
					
		H = QHBoxLayout()
		l = QLabel(text=self.tr('Duration'))
		l.setMaximumWidth(80)
		H.addWidget(l)
		self.TMAXtext = utils.lineEdit(40, self.TMAX, 6, None)
		H.addWidget(self.TMAXtext)
		l = QLabel(text=self.tr('Seconds'))
		l.setMaximumWidth(60)
		H.addWidget(l)
		right.addLayout(H)

		b = QPushButton(self.tr("Start"))
		right.addWidget(b)
		b.clicked.connect(self.start)		
		
		b = QPushButton(self.tr("Stop"))
		right.addWidget(b)
		b.clicked.connect(self.stop)		
		
		b = QPushButton(self.tr("Analyze last Trace"))
		right.addWidget(b)
		b.clicked.connect(self.fit_curve)		

		b = QPushButton(self.tr("Clear Traces"))
		right.addWidget(b)
		b.clicked.connect(self.clear)		

		self.SaveButton = QPushButton(self.tr("Save Data"))
		self.SaveButton.clicked.connect(self.save_data)		
		right.addWidget(self.SaveButton)


		l = QLabel(text=self.tr('\nSet SQ1 Frequency\nFor Driven Pendulum Expt.'))
		right.addWidget(l)

		self.SQ1slider = utils.slider(10, 1000, 100, 1000,self.sq1_slider)
		right.addWidget(self.SQ1slider)

		self.Freq = QLabel('')
		right.addWidget(self.Freq)

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
	
	def sq1_slider(self, val):
		try:
			res = self.p.set_sqr1(val*0.01)
			ss = '%5.2f'%res
			self.msg(self.tr('sqr1 set to ') + ss + self.tr(' Hz'))
			self.Freq.setText(ss)
		except:
			self.comerr()
			
				
	def fit_curve(self):
		if self.running == True or self.data[0]==[]:
			return

		if (len(self.data[0])%2) == 1:			# make it an even size, for fitting
			self.data[0] = self.data[0][:-1]
			self.data[1] = self.data[1][:-1]
			
		fa = em.fit_dsine(self.data[0], self.data[1], 1000.0)   # fit in em expects khz
		if fa != None:
			pa = fa[1]
			self.traces.append(self.pwin.plot(self.data[0], fa[0], pen = self.traceCols[self.trial%5]))
			self.trial += 1
			ss1 = '%5.2f'%pa[1]
			ss2 = '%5.3f'%pa[4]
			self.msg(self.tr('Frequency of Oscillation = ') + ss1 + self.tr(' Hz. Damping Factor = ') + ss2)	
			self.history.append((self.data[0], fa[0]))	
		else:
			self.msg(self.tr('Analysis failed. Could not fit data'))
				
	def update(self):
		if self.running == False:
			return
		try:	
			t,v = self.p.get_voltage_time('A3')  		# Read A3
		except:
			self.comerr()
			return 
		
		if len(self.data[0]) == 0:
			self.start_time = t
			elapsed = 0
		else:
			elapsed = t - self.start_time

		self.data[0].append(elapsed)
		self.data[1].append(v)
		if elapsed > self.TMAX:
			self.running = False
			self.history.append(self.data)
			self.traces.append(self.currentTrace)
			self.msg(self.tr('Time Vs Angular velocity plot completed'))
			return
		if self.index > 1:			  # Draw the line
			self.currentTrace.setData(self.data[0], self.data[1])
		self.index += 1


	def start(self):
		if self.running == True: return
		try:
			val = float(self.TMAXtext.text())
		except:
			self.msg(self.tr('Invalid Duration'))
			return
		self.TMAX = val
		self.pwin.setXRange(self.TMIN, self.TMAX)
		self.pwin.setYRange(self.VMIN, self.VMAX)
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
	
