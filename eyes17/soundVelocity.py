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
	AWGval = 3500

	tbvals = [0.100, 0.200, 0.500]	# allowed mS/div values
	NP = 500			# Number of samples
	TG = 1				# Number of channels
	MINDEL = 1			# minimum time between samples, in usecs
	MAXDEL = 1000
	delay = MINDEL		# Time interval between samples
	TBval = 1			# timebase list index
	
	TMAX = 1
	VMIN = -5
	VMAX = 5
	MAXCHAN = 2
	timeData    = [None]*MAXCHAN
	voltData    = [None]*MAXCHAN
	voltDataFit = [None]*MAXCHAN
	traceWidget = [None]*MAXCHAN
	traceWidget = [None]*MAXCHAN
	#history = []		# Data store	
	measured = False
	
	NP = 500			# Number of samples
	TG = 1				# Number of channels
	trial = 0
	
	def __init__(self, device=None):
		QWidget.__init__(self)
		self.p = device										# connection to the device hardware 
		self.traceCols = utils.makeTraceColors()
		try:
			self.p.configure_trigger(0, 'A1', 0)
			self.p.select_range('A1',4.0)
			self.p.set_sine(0)
		except:
			pass

		self.pwin = pg.PlotWidget()							# pyqtgraph window
		self.pwin.showGrid(x=True, y=True)					# with grid
		ax = self.pwin.getAxis('bottom')
		ax.setLabel(self.tr('Time (mS)'))	
		ax = self.pwin.getAxis('left')
		ax.setLabel(self.tr('Voltage'))
		self.pwin.disableAutoRange()
		self.pwin.setXRange(0, self.TMAX)
		self.pwin.setYRange(self.VMIN, self.VMAX)
		self.pwin.hideButtons()								# Do not show the 'A' button of pg

		for ch in range(self.MAXCHAN):							# initialize the pg trace widgets
			self.traceWidget[ch] = self.pwin.plot([0,0],[0,0], pen = self.traceCols[ch])

		right = QVBoxLayout()							# right side vertical layout
		right.setAlignment(Qt.AlignmentFlag(0x0020)) #Qt.AlignTop
		right.setSpacing(self.RPGAP)				


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
		l = QLabel(text=self.tr('Timebase'))
		l.setMaximumWidth(60)
		H.addWidget(l)
		self.TBslider = utils.slider(0, len(self.tbvals)-1, self.TBval, 150, self.set_timebase)
		H.addWidget(self.TBslider)
		l = QLabel(text=self.tr('mS/div'))
		l.setMaximumWidth(60)
		H.addWidget(l)
		right.addLayout(H)

		self.enable = QCheckBox(self.tr('Enable Measurements'))
		right.addWidget(self.enable)
		self.enable.stateChanged.connect(self.control)

		self.SaveButton = QPushButton(self.tr("Save Data"))
		self.SaveButton.clicked.connect(self.save_data)		
		right.addWidget(self.SaveButton)

		H = QHBoxLayout()
		self.Res = QLabel(text='')
		#Res.setMaximumWidth(60)
		H.addWidget(self.Res)
		right.addLayout(H)
		
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
		

		#----------------------------- end of init ---------------
	
	def control(self):
		try:	
			if self.enable.isChecked() == False:
				self.p.set_sine(0)
			else:
				self.p.set_sine(self.AWGval)
		except:
			self.comerr()
			return
			
	def update(self):
		if self.enable.isChecked() == False:
			return
		try:
			tvs = self.p.capture4(self.NP, self.TG)
			self.timeData[0] = tvs[0]
			self.voltData[0] = tvs[1]
			self.timeData[1] = tvs[6]   # MIC channel
			self.voltData[1] = -tvs[7]			
			for ch in range(self.MAXCHAN):
				self.traceWidget[ch].setData(self.timeData[ch], self.voltData[ch])		
			self.measured = True
		except:
			self.comerr()
			
		try:
			fa = em.fit_sine(self.timeData[0], self.voltData[0])
		except Exception as err:
			print('fit_sine error:', err)
			fa=None
		if fa != None:	
			try:
				fb = em.fit_sine(self.timeData[1], self.voltData[1])
			except Exception as err:
				print('fit_sine error:', err)
				fb=None
			pa = fa[1][2] * 180/em.pi
			pb = fb[1][2] * 180/em.pi
			pdiff = pa-pb
			if fb[1][0] < 0: pdiff = 180 - pdiff
			ss = '%5.1f'%pdiff
			self.Res.setText(self.tr('Phase Shift = ') + ss + self.tr(' Hz'))
	
			
	def save_data(self):
		if self.enable.isChecked() == True:
			self.msg(self.tr('Disable before Saving'))
			return
		if self.measured == False: 
			self.msg(self.tr('No data to save'))
			return
		fn = QFileDialog.getSaveFileName()
		if fn != '':
			dat = []
			for ch in range(2):
					dat.append( [self.timeData[ch], self.voltData[ch] ])
			self.p.save(dat,fn)
			ss = fn
			self.msg(self.tr('Trace saved to ') + ss)			
			
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
			ss = '%6.2f Hz'%res
			self.msg(self.tr('AWG set to ') + ss + self.tr(' Hz'))
		except:
			self.comerr()
			return

	def awg_text(self, text):
		val = float(text)
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
	
