'''
Code for science experiments using expEYES-17 interface
Logs data from TSL2561 light sensor
Author  : Ajith Kumar B.P, bpajith@gmail.com
Date    : Aug-2017
License : GNU GPL version 3
'''

import sys, time, math, os.path
import utils

from eyes17.SENSORS import TSL2561

from QtVersion import *

import pyqtgraph as pg
import numpy as np
import eyes17.eyemath17 as em


class Expt(QWidget):
	TIMER = 5
	RPWIDTH = 300
	RPGAP = 4
	running = False
	MAXCHAN = TSL2561.TSL2561.NUMPLOTS
	timeData =  []
	lightData =  [[] for x in range(MAXCHAN)]
	chanSelCB = [None]*MAXCHAN
	traces = [None]*MAXCHAN
	selected = [0]*MAXCHAN
	LMIN = 0
	LMAX = 65535
	TMIN = 0
	TMAX = 10
	TGAP = 0.10
	currentTrace = None
	history = []		# Data store	

	sources = TSL2561.TSL2561.PLOTNAMES
	traceCols = []
	#resultCols = []
	htmlColors = []
	
	def __init__(self, device=None):
		QWidget.__init__(self)
		self.p = device		#connection to the device hardware 	
		self.t = TSL2561.connect(self.p.I2C)	
		self.t.setGain('16x')
		self.t.setTiming(0)

		self.resultCols = utils.makeResultColors()
		self.traceCols = utils.makeTraceColors()
		self.htmlColors = utils.makeHtmlColors()
		
		self.pwin = pg.PlotWidget()							# pyqtgraph window
		self.pwin.showGrid(x=True, y=True)					# with grid
		ax = self.pwin.getAxis('bottom')
		ax.setLabel(self.tr('Time (mS)'))	
		ax = self.pwin.getAxis('left')
		ax.setLabel(self.tr('Voltage(V)'))
		self.pwin.disableAutoRange()
		self.pwin.setXRange(self.TMIN, self.TMAX)
		self.pwin.setYRange(self.LMIN, self.LMAX)
		self.pwin.hideButtons()								# Do not show the 'A' button of pg

		for ch in range(self.MAXCHAN):
			self.traces[ch] = self.pwin.plot([0,0],[0,0], pen = self.traceCols[ch])
	
		right = QVBoxLayout()							# right side vertical layout
		right.setAlignment(Qt.AlignmentFlag(0x0020)) #Qt.AlignTop
		right.setSpacing(self.RPGAP)
	
		H = QHBoxLayout()
		l = QLabel(text=self.tr('Total Duration'))
		l.setMaximumWidth(100)
		H.addWidget(l)
		self.TMAXtext = utils.lineEdit(40, self.TMAX, 6, None)
		H.addWidget(self.TMAXtext)
		l = QLabel(text=self.tr('Seconds'))
		l.setMaximumWidth(60)
		H.addWidget(l)
		right.addLayout(H)

		H = QHBoxLayout()
		l = QLabel(text=self.tr('Measure every'))
		l.setMaximumWidth(100)
		H.addWidget(l)
		self.TGAPtext = utils.lineEdit(40, self.TGAP, 6, None)
		H.addWidget(self.TGAPtext)
		l = QLabel(text=self.tr('Seconds'))
		l.setMaximumWidth(60)
		H.addWidget(l)
		right.addLayout(H)

		for ch in range(self.MAXCHAN):
			H = QHBoxLayout()
			H.setAlignment(Qt.AlignmentFlag(0x1)) # Qt.AlignLeft
			self.chanSelCB[ch] = QCheckBox()
			#self.chanSelCB[ch].stateChanged.connect(partial (self.select_channel,ch))
			H.addWidget(self.chanSelCB[ch])
			l = QLabel(text='<font color="%s">%s' %(self.htmlColors[ch],self.sources[ch]))
			l.setMaximumWidth(30)
			l.setMinimumWidth(30)
			H.addWidget(l)
			right.addLayout(H)

		self.chanSelCB[0].setChecked(True)

		b = QPushButton(self.tr("Start"))
		right.addWidget(b)
		b.clicked.connect(self.start)		
		
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
		self.msgwin = QLabel(text=self.tr(''))
		full.addWidget(self.msgwin)
				
		self.setLayout(full)
		
		self.timer = QTimer()
		self.timer.timeout.connect(self.update)
		self.timer.start(self.TIMER)
		
		if TSL2561.TSL2561.ADDRESS not in self.p.I2C.scan():
			self.msg(self.tr('TSL2561 Sensor Not Found'))

		#----------------------------- end of init ---------------
	
	def update(self):
		if self.running == False:
			return

		t = time.time()
		if len(self.timeData) == 0:
			self.start_time = t
			elapsed = 0
		else:
			elapsed = t - self.start_time

		self.timeData.append(elapsed)
		
		try:
			vals = self.t.getRaw()
			for ch in range(self.MAXCHAN):
				if self.selected[ch] == True:
					self.lightData[ch].append(vals[ch])
					if len(self.timeData) > 1:
						self.traces[ch].setData(self.timeData, self.lightData[ch])
		except:
			self.comerr()
			
		if elapsed > self.TMAX:
			self.running = False
			self.msg(self.tr('Data logger plot completed'))
			return


	def start(self):
		if self.running == True: return
		try:
			self.TMAX = float(self.TMAXtext.text())
		except:
			self.msg(self.tr('Invalid Duration'))
			return
			
		try:
			self.TGAP = float(self.TGAPtext.text())
			self.TIMER = self.TGAP * 1000    # into mS
			self.timer.stop()
			self.timer.start(self.TIMER)
		except:
			self.msg(self.tr('Invalid time interval between reads'))
			return

		for ch in range(self.MAXCHAN):
			if self.chanSelCB[ch].isChecked() == True:
				self.selected[ch] = True
			else:
				self.selected[ch] = False

		self.pwin.setXRange(self.TMIN, self.TMAX)
		self.pwin.setYRange(self.LMIN, self.LMAX)
		self.timeData = []
		self.lightData =  [[] for x in range(self.MAXCHAN)]
		for ch in range(self.MAXCHAN):
			self.traces[ch].setData([0,0],[0,0], pen = self.traceCols[ch])
		self.running = True
		self.msg(self.tr('Started Measurements'))

	def stop(self):
		if self.running == False: return
		self.running = False
		self.msg(self.tr('User Stopped'))

	def clear(self):
		if self.running == True: return
		for ch in range(self.MAXCHAN):
			self.traces[ch].setData([0,0],[0,0], pen = self.traceCols[ch])
		self.timeData = []
		self.lightData =  [[] for x in range(self.MAXCHAN)]
		self.msg(self.tr('Cleared Traces and Data'))
		
	def save_data(self):
		fn = QFileDialog.getSaveFileName()
		if fn != '':
			dat = []
			for ch in range(self.MAXCHAN):
				if self.chanSelCB[ch].isChecked() == True:
					dat.append( [self.timeData, self.lightData[ch] ])
			self.p.save(dat,fn)
			self.msg(self.tr('Traces saved to ') + fn)
				
	def msg(self, m):
		self.msgwin.setText(self.tr(m))
		
	def comerr(self):
		self.msgwin.setText('<font color="red">' + self.tr('Error. Try Device->Reconnect'))

if __name__ == '__main__':
	import eyes17.eyes
	dev = eyes17.eyes.open()
	
	dev.set_pv1(0.120)
	dev.set_pv2(0.120)
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
	
