# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
import sys, time, math, os.path

from QtVersion import *

import sys, time, utils
import pyqtgraph as pg
import numpy as np
import eyes17.eyemath17 as em
from functools import partial


class Expt(QWidget):
	TIMER = 50
	loopCounter = 0
	AWGmin = 1
	AWGmax = 5000
	AWGval = 1000
	SQ1min = 0
	SQ1max = 5000
	SQ1val = 0
	PV1min = -5.0
	PV1max = 5.0
	PV1val = 0.0
	PV2min = -3.3
	PV2max = 3.3
	PV2val = 0.0
	Waves = ['sine', 'tria', 'SQR2']
	Wgains = ['80 mV', '1V', '3V']
	waveindex = 0
	wgainindex = 2
	
	RPVspacing = 3											# Right panel Widget spacing
	RPWIDTH = 300
	LABW = 60
		
	# Scope parameters
	MAXCHAN = 4
	Ranges12 = ['16 V', '8 V','4 V', '2.5 V', '1 V', '.5V']	# Voltage ranges for A1 and A2
	RangeVals12 = [16., 8., 4., 2.5, 1., 0.5]
	Ranges34 = ['4 V', '2 V', '1 V', '.5V']					# Voltage ranges for A3 and MIC
	RangeVals34 = [4,2,1,0.5]
	chanStatus  = [1,0,0,0]
	timeData    = [None]*4
	voltData    = [None]*4
	voltDataFit = [None]*4
	traceWidget = [None]*4
	offSliders  = [None]*4
	offValues   = [0] * 4
	DiffTraceW  = None
	fitResWidget= [None]*4
	chanSelCB   = [None]*4
	rangeSelPB  = [None]*4
	fitSelCB    = [None]*4
	fitResLab   = [None]*4
	fitFlags    = [0]*4
	Amplitude   = [0]*4
	Frequency   = [0]*4
	Phase       = [0]*4
	rangeVals   = [4]*4		# selected value of range
	rangeTexts  = ['4 V']*4		# selected value of range
	scaleLabs   = [None]*4  # display fullscale value inside pg
	voltMeters  = [None]*3
	voltMeterCB = [None]*3
	valueLabel = None
	
	sources = ['A1','A2','A3', 'MIC']	

	tbvals = [0.100, 0.200, 0.500, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0]	# allowed mS/div values
	NP = 500			# Number of samples
	TG = 1				# Number of channels
	MINDEL = 1			# minimum time between samples, in usecs
	MAXDEL = 1000
	delay = MINDEL		# Time interval between samples
	TBval = 1			# timebase list index
	Trigindex = 0
	Triglevel = 0
	dutyCycle = 50
	MAXRES = 5
	resLabs     = [None]*MAXRES
	Results     = [None]*MAXRES

		

	def recover(self):		# Recover the settings before it got disconnected
		try:
			self.control_od1()
			self.pv1_text('0')
			self.pv2_text('0')
			self.p.set_sqr1(self.SQ1val, self.dutyCycle)
			self.select_wave(self.waveindex)
			self.p.set_wave(self.AWGval)
			self.select_wgain(self.wgainindex)
			self.set_trigger(self.Triglevel*1000)
			self.p.set_sine(self.AWGval)
			self.p.configure_trigger(0, 'A1', 0)
			self.select_range((0,2))
			self.select_range((1,2))
			self.select_range((2,0))
			self.select_range((3,0))
		except:
			pass
		
	def cross_hair(self):
		if self.Cross.isChecked() == False:
			self.pwin.vLine.setPos(-1)
			self.pwin.hLine.setPos(-17)

	def updateTV(self, evt):
		if self.p == None: return
		pos = evt[0]  			## using signal proxy turns original arguments into a tuple
		if self.pwin.sceneBoundingRect().contains(pos):
			mousePoint = self.pwin.vb.mapSceneToView(pos)
			xval = mousePoint.x()

			if self.Cross.isChecked() == True:
				self.pwin.vLine.setPos(mousePoint.x())
				self.pwin.hLine.setPos(mousePoint.y())

			for k in range(self.MAXRES):
				self.pwin.removeItem(self.resLabs[k])
			
			t = self.timeData[0]
			index = 0
			for k in range(len(t)-1):		# find out Time at the cursor position
				if t[k] < xval < t[k+1]:
					index = k
			
			self.resLabs[0] = pg.TextItem(
				text= unicode(self.tr('Time: %6.2fmS ')) %t[index],
				color= self.resultCols[0]
			)
			self.resLabs[0].setPos(0, -11)
			self.pwin.addItem(self.resLabs[0])
			
			for k in range(self.MAXCHAN):
				if self.chanStatus[k] == 1:
					self.Results[k+1] = unicode(self.tr('%s:%6.2fV ')) %(self.sources[k],self.voltData[k][index])
					self.resLabs[k+1] = pg.TextItem(text= self.Results[k+1],	color= self.resultCols[k])
					self.resLabs[k+1].setPos(0, -12 - 1.0*k)
					self.pwin.addItem(self.resLabs[k+1])

			
	def set_offset(self, ch):
		self.offValues[ch] = self.offSliders[ch].value()
		
	def __init__(self, device=None):
		QWidget.__init__(self)
		
		self.resultCols = utils.makeResultColors()
		self.traceCols = utils.makeTraceColors()
		self.htmlColors = utils.makeHtmlColors()
		self.p = device						# connection to the device hardware 
			
		self.chanStatus = [1,0,0,0]			# PyQt problem. chanStatus somehow getting preserved ???		

		left = QVBoxLayout()				# right side vertical layout
		for ch in range(self.MAXCHAN):
			self.offSliders[ch] = utils.sliderVert(-4, 4, 0, 40, None)
			left.addWidget(self.offSliders[ch])
			self.offSliders[ch].valueChanged.connect(partial (self.set_offset,ch))
			self.offSliders[ch].setStyleSheet("border: 1px solid %s;"%self.htmlColors[ch])
		

		win = pg.GraphicsWindow()
		self.pwin = win.addPlot()
		self.pwin.proxy = pg.SignalProxy(self.pwin.scene().sigMouseMoved, rateLimit=60, slot=self.updateTV)				
		self.pwin.showGrid(x=True, y=True)						# with grid
		

		for k in range(self.MAXCHAN):							# pg textItem to show the voltage scales
			self.scaleLabs[k] = pg.TextItem(text='')

		for k in range(self.MAXRES):						# pg textItem to show the Results
			self.resLabs[k] = pg.TextItem()
			self.pwin.addItem(self.resLabs[k])
		
		vLine = pg.InfiniteLine(angle=90, movable=False, pen = 'w')
		self.pwin.addItem(vLine, ignoreBounds=True)
		self.pwin.vLine=vLine
		self.pwin.vLine.setPos(-1)
		hLine = pg.InfiniteLine(angle=0, movable=False, pen = 'w')
		self.pwin.addItem(hLine, ignoreBounds=True)
		self.pwin.hLine=hLine
		self.pwin.hLine.setPos(-17)
		
		ax = self.pwin.getAxis('bottom')
		ax.setLabel(self.tr('Time (mS)'))	
		ax = self.pwin.getAxis('left')
		ax.setStyle(showValues=False)
		ax.setLabel(self.tr('Voltage'))
		
		self.set_timebase(self.TBval)
		self.pwin.disableAutoRange()
		self.pwin.setXRange(0, self.tbvals[self.TBval]*10)
		self.pwin.setYRange(-16, 16)
		self.pwin.hideButtons()									# Do not show the 'A' button of pg

		for ch in range(self.MAXCHAN):							# initialize the pg trace widgets
			self.traceWidget[ch] = self.pwin.plot([0,0],[0,0], pen = self.traceCols[ch])
		self.diffTraceW = self.pwin.plot([0,0],[0,0], pen = self.traceCols[-1])

		right = QVBoxLayout()							# right side vertical layout
		right.setAlignment(Qt.AlignTop)
		right.setSpacing(self.RPVspacing)		

		l = QLabel(text= '<font color="red">' +self.tr('DC Voltages at A1, A2 and A3'))
		l.setMinimumWidth(self.RPWIDTH)
		right.addWidget(l)

		H = QHBoxLayout()
		for k in range(3):
			H.setAlignment(Qt.AlignLeft)
			self.voltMeterCB[k] = QCheckBox(self.tr(self.sources[k]))
			H.addWidget(self.voltMeterCB[k])
			self.voltMeters[k] = QLabel()
			self.voltMeters[k].setMinimumWidth(50)
			H.addWidget(self.voltMeters[k])
		right.addLayout(H)

		H = QHBoxLayout()
		l = QLabel(text=self.tr('Resistance on SEN = '))
		H.addWidget(l)
		self.RES = QLabel()
		H.addWidget(self.RES)
		right.addLayout(H)
		
		H = QHBoxLayout()
		b = QPushButton(self.tr("Click for Capacitance on IN1"))
		b.setMinimumWidth(200)
		H.addWidget(b)
		b.clicked.connect(self.measure_cap)
		self.CAP = QLabel('')
		H.addWidget(self.CAP)
		right.addLayout(H)

		H = QHBoxLayout()
		b = QPushButton(self.tr("Click for Frequency on IN2"))
		b.setMinimumWidth(200)
		H.addWidget(b)
		b.clicked.connect(self.measure_freq)
		self.IN2 = QLabel('')
		H.addWidget(self.IN2)
		right.addLayout(H)

		H = QHBoxLayout()
		self.OD1 = QCheckBox(self.tr("Enable OD1"))
		H.addWidget(self.OD1)
		self.OD1.stateChanged.connect(self.control_od1)
		self.CCS = QCheckBox(self.tr("Enable CCS"))
		H.addWidget(self.CCS)
		self.CCS.stateChanged.connect(self.control_ccs)
		right.addLayout(H)

		H = QHBoxLayout()
		l = QLabel(text=self.tr('WG Shape'))
		H.addWidget(l)
		self.Wshape = QPushButton('sine')
		menu = QMenu()
		for k in range(len(self.Waves)):
			menu.addAction(self.Waves[k], lambda index=k: self.select_wave(index))
		self.Wshape.setMenu(menu)
		H.addWidget(self.Wshape)

		l = QLabel(text=self.tr('Amplitude'))
		H.addWidget(l)

		self.Wgain = QPushButton(self.Wgains[self.wgainindex])
		menu = QMenu()
		for k in range(len(self.Wgains)):
			menu.addAction(self.Wgains[k], lambda index=k: self.select_wgain(index))
		self.Wgain.setMenu(menu)
		H.addWidget(self.Wgain)
		right.addLayout(H)
		
		H = QHBoxLayout()
		l = QLabel(text=self.tr('WG'))
		l.setMaximumWidth(30)
		H.addWidget(l)
		self.AWGslider = utils.slider(self.AWGmin, self.AWGmax, self.AWGval,100,self.awg_slider)
		H.addWidget(self.AWGslider)
		self.AWGtext = utils.lineEdit(100, self.AWGval, 6, self.awg_text)
		H.addWidget(self.AWGtext)
		l = QLabel(text=self.tr('Hz'))
		l.setMaximumWidth(40)
		l.setMinimumWidth(40)
		H.addWidget(l)
		right.addLayout(H)
		
		H = QHBoxLayout()
		l = QLabel(text=self.tr('SQ1'))
		l.setMaximumWidth(30)
		l.setMinimumWidth(30)
		H.addWidget(l)
		self.SQ1slider = utils.slider(self.SQ1min, self.SQ1max, self.SQ1val,100,self.sq1_slider)
		H.addWidget(self.SQ1slider)
		self.SQ1text = utils.lineEdit(60, self.SQ1val, 6, self.sq1_text)
		H.addWidget(self.SQ1text)
		l = QLabel(text=self.tr('Hz'))
		l.setMaximumWidth(15)
		H.addWidget(l)
		self.SQ1DCtext = utils.lineEdit(30, 50, 6, self.sq1_dc)
		H.addWidget(self.SQ1DCtext)
		l = QLabel(text=self.tr('%'))
		l.setMaximumWidth(15)
		H.addWidget(l)
		right.addLayout(H)

		H = QHBoxLayout()
		l = QLabel(text=self.tr('PV1'))
		l.setMaximumWidth(25)
		H.addWidget(l)
		
		self.PV1slider = utils.slider(self.PV1min*1000, self.PV1max*1000, self.PV1val*1000,100,self.pv1_slider)
		H.addWidget(self.PV1slider)
		
		self.PV1text = utils.lineEdit(100, self.PV1val, 6, self.pv1_text)
		H.addWidget(self.PV1text)
		l = QLabel(text=self.tr('Volt'))
		l.setMaximumWidth(40)
		l.setMinimumWidth(40)
		H.addWidget(l)
		right.addLayout(H)

		H = QHBoxLayout()
		l = QLabel(text=self.tr('PV2'))
		l.setMaximumWidth(25)
		H.addWidget(l)

		self.PV2slider = utils.slider(self.PV2min*1000, self.PV2max*1000, self.PV2val*1000,100,self.pv2_slider)
		H.addWidget(self.PV2slider)
		
		self.PV2text = utils.lineEdit(100, self.PV2val, 6, self.pv2_text)
		H.addWidget(self.PV2text)
		l = QLabel(text=self.tr('Volt'))
		l.setMaximumWidth(40)
		l.setMinimumWidth(40)
		H.addWidget(l)
		right.addLayout(H)
		
		#--------------------------Scope Controls---------------------
		l = QLabel('<font color="red">' +self.tr('Oscilloscope Channels, Range and Analysis '))
		right.addWidget(l)

		for ch in range(4):
			H = QHBoxLayout()
			H.setAlignment(Qt.AlignLeft)
			self.chanSelCB[ch] = QCheckBox()
			self.chanSelCB[ch].stateChanged.connect(partial (self.select_channel,ch))
			H.addWidget(self.chanSelCB[ch])

			l = QLabel(text='<font color="%s">%s'%(self.htmlColors[ch],self.sources[ch]))		
			l.setMaximumWidth(30)
			l.setMinimumWidth(30)
			H.addWidget(l)
			
			self.rangeSelPB[ch] = QPushButton('4 V')
			self.rangeSelPB[ch].setMaximumWidth(60)
			menu = QMenu()
			if ch <= 1:
				for k in range(len(self.Ranges12)):
					menu.addAction(self.Ranges12[k], lambda index=(ch,k): self.select_range(index))
			else:	
				for k in range(len(self.Ranges34)):
					menu.addAction(self.Ranges34[k], lambda index=(ch,k): self.select_range(index))
			self.rangeSelPB[ch].setMenu(menu)
			H.addWidget(self.rangeSelPB[ch])
			self.fitSelCB[ch] = QCheckBox('')
			self.fitSelCB[ch].setMaximumWidth(30)
			H.addWidget(self.fitSelCB[ch])
			self.fitResLab[ch] = QLabel('') 
			H.addWidget(self.fitResLab[ch])
			right.addLayout(H)
		self.chanSelCB[0].setChecked(True)

		H = QHBoxLayout()
		l = QLabel(text=self.tr('Timebase'))
		l.setMaximumWidth(60)
		H.addWidget(l)
		self.TBslider = utils.slider(0, 8, self.TBval, 180, self.set_timebase)
		H.addWidget(self.TBslider)
		l = QLabel(text=self.tr('mS/div'))
		l.setMaximumWidth(60)
		H.addWidget(l)
		right.addLayout(H)

		H = QHBoxLayout()
		l = QLabel(text=self.tr('Trigger'))
		l.setMaximumWidth(60)
		H.addWidget(l)
		self.Trigslider = utils.slider(-3300, 3300, self.Triglevel, 150, self.set_trigger)
		H.addWidget(self.Trigslider)
		l = QLabel(text=self.tr('On'))
		l.setMaximumWidth(30)
		H.addWidget(l)	
		self.Trigbutton = QPushButton(self.tr('A1'))
		self.Trigbutton.setMaximumWidth(50)
		menu = QMenu()
		for k in range(len(self.sources)):
			menu.addAction(self.sources[k], lambda index=k :self.select_trig_source(index))
		self.Trigbutton.setMenu(menu)
		H.addWidget(self.Trigbutton)
		right.addLayout(H)

		H = QHBoxLayout()
		self.SaveButton = QPushButton(self.tr("Save Traces"))
		#self.SaveButton.setMaximumWidth(80)
		self.SaveButton.clicked.connect(self.save_data)		
		H.addWidget(self.SaveButton)
			
		#self.Filename = utils.lineEdit(100, self.tr('scope.txt'), 20, None)
		#H.addWidget(self.Filename)
		
		self.FFT = QPushButton(self.tr("Fourier Transform"))
		#self.FFT.setMaximumWidth(50)
		H.addWidget(self.FFT)
		self.FFT.clicked.connect(self.show_fft)		
	
		right.addLayout(H)
		
		H = QHBoxLayout()
		self.Cross = QCheckBox(self.tr("Cross hair"))
		self.Cross.stateChanged.connect(self.cross_hair)
		H.addWidget(self.Cross)

		self.Freeze = QCheckBox(self.tr("Freeze"))
		H.addWidget(self.Freeze)
		self.Diff = QCheckBox(self.tr('A1-A2'))
		H.addWidget(self.Diff)
		self.Diff.stateChanged.connect(self.show_diff)
		right.addLayout(H)

		#------------------------end of right panel ----------------
		
		top = QHBoxLayout()
		top.addLayout(left)
		top.addWidget(win)# self.pwin)
		top.addLayout(right)
		
		full = QVBoxLayout()
		full.addLayout(top)
		self.msgwin = QLabel(text=self.tr('messages'))
		full.addWidget(self.msgwin)
				
		self.setLayout(full)
		
		self.timer = QTimer()
		self.timer.timeout.connect(self.update)
		self.timer.start(self.TIMER)

		self.recover()
		#----------------------------- end of init ---------------
	
	
	def update(self):
		if self.Freeze.isChecked(): return

		try:
			if self.chanStatus[2] == 1 or self.chanStatus[3] == 1: # channel 3 or 4 selected  	
				self.timeData[0], self.voltData[0],	\
				self.timeData[1], self.voltData[1], \
				self.timeData[2], self.voltData[2], \
				self.timeData[3], self.voltData[3] = self.p.capture4(self.NP, self.TG)				
			elif self.chanStatus[1] == 1:    	# channel 2 is selected  	
				self.timeData[0], self.voltData[0], \
				self.timeData[1], self.voltData[1] = self.p.capture2(self.NP, self.TG)
			elif self.chanStatus[0] == 1: 		# only A1 selected
				self.timeData[0], self.voltData[0] = self.p.capture1('A1', self.NP, self.TG)
		except:
			self.comerr()
			return
			
		for ch in range(4):
			if self.chanStatus[ch] == 1:
				r = 16./self.rangeVals[ch]
				self.traceWidget[ch].setData(self.timeData[ch], self.voltData[ch] * r + 4*self.offValues[ch] )
				if np.max(self.voltData[ch]) > self.rangeVals[ch]:
					self.msg(unicode(self.tr('%s input is clipped. Increase range')) %self.sources[ch])

				if self.fitSelCB[ch].isChecked() == True:
					try:
						fa = em.fit_sine(self.timeData[ch],self.voltData[ch])
					except Exception as err:
						print('fit_sine error:', err)
						fa=None
					if fa != None:
						self.voltDataFit[ch] = fa[0]
						self.Amplitude[ch] = abs(fa[1][0])
						self.Frequency[ch] = fa[1][1]*1000
						self.Phase[ch] = fa[1][2] * 180/em.pi
						s = unicode(self.tr('%5.2f V, %5.1f Hz')) %(self.Amplitude[ch],self.Frequency[ch])
						self.fitResLab[ch].setText(s)
				else:
					self.fitResLab[ch].setText('')

		if self.Diff.isChecked() == True and self.chanStatus[0] == 1 and self.chanStatus[1] == 1:
			r = 16./self.rangeVals[0]
			self.diffTraceW.setData(self.timeData[0], r*(self.voltData[0]-self.voltData[1]))

		self.loopCounter += 1
		if self.loopCounter % 5 == 0:
			for ch in range(3):
				if self.voltMeterCB[ch].isChecked() == True:
					try:
						v = self.p.get_voltage(self.sources[ch])		# Voltmeter functions
					except:
						self.comerr()

					self.voltMeters[ch].setText(unicode(self.tr('%5.3f V')) %(v))
				else:
					self.voltMeters[ch].setText(self.tr(''))			
			try:
				res = self.p.get_resistance()
				if res != np.Inf and res > 100  and  res < 100000:
					self.RES.setText('<font color="blue">'+unicode(self.tr('%5.0f Ohm')) %(res))
				else:
					self.RES.setText(self.tr('<100Ohm  or  >100k'))
				self.p.select_range('A1', self.rangeVals[0])
				self.p.select_range('A2', self.rangeVals[1])
			except:
				self.comerr()
		# End of update


	def show_diff(self):
		if self.Diff.isChecked() == False:
				self.diffTraceW.setData([0,0], [0,0])
	
	def showRange(self, ch):
		spacing = self.tbvals[self.TBval]
		self.pwin.removeItem(self.scaleLabs[ch])
		if self.chanStatus[ch] == 0: 
			return
		self.scaleLabs[ch] = pg.TextItem(text=self.rangeTexts[ch],	color= self.resultCols[ch],  angle=315)
		self.scaleLabs[ch].setPos(ch*spacing/3, 15.5)
		#self.scaleLabs[ch].setText('hello')
		self.pwin.addItem(self.scaleLabs[ch])

	def select_channel(self, ch):
		if self.chanSelCB[ch].isChecked() == True:
			self.chanStatus[ch] = 1
			self.traceWidget[ch] = self.pwin.plot([0,0],[0,0], pen=self.traceCols[ch])
		else:
			self.chanStatus[ch] = 0
			self.pwin.removeItem(self.traceWidget[ch])
		self.showRange(ch)

	def select_range(self,info):
		ch = info[0]
		index = info[1]
		if ch <= 1:
			self.rangeTexts[ch] = self.Ranges12[index]
			self.rangeVals[ch] = self.RangeVals12[index]
			try:
				self.p.select_range(self.sources[ch], self.RangeVals12[index])
			except:
				self.comerr()
				return		
		else:
			self.rangeTexts[ch] = self.Ranges34[index]
			self.rangeVals[ch] = self.RangeVals34[index]
		self.rangeSelPB[ch].setText(self.rangeTexts[ch])
		self.showRange(ch)
		ss1 = '%s'%self.sources[ch]
		ss2 = '%s'%self.rangeTexts[ch]
		self.msg(self.tr('Range of') + ss1 + self.tr(' set to ') + ss2)
	

	def show_fft(self):
		for ch in range(4):
			if self.chanStatus[ch] == 1:
				try:	
					fa = em.fit_sine(self.timeData[ch],self.voltData[ch])
				except Exception as err:
					print('fit_sine error:', err)
					fa=None
				if fa != None:
					fr = fa[1][1]*1000			# frequency in Hz
					dt = int(1.e6/ (20 * fr))	# dt in usecs, 20 samples per cycle
					try:
						t,v = self.p.capture1(self.sources[ch], 3000, dt)
					except:
						self.comerr()

					xa,ya = em.fft(v,dt)
					xa *= 1000
					peak = self.peak_index(xa,ya)
					ypos = np.max(ya)
					pop = pg.plot(xa,ya, pen = self.traceCols[ch])
					pop.showGrid(x=True, y=True)
					txt = pg.TextItem(text=unicode(self.tr('Fundamental frequency = %5.1f Hz')) %peak, color = 'w')
					txt.setPos(peak, ypos)
					pop.addItem(txt)
					pop.setWindowTitle(self.tr('Frequency Spectrum'))
				else:
					self.msg(self.tr('FFT Error'))
						
						
	def peak_index(self, xa, ya):
		peak = 0
		peak_index = 0
		for k in range(2,len(ya)):
			if ya[k] > peak:
				peak = ya[k]
				peak_index = xa[k]
		return peak_index
		
	def save_data(self):
		self.timer.stop()
		fn = QFileDialog.getSaveFileName()
		if fn != '':
			dat = []
			for ch in range(4):
				if self.chanStatus[ch] == 1:
					dat.append( [self.timeData[ch], self.voltData[ch] ])
			self.p.save(dat,fn)
			ss = unicode(fn)
			self.msg(self.tr('Traces saved to ') + ss)
		self.timer.start(self.TIMER)


	def select_trig_source(self, index):
		self.Trigindex = index
		src = self.sources[self.Trigindex]
		self.Trigbutton.setText(self.sources[self.Trigindex])
		try:
			self.p.configure_trigger(self.Trigindex, self.sources[self.Trigindex], self.Triglevel)
		except:
			self.comerr()

	def set_trigger(self, tr):
		self.Triglevel = tr * 0.001		# convert to volts
		try:
			if self.TBval > 3:
				self.p.configure_trigger(self.Trigindex, self.sources[self.Trigindex], self.Triglevel,resolution=10,prescaler=5)
			else:
				self.p.configure_trigger(self.Trigindex, self.sources[self.Trigindex], self.Triglevel)
		except:
			self.comerr()
			
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
		for k in range(self.MAXCHAN):
			self.showRange(k)

	def pv1_text(self, text):
		try:
			val = float(text)
		except:
			return
		val = float(text)
		if self.PV1min <= val <= self.PV1max:
			self.PV1val = val
			try:
				self.p.set_pv1(val)
				self.PV1slider.setValue(int(val*1000))
			except:
				self.comerr()

	def pv1_slider(self, pos):
		val = float(pos)/1000.0
		if self.PV1min <= val <= self.PV1max:
			self.PV1val = val
			self.PV1text.setText(unicode(val))
			try:
				self.p.set_pv1(val)
			except:
				self.comerr()

	def pv2_text(self, text):
		try:
			val = float(text)
		except:
			return
		val = float(text)
		if self.PV2min <= val <= self.PV2max:
			self.PV2val = val
			try:
				self.p.set_pv2(val)
				self.PV2slider.setValue(int(val*1000))
			except:
				self.comerr()
				
	def pv2_slider(self, pos):
		val = float(pos)/1000.0
		if self.PV2min <= val <= self.PV2max:
			self.PV2val = val
			self.PV2text.setText(unicode(val))
			try:
				self.p.set_pv2(val)
			except:
				self.comerr()
				
	def sq1_dc(self, text):
		try:
			val = float(text)
		except:
			return
		if 1 <= val <= 99:
			self.dutyCycle = val
			s = self.SQ1text.text()
			self.sq1_text(s)

	def sq1_text(self, text):
		try:
			val = float(text)
		except:
			return
		if self.SQ1min <= val <= self.SQ1max:
			self.SQ1val = val
			self.SQ1slider.setValue(self.SQ1val)
			try:
				if 0 <= val < 4 : val = 0
				res = self.p.set_sqr1(val, self.dutyCycle)
				ss = '%5.1f'%res
				self.msg(self.tr('sqr1 set to ') + ss)
			except:
				self.comerr()

	def sq1_slider(self, val):
		if self.SQ1min <= val <= self.SQ1max:
			self.SQ1val = val
			self.SQ1text.setText(unicode(val))
			s = self.SQ1text.text()
			self.sq1_text(s)
				
	def select_wgain(self,index):
		self.Wgain.setText(self.Wgains[index])
		self.wgainindex = index
		try:
			self.p.set_sine_amp(index)
		except:
			self.comerr()

	def set_wave(self):
		try:
			if self.waveindex <= 1:
				res = self.p.set_wave(self.AWGval, self.Waves[self.waveindex])
				ss = '%6.2f'%res
				self.msg(self.tr('AWG set to ') + ss + self.tr(' Hz'))
			else:
				self.p.set_sqr2(self.AWGval)
				self.msg(self.tr('Output Changed from WG to SQ2'))
		except:
			self.comerr()

	def select_wave(self,index):
		self.Wshape.setText(self.Waves[index])
		self.waveindex = index
		self.set_wave()

	def awg_text(self, text):
		try:
			val = float(text)
			if self.AWGmin <= val <= self.AWGmax:
				self.AWGval = val
				self.AWGslider.setValue(self.AWGval)
				self.set_wave()
		except:
			return

	def awg_slider(self, val):
		if self.AWGmin <= val <= self.AWGmax:
			self.AWGval = val
			self.AWGtext.setText(unicode(val))
			self.set_wave()

	def control_od1(self):
		try:
			state = self.OD1.isChecked()
			if state == True:
				self.p.set_state(OD1=1)
			else:
				self.p.set_state(OD1=0)      
		except:
			self.comerr()
   
	def control_ccs(self):
		try:
			state = self.CCS.isChecked()
			if state == True:
				self.p.set_state(CCS=1)
			else:
				self.p.set_state(CCS=0)      
		except:
			self.comerr()
			
	def measure_cap(self):
		try:
			cap = self.p.get_capacitance()
			if cap == None:
				self.msg(self.tr('Capacitance too high or short to ground'))
			else:
				if cap < 1.0e-9:
					ss = '%6.1f'%(cap*1e12)
					self.CAP.setText('<font color="blue">'+ ss +self.tr(' pF'))
				elif cap < 1.0e-6:
					ss = '%6.1f'%(cap*1e9)
					self.CAP.setText('<font color="blue">'+ ss +self.tr(' nF'))
				elif cap < 1.0e-3:
					ss = '%6.1f'%(cap*1e6)
					self.CAP.setText('<font color="blue">'+ ss +self.tr(' uF'))
		except:
			self.comerr()

	def measure_freq(self):
		try:
			fr = self.p.get_freq()
			hi = self.p.r2ftime('IN2','IN2')
		except:
			self.comerr()
		if fr > 0:	
			T = 1./fr
			dc = hi*100/T
			self.IN2.setText(u'<font color="blue">'+unicode(self.tr('%5.1fHz %4.1f%%')) %(fr,dc))
		else:
			self.IN2.setText(u'<font color="blue">'+self.tr('No signal'))
		
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
	
