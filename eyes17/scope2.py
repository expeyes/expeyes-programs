import sys, time, utils, math

if utils.PQT5 == True:
	from PyQt5.QtCore import Qt, QTimer
	from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QCheckBox,\
	QStatusBar, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QMenu
	from PyQt5.QtGui import QPalette, QColor
else:
	from PyQt4.QtCore import Qt, QTimer
	from PyQt4.QtGui import QPalette, QColor, QApplication, QWidget,\
	QCheckBox, QStatusBar, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QMenu

import sys, time, utils
import pyqtgraph as pg
import numpy as np
import eyes17.eyemath17 as em


class Expt(QWidget):
	TIMER = 50
	loopCounter = 0
	AWGmin = 1
	AWGmax = 5000
	AWGval = 1000
	SQ1min = 1
	SQ1max = 5000
	SQ1val = 1000
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
	MAXCHAN = 5
	Ranges12 = ['16 V', '8 V','4 V', '2.5 V', '1 V', '.5V']	# Voltage ranges for A1 and A2
	RangeVals12 = [16., 8., 4., 2.5, 1., 0.5]
	Ranges34 = ['4 V', '2 V', '1 V', '.5V']					# Voltage ranges for A3 and MIC
	RangeVals34 = [4,2,1,0.5]
	chanStatus  = [1,0,0,0,0]
	timeData    = [None]*MAXCHAN
	voltData    = [None]*MAXCHAN
	voltDataFit = [None]*MAXCHAN
	traceWidget = [None]*MAXCHAN
	xytraceWidget = None
	fitResWidget= [None]*MAXCHAN
	chanSelCB   = [None]*MAXCHAN
	rangeSelPB  = [None]*MAXCHAN
	fitSelCB    = [None]*MAXCHAN
	fitResLab   = [None]*MAXCHAN
	fitFlags    = [0]*MAXCHAN
	Amplitude   = [0]*MAXCHAN
	Frequency   = [0]*MAXCHAN
	Phase       = [0]*MAXCHAN
	rangeVals   = [4]*MAXCHAN		# selected value of range
	rangeTexts  = ['4 V']*MAXCHAN		# selected value of range
	scaleLabs   = [None]*MAXCHAN  # display fullscale value inside pg
	voltMeters  = [None]*3
	
	sources = ['A1','A2','A3', 'MIC']
	chanpens = ['y','g','w','m','r']     #pqtgraph pen colors

	tbvals = [0.100, 0.200, 0.500, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0]	# allowed mS/div values
	NP = 500			# Number of samples
	TG = 1				# Number of channels
	MINDEL = 1			# minimum time between samples, in usecs
	MAXDEL = 1000
	delay = MINDEL		# Time interval between samples
	TBval = 1			# timebase list index
	Trigindex = 0
	Triglevel = 0
	scaleCols = [(200,200,0),(0,200,0),(200,200,200), (200,0,200), (200,0,200)]

	def update(self):
		if self.Freeze.isChecked(): return

		if 1:
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

			for ch in range(4):
				if self.chanStatus[ch] == 1:
					r = 16./self.rangeVals[ch]
					self.traceWidget[ch].setData(self.timeData[ch], self.voltData[ch]*r)
					if np.max(self.voltData[ch]) > self.rangeVals[ch]:
						self.msg('%s input is clipped. Increase range'%self.sources[ch])

					if self.fitSelCB[ch].isChecked() == True:
						fa = em.fit_sine(self.timeData[ch],self.voltData[ch])
						if fa != None:
							self.voltDataFit[ch] = fa[0]
							self.Amplitude[ch] = abs(fa[1][0])
							self.Frequency[ch] = fa[1][1]*1000
							self.Phase[ch] = fa[1][2] * 180/em.pi
							s = '%5.2f V, %5.1f Hz'%(self.Amplitude[ch],self.Frequency[ch])
							self.fitResLab[ch].setText(s)
					else:
						self.fitResLab[ch].setText('')

			if self.XY.isChecked() == True and self.chanStatus[0] == 1 and self.chanStatus[1] == 1:
				r = 16./self.rangeVals[0]
				self.traceWidget[4].setData(self.timeData[0], (self.voltData[0]-self.voltData[1])*r)
		
			self.loopCounter += 1
			if self.loopCounter % 5 == 0:
				for ch in range(3):
					v = self.p.get_voltage(self.sources[ch])		# Voltmeter functions
					self.voltMeters[ch].setText(self.tr('%5.3f V'%(v)))
				res = self.p.get_resistance()
				if res != np.Inf:
					self.RES.setText(' %5.0f Ohm'%(res))
				else:
					self.RES.setText(' Out of range')
				self.p.select_range('A1', self.rangeVals[0])
				self.p.select_range('A2', self.rangeVals[1])
		else:
			self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		
		# End of update

	def show_diff(self):
		if self.XY.isChecked() == False:
				self.traceWidget[4].setData([0,0], [0,0])

	def __init__(self, device=None):
		QWidget.__init__(self)
		self.p = device											# connection to the device hardware 
		try:
			self.p.select_range('A1',4.0)
			self.p.select_range('A2',4.0)	
			self.p.set_sine(self.AWGval)
			self.p.configure_trigger(0, 'A1', 0)
		except:
			pass		
			
		self.pwin = pg.PlotWidget()								# pyqtgraph window
		self.pwin.showGrid(x=True, y=True)						# with grid
		for k in range(self.MAXCHAN):							# pg textItem to show the voltage scales
			self.scaleLabs.append(pg.TextItem(text=''))


		ax = self.pwin.getAxis('bottom')
		ax.setLabel('Time (mS)')	
		ax = self.pwin.getAxis('left')
		ax.setStyle(showValues=False)
		ax.setLabel('Voltage')

		self.set_timebase(self.TBval)
		self.pwin.disableAutoRange()
		self.pwin.setXRange(0, self.tbvals[self.TBval]*10)
		self.pwin.setYRange(-16, 16)
		self.pwin.hideButtons()									# Do not show the 'A' button of pg

		for ch in range(self.MAXCHAN):							# initialize the pg trace widgets
			self.traceWidget[ch] = self.pwin.plot([0,0],[0,0], pen = self.chanpens[ch])

		right = QVBoxLayout()							# right side vertical layout
		right.setAlignment(Qt.AlignTop)
		right.setSpacing(self.RPVspacing)
		
		l = QLabel(text=self.tr('Measurements & Controls'))
		l.setMinimumWidth(self.RPWIDTH)
		right.addWidget(l)


		H = QHBoxLayout()
		for k in range(3):
			l = QLabel(text=self.tr(self.sources[k]))
			l.setMaximumWidth(30)
			H.addWidget(l)
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

		self.Wgain = QPushButton('3 V')
		menu = QMenu()
		for k in range(len(self.Wgains)):
			menu.addAction(self.Wgains[k], lambda index=k: self.select_wgain(index))
		self.Wgain.setMenu(menu)
		H.addWidget(self.Wgain)
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
		l = QLabel(text=self.tr('SQ1'))
		l.setMaximumWidth(25)
		H.addWidget(l)
		self.SQ1slider = utils.slider(self.SQ1min, self.SQ1max, self.SQ1val,100,self.sq1_slider)
		H.addWidget(self.SQ1slider)
		self.SQ1text = utils.lineEdit(100, self.SQ1val, 6, self.sq1_text)
		H.addWidget(self.SQ1text)
		l = QLabel(text=self.tr('Hz'))
		l.setMaximumWidth(20)
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
		l = QLabel(text=self.tr('V'))
		l.setMaximumWidth(20)
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
		l = QLabel(text=self.tr('V'))
		l.setMaximumWidth(20)
		H.addWidget(l)
		right.addLayout(H)
		
		#--------------------------Scope Controls---------------------
		l = QLabel(self.tr('Oscilloscope Channels, Range and Analysis '))
		l.setStyleSheet("background-color:#99ccdd;")  #99ccff
		right.addWidget(l)
		from functools import partial

		for ch in range(4):
			H = QHBoxLayout()
			H.setAlignment(Qt.AlignLeft)
			self.chanSelCB[ch] = QCheckBox(self.tr(self.sources[ch]))
			self.chanSelCB[ch].stateChanged.connect(partial (self.select_channel,ch))
			self.chanSelCB[ch].setMinimumWidth(self.LABW)
			H.addWidget(self.chanSelCB[ch])
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
			self.fitSelCB[ch] = QCheckBox(self.tr(""))
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
		self.TBslider = utils.slider(0, 8, self.TBval, 150, self.set_timebase)
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
		self.Trigbutton = QPushButton('A1')
		self.Trigbutton.setMaximumWidth(50)
		menu = QMenu()
		for k in range(len(self.sources)):
			menu.addAction(self.sources[k], lambda index=k :self.select_trig_source(index))
		self.Trigbutton.setMenu(menu)
		H.addWidget(self.Trigbutton)
		right.addLayout(H)

		H = QHBoxLayout()
		self.SaveButton = QPushButton(self.tr("Save to"))
		self.SaveButton.setMaximumWidth(80)
		self.SaveButton.clicked.connect(self.save_data)		
		H.addWidget(self.SaveButton)
			
		self.Filename = utils.lineEdit(100, 'scope.txt', 20, None)
		H.addWidget(self.Filename)
		
		self.FFT = QPushButton(self.tr("FFT"))
		self.FFT.setMaximumWidth(50)
		H.addWidget(self.FFT)
		self.FFT.clicked.connect(self.show_fft)		
	
		right.addLayout(H)
		
		H = QHBoxLayout()
		self.Freeze = QCheckBox(self.tr("Freeze"))
		H.addWidget(self.Freeze)
		self.XY = QCheckBox(self.tr('A1-A2'))
		H.addWidget(self.XY)
		self.XY.stateChanged.connect(self.show_diff)
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
	
	def showRange(self, ch):
		spacing = self.tbvals[self.TBval]
		self.pwin.removeItem(self.scaleLabs[ch])
		print ch, self.chanStatus
		if self.chanStatus[ch] == 0: 
			return
		self.scaleLabs[ch] = pg.TextItem(text=self.rangeTexts[ch],	color= self.scaleCols[ch],  angle=315)
		self.scaleLabs[ch].setPos(ch*spacing/3, 15.5)
		self.pwin.addItem(self.scaleLabs[ch])

	def select_channel(self, ch):
		if self.chanSelCB[ch].isChecked() == True:
			self.chanStatus[ch] = 1
			self.traceWidget[ch] = self.pwin.plot([0,0],[0,0], pen=self.chanpens[ch])
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
				self.msg('<font color="red">Capture or fit Error, Try reconnect')
				return		
		else:
			self.rangeTexts[ch] = self.Ranges34[index]
			self.rangeVals[ch] = self.RangeVals34[index]
		self.rangeSelPB[ch].setText(self.rangeTexts[ch])
		self.showRange(ch)
		self.msg('Range of %s set to %s'%(self.sources[ch],self.rangeTexts[ch]))
	

	def show_fft(self):
		self.popwin = pg.PlotWidget()				# pyqtgraph window
		self.popwin.showGrid(x=True, y=True)						# with grid
		self.popwin.setWindowTitle('Frequency Spectrum')
		for ch in range(4):
			if self.chanStatus[ch] == 1:
				try:
					fa = em.fit_sine(self.timeData[ch],self.voltData[ch])
					if fa != None:
						fr = fa[1][1]*1000			# frequency in Hz
						dt = int(1.e6/ (20 * fr))	# dt in usecs, 20 samples per cycle
						t,v = self.p.capture1(self.sources[ch], 3000, dt)
						xa,ya = em.fft(v,dt)
						self.popwin.plot(xa*1000,ya, pen = self.chanpens[ch])					
				except:
					self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		
			self.popwin.show()


	def save_data(self):
		fn = self.Filename.text()
		dat = []
		for ch in range(4):
			if self.chanStatus[ch] == 1:
				dat.append( [self.timeData[ch], self.voltData[ch] ])
		self.p.save(dat,fn)
		self.msg('Traces saved to %s'%fn)


	def select_trig_source(self, index):
		self.Trigindex = index
		src = self.sources[self.Trigindex]
		self.Trigbutton.setText(self.sources[self.Trigindex])
		try:
			self.p.configure_trigger(self.Trigindex, self.sources[self.Trigindex], self.Triglevel)
		except:
			self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		

	def set_trigger(self, tr):
		self.Triglevel = tr * 0.001		# convert to volts
		try:
			self.p.configure_trigger(self.Trigindex, self.sources[self.Trigindex], self.Triglevel)
		except:
			self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		
			
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
				self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		

	def pv1_slider(self, pos):
		val = float(pos)/1000.0
		if self.PV1min <= val <= self.PV1max:
			self.PV1val = val
			self.PV1text.setText(str(val))
			try:
				self.p.set_pv1(val)
			except:
				self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		

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
				self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		
				
	def pv2_slider(self, pos):
		val = float(pos)/1000.0
		if self.PV2min <= val <= self.PV2max:
			self.PV2val = val
			self.PV2text.setText(str(val))
			try:
				self.p.set_pv2(val)
			except:
				self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		
				
	def sq1_text(self, text):
		try:
			val = float(text)
		except:
			return
		if self.SQ1min <= val <= self.SQ1max:
			self.SQ1val = val
			self.SQ1slider.setValue(self.SQ1val)
			try:
				res = self.p.set_sqr1(val)
			except:
				self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		

	def sq1_slider(self, val):
		if self.SQ1min <= val <= self.SQ1max:
			self.SQ1val = val
			self.SQ1text.setText(str(val))
			try:
				self.p.set_sqr1(val)
			except:
				self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		
				
	def select_wgain(self,index):
		self.Wgain.setText(self.Wgains[index])
		self.wgainindex = index
		try:
			self.p.set_sine_amp(index)
		except:
			self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		

	def set_wave(self):
		try:
			if self.waveindex <= 1:
				res = self.p.set_wave(self.AWGval, self.Waves[self.waveindex])
				self.msg('AWG set to %6.2f Hz'%res)
			else:
				self.p.set_sqr2(self.AWGval)
				self.msg('Output Changed from WG to SQ2')
		except:
			self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		

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
			self.AWGtext.setText(str(val))
			self.set_wave()

	def control_od1(self):
		try:
			state = self.OD1.isChecked()
			if state == True:
				self.p.set_state(OD1=1)
			else:
				self.p.set_state(OD1=0)      
		except:
			self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		
   
	def control_ccs(self):
		try:
			state = self.CCS.isChecked()
			if state == True:
				self.p.set_state(CCS=1)
			else:
				self.p.set_state(CCS=0)      
		except:
			self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		
			
	def measure_cap(self):
		try:
			cap = self.p.get_capacitance() * 1.e12
			if cap == None:
				self.msg('Capacitance too high or short to ground')
			else:
				self.CAP.setText('<font color="blue">%6.1f pF'%cap)
		except:
			self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		

	def measure_freq(self):
		try:
			fr = self.p.get_freq()
			self.IN2.setText('<font color="blue">%6.1f Hz'%fr)
		except:
			self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		
		
	def msg(self, m):
		self.msgwin.setText(self.tr(m))
		

if __name__ == '__main__':
	import eyes17.eyes
	dev = eyes17.eyes.open()
	app = QApplication(sys.argv)
	mw = Expt(dev)
	mw.show()
	sys.exit(app.exec_())
	
