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
	AWGval = 200

	xvals = [2., 3.0, 4.0, 5.0, 10]	# allowed X values
	NP = 500			# Number of samples
	TG = 1				# Number of channels
	MINDEL = 1			# minimum time between samples, in usecs
	MAXDEL = 1000
	delay = MINDEL		# Time interval between samples
	Xval = 1			# timebase list index
	
	VMIN = -5
	VMAX = 5
	MAXCHAN = 1
	Data    = [ [], [] ]
	traceWidget = [None]
	

	NP = 500			# Number of samples
	TG = 10				# Number of channels
	
	def __init__(self, device=None):
		QWidget.__init__(self)
		self.p = device										# connection to the device hardware 

		try:
			self.p.select_range('A1',4)
			self.p.select_range('A2',4)
			self.p.set_sine(self.AWGval)
		except:
			pass

		self.traceCols = utils.makeTraceColors()

		self.pwin = pg.PlotWidget()							# pyqtgraph window
		self.pwin.showGrid(x=True, y=True)					# with grid
		ax = self.pwin.getAxis('bottom')
		ax.setLabel(self.tr('Voltage  A2'))	
		ax = self.pwin.getAxis('left')
		ax.setLabel(self.tr('Voltage (A2)'))
		self.pwin.disableAutoRange()
		self.pwin.setXRange(self.VMIN, self.VMAX)
		self.pwin.setYRange(self.VMIN, self.VMAX)


		for ch in range(self.MAXCHAN):							# initialize the pg trace widgets
			self.traceWidget[ch] = self.pwin.plot([0,0],[0,0], pen = self.traceCols[ch])


		self.pwin2 = pg.PlotWidget()		# pyqtgraph window
		self.pwin2.showGrid(x=True, y=True)	# with grid
		ax = self.pwin2.getAxis('bottom')
		ax.setLabel(self.tr('Voltage  A1'))	
		ax = self.pwin2.getAxis('left')
		ax.setLabel(self.tr('Voltage (A2)'))
		self.pwin2.disableAutoRange()
		self.pwin2.setXRange(self.VMIN, self.VMAX)
		self.pwin2.setYRange(self.VMIN, self.VMAX)
		self.curve2 = self.pwin2.plot([0,0],[0,0], pen = self.traceCols[ch])


		self.pwin3 = pg.PlotWidget()		# pyqtgraph window
		self.pwin3.showGrid(x=True, y=True)	# with grid
		ax = self.pwin3.getAxis('bottom')
		ax.setLabel(self.tr('Time'))	
		ax = self.pwin3.getAxis('left')
		ax.setLabel(self.tr('Voltage'))
		self.pwin3.disableAutoRange()
		self.pwin3.setXRange(0, int(self.NP*self.TG))
		self.pwin3.setYRange(self.VMIN, self.VMAX)
		self.datacurves={}
		for a in ['A1','A2','A3','MIC']:
			self.datacurves[a] = self.pwin3.plot([0,0],[0,0], pen = self.traceCols[ch])


		right = QVBoxLayout()				# right side vertical layout
		right.setAlignment(Qt.AlignTop)
		right.setSpacing(self.RPGAP)				

		H = QHBoxLayout()
		self.SaveButton = QPushButton(self.tr("Save Data to"))
		self.SaveButton.setMaximumWidth(90)
		self.SaveButton.clicked.connect(self.save_data)		
		H.addWidget(self.SaveButton)
		self.Filename = utils.lineEdit(150, self.tr('XYplot.txt'), 20, None )
		H.addWidget(self.Filename)
		right.addLayout(H)

		H = QHBoxLayout()
		l = QLabel(text=self.tr('WG'))
		l.setMaximumWidth(25)
		H.addWidget(l)
		self.AWGslider = utils.slider(self.AWGmin, self.AWGmax, self.AWGval,100,self.awg_slider)
		H.addWidget(self.AWGslider)
		self.AWGtext = utils.lineEdit(100, self.AWGval, 6, self.awg_text)
		H.addWidget(self.AWGtext)
		l = QLabel(text=self.tr('Hz'))
		l.setMaximumWidth(20)
		H.addWidget(l)
		right.addLayout(H)
		
		H = QHBoxLayout()
		l = QLabel(text=self.tr('Voltage range'))
		l.setMaximumWidth(100)
		H.addWidget(l)
		self.Xslider = utils.slider(0, len(self.xvals)-1, self.Xval, 100, self.set_range)
		H.addWidget(self.Xslider)
		l = QLabel(text=self.tr('Volts'))
		l.setMaximumWidth(60)
		H.addWidget(l)
		right.addLayout(H)

		self.Diffmode = QCheckBox(self.tr('show (A1-A2) Vs A2'))
		right.addWidget(self.Diffmode)
		self.Diffmode.stateChanged.connect(self.diff_mode)

		H = QHBoxLayout()
		self.Xmax = QLabel(text='')
		H.addWidget(self.Xmax)
		right.addLayout(H)
		
		H = QHBoxLayout()
		self.Ymax = QLabel(text='')
		H.addWidget(self.Ymax)
		right.addLayout(H)


		#------------------------end of right panel ----------------
		from PyQt4.QtGui import QGridLayout
		top = QGridLayout()
		top.addWidget(self.pwin,0,0) #A1 and A2
		top.addWidget(self.pwin2,1,0) #A3 and MIC
		top.addWidget(self.pwin3,0,1,2,1) #All signals
		top.addLayout(right,0,2)
		
		full = QVBoxLayout()
		full.addLayout(top)
		self.msgwin = QLabel(text=self.tr('messages'))
		full.addWidget(self.msgwin)
				
		self.setLayout(full)
		
		self.timer = QTimer()
		self.timer.timeout.connect(self.update)
		self.timer.start(self.TIMER)
		

		#----------------------------- end of init ---------------
				
	def diff_mode(self):
		ax = self.pwin.getAxis('left')
		if self.Diffmode.isChecked() == True:
			ax.setLabel(self.tr('Voltage (A1-A2)'))
		else:		
			ax.setLabel(self.tr('Voltage (A2)'))
				
	def update(self):
		try:
			tvs = self.p.capture4(self.NP, self.TG)
			#tvs = x*1e-3,y,x*1e-3,y2,x*1e-3,y3,x*1e-3,y4  
			self.Data[0] = tvs[3]    # A2
			if self.Diffmode.isChecked() == False:
				self.Data[1] = tvs[1]   # A1
			else:
				self.Data[1] = tvs[1] - tvs[3]  # A1-A2
			self.traceWidget[0].setData(self.Data[0], self.Data[1])		
			self.curve2.setData(tvs[7], tvs[5])		
			self.datacurves['A1'].setData(tvs[0],tvs[1])
			self.datacurves['A2'].setData(tvs[2],tvs[3])
			self.datacurves['A3'].setData(tvs[4],tvs[5])
			self.datacurves['MIC'].setData(tvs[6],tvs[7])

		except:
			self.comerr()
			self.Xmax.setText('')
			self.Ymax.setText('')
			return
	
	def save_data(self):
		fn = self.Filename.text()
		dat = []
		for ch in range(2):
				dat.append( [self.Data[0], self.Data[1] ])
		self.p.save(dat,fn)
		ss = self.tr(unicode(fn))
		self.msg(self.tr('Traces saved to ') + ss)
			
	def set_range(self, index):
		x = self.xvals[index]
		self.pwin.setXRange(-x, x)
		self.pwin.setYRange(-x, x)
		
	def set_wave(self):
		try:	
			res = self.p.set_sine(self.AWGval)
			ss = '%6.2f'%res
			self.msg(self.tr('AWG set to ') + ss + self.tr(' Hz'))
		except:
			self.comerr()
			return
		T = 1.0e6/res
		self.NP = 500
		self.TG = int(1+T/self.NP)
		if self.TG < self.MINDEL:
			self.TG = self.MINDEL
		elif self.TG > self.MAXDEL:
			self.TG = self.MAXDEL


	def awg_text(self, text):
		val = float(text)
		if self.AWGmin <= val <= self.AWGmax:
			self.AWGval = val
			self.AWGslider.setValue(self.AWGval)
			self.set_wave()

	def awg_slider(self, val):
		if self.AWGmin <= val <= self.AWGmax:
			self.AWGval = val
			self.AWGtext.setText(unicode(val))
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
	
