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
	PV1min = -5.0
	PV1max = 5.0
	PV1val = 2.
	
	VLLIM = -5  # maximum limits
	VULIM = 5
	ILLIM = -5  # maximum limits
	IULIM =  5
	
	VMIN = -5.0
	VMAX =  5.0
	VSET = VMIN
	STEP = 0.050	   # 50 mV
	Res = 1000
	IMIN = 5
	IMAX = 5
	data = [ [], [] ]
	currentTrace = None
	traces = []
	history = []		# Data store	
	#sources = ['A1','A2','A3', 'MIC']
	trial = 0
	
	def __init__(self, device=None):
		QWidget.__init__(self)
		self.p = device										# connection to the device hardware 
		self.traceCols = utils.makeTraceColors()
		
		self.pwin = pg.PlotWidget()							# pyqtgraph window
		self.pwin.showGrid(x=True, y=True)					# with grid
		ax = self.pwin.getAxis('bottom')
		ax.setLabel(self.tr('Current through R (mA)'))	
		ax = self.pwin.getAxis('left')
		ax.setLabel(self.tr('Voltage across R(Volts)'))
		self.pwin.disableAutoRange()
		self.IMIN = self.VMIN / self.Res
		self.IMAX = self.VMAX / self.Res
		self.pwin.setXRange(self.IMIN, self.IMAX)
		self.pwin.setYRange(self.VMIN, self.VMAX)
		self.pwin.hideButtons()								# Do not show the 'A' button of pg

		right = QVBoxLayout()							# right side vertical layout
		right.setAlignment(Qt.AlignmentFlag(0x0020)) #Qt.AlignTop
		right.setSpacing(self.RPGAP)
					
		H = QHBoxLayout()
		l = QLabel(self.tr("R to Ground"))
		l.setMaximumWidth(120)
		H.addWidget(l)
		self.Rval = utils.lineEdit(50, self.Res, 10, None)
		H.addWidget(self.Rval)
		l = QLabel(self.tr("Ohm"))
		l.setMaximumWidth(30)
		H.addWidget(l)
		right.addLayout(H)

		
		H = QHBoxLayout()
		l = QLabel(self.tr("Starting PV1"))
		l.setMaximumWidth(120)
		H.addWidget(l)
		self.PVmin = utils.lineEdit(40, self.VMIN, 10, None)
		H.addWidget(self.PVmin)
		l = QLabel(self.tr("V"))
		l.setMaximumWidth(30)
		H.addWidget(l)
		right.addLayout(H)

		H = QHBoxLayout()
		l = QLabel(self.tr("Ending PV1"))
		l.setMaximumWidth(120)
		H.addWidget(l)
		self.PVmax = utils.lineEdit(40, self.VMAX, 10, None)
		H.addWidget(self.PVmax)
		l = QLabel(self.tr("V"))
		l.setMaximumWidth(30)
		H.addWidget(l)
		right.addLayout(H)
		
		H = QHBoxLayout()		 
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

		self.Manual = QLabel(self.tr("Change Voltage"))
		right.addWidget(self.Manual)

		self.PV1slider = utils.slider(0, 30, 0, 250, self.pv1_slider)
		right.addWidget(self.PV1slider)

		H = QHBoxLayout()
		self.Voltage = QLabel(self.tr('Voltage = %5.3f') %self.PV1min)
		H.addWidget(self.Voltage)
		right.addLayout(H)

		H = QHBoxLayout()
		self.Current = QLabel(self.tr("Current = 0 mA"))
		H.addWidget(self.Current)
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
		
		
	def pv1_slider(self, pos):
		res = float(self.Rval.text())		# Reference register
		sval = float(pos)
		val = self.PV1min + pos*(self.PV1max-self.PV1min)/30
		self.p.set_pv1(val)
		a1 = self.p.get_voltage('A1')
		volt = val- a1
		self.Voltage.setText(self.tr('Voltage = %5.3f V') %volt)
		i = a1/res *1000
		self.Current.setText(self.tr('Current = %5.3f mA') %i)
	
	
	def fit_curve(self):
		if self.running == True or self.data[0]==[]:
			return
		x = self.data[0]
		data = self.data[1]
		xbar = np.mean(x)
		ybar = np.mean(data)
		b = np.sum(data*(x-xbar)) / np.sum(x*(x-xbar))
		a = ybar - xbar * b
		ss = '%5.0f'%(b*1000)
		self.msg(self.tr('Slope of the Line (dV/dI) = ') + ss)
	
				
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
		
		i = va/self.Res * 1000 		   # in mA
		vr = vs-va
		if i == i and vr == vr and abs(vr) > 0.04:   # Reject NaN and very small values
			self.data[0].append(i)
			self.data[1].append(vs-va)
		
		self.VSET += self.STEP
		if self.VSET > self.VMAX:
			self.running = False
			self.history.append(self.data)
			self.traces.append(self.currentTrace)
			self.fit_curve()
			self.manual()
			return
		if self.index > 1:			  # Draw the line
			self.currentTrace.setData(self.data[0], self.data[1])
		self.index += 1


	def manual(self):
		if self.running == True:
			self.PV1slider.hide()
			self.Voltage.hide()
			self.Current.hide()
			self.Manual.hide()
		else:
			self.PV1slider.show()
			self.Voltage.show()
			self.Current.show()	
			self.Manual.show()

	def start(self):
		if self.running == True: return
		try:
			self.Res = float(self.Rval.text())
			self.VMIN = float(self.PVmin.text())
			self.VMAX = float(self.PVmax.text())
		except:
			self.msg(self.tr('Err'))
			return
		
		self.IMIN = self.VMIN / self.Res
		self.IMAX = self.VMAX / self.Res
		self.pwin.setXRange(self.ILLIM, self.IULIM)
		self.pwin.setYRange(self.VLLIM, self.VULIM)
		self.running = True
		self.data = [ [], [] ]
		self.VSET = self.VMIN
		self.currentTrace = self.pwin.plot([0,0],[0,0], pen = self.traceCols[self.trial%5])
		self.index = 0
		self.trial += 1
		self.msg(self.tr('Started'))
		self.manual()

	def stop(self):
		if self.running == False: return
		self.PV1slider.show()
		self.Voltage.show()
		self.Current.show()
		self.running = False
		self.history.append(self.data)
		self.traces.append(self.currentTrace)
		self.msg(self.tr('User Stopped'))
		self.manual()
		
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
	
