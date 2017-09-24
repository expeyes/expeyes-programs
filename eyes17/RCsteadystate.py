import sys, time, utils, math

if utils.PQT5 == True:
	from PyQt5.QtCore import Qt, QTimer
	from PyQt5.QtWidgets import QApplication,QWidget,QLabel, QHBoxLayout, QVBoxLayout, QPushButton,QCheckBox
	from PyQt5.QtGui import QPalette, QColor
else:
	from PyQt4.QtCore import Qt, QTimer
	from PyQt4.QtGui import QPalette, QColor, QApplication, QWidget,\
	QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QCheckBox

import pyqtgraph as pg
import numpy as np
import eyes17.eyemath17 as em


class Expt(QWidget):
	TIMER = 200
	loopCounter = 0
	AWGmin = 1
	AWGmax = 5000
	AWGval = 150
	waveindex = 0
	wgainindex = 2
	
	RPVspacing = 3											# Right panel Widget spacing
	RPWIDTH = 300
	LABW = 60
		
	# Scope parameters
	MAXCHAN = 4
	chanStatus  = [1,0,0,0]
	timeData    = [None]*4
	voltData    = [None]*4
	voltDataFit = [None]*4
	traceWidget = [None]*4
	fitResWidget= [None]*4
	#chanSelCB   = [None]*4
	#rangeSelPB  = [None]*4
	#fitSelCB    = [None]*4
	#fitResLab   = [None]*4
	fitFine     = [0]*4
	Amplitude   = [0]*4
	Frequency   = [0]*4
	Phase       = [0]*4
	rangeVals   = [4]*4		# selected value of range
	rangeTexts  = ['4 V']*4		# selected value of range
	scaleLabs   = [None]*4  # display fullscale value inside pg
	voltMeters  = [None]*3
	MAXRES = 8
	Results     = [None]*MAXRES
	phasorPlot = None
	phasorTraces = [None]*3
	
	sources = ['A1','A2','A3', 'MIC']
	#chancols = ['black', 'red', 'blue','magenta']
	chanpens = ['y','g','w','m']     #pqtgraph pen colors

	tbvals = [0.100, 0.200, 0.500, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0]	# allowed mS/div values
	NP = 500			# Number of samples
	TG = 1				# Number of channels
	MINDEL = 1			# minimum time between samples, in usecs
	MAXDEL = 1000
	delay = MINDEL		# Time interval between samples
	TBval = 4			# timebase list index
	Trigindex = 0
	Triglevel = 0
	scaleCols = [(200,200,0),(0,200,0),(200,200,200), (200,0,200)]

	
	def __init__(self, device=None):
		QWidget.__init__(self)
		self.p = device										# connection to the device hardware 
		try:
			self.p.select_range('A1',4.0)
			self.p.select_range('A2',4.0)	
			self.p.set_sine(self.AWGval)
			self.p.configure_trigger(1, 'A1', 0)
		except:
			pass	
		
		self.pwin = pg.PlotWidget()							# pyqtgraph window
		self.pwin.showGrid(x=True, y=True)					# with grid
		for k in range(self.MAXCHAN):						# pg textItem to show the voltage scales
			self.scaleLabs.append(pg.TextItem(text=''))
		ax = self.pwin.getAxis('bottom')
		ax.setLabel('Time (mS)')	
		ax = self.pwin.getAxis('left')
		ax.setLabel('Voltage')

		self.set_timebase(self.TBval)
		self.pwin.disableAutoRange()
		self.pwin.setXRange(0, self.tbvals[self.TBval]*10)
		self.pwin.setYRange(-4, 4)
		self.pwin.hideButtons()									# Do not show the 'A' button of pg

		for ch in range(self.MAXCHAN):							# initialize the pg trace widgets
			self.traceWidget[ch] = self.pwin.plot([0,0],[0,0], pen = self.chanpens[ch])

		right = QVBoxLayout()							# right side vertical layout
		#right.setAlignment(Qt.AlignTop)
		right.setSpacing(self.RPVspacing)
		
		l = QLabel(text=self.tr('<font color="blue">Measurement Results'))
		l.setMaximumWidth(300)
		right.addWidget(l)
		for k in range(self.MAXRES):
			self.Results[k] = QLabel(text='')
			right.addWidget(self.Results[k])

		self.phasorEnable = QCheckBox('Phasor Plot')
		right.addWidget(self.phasorEnable)
		self.phasorEnable.stateChanged.connect(self.draw_phasor)
				
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
		self.TBslider = utils.slider(0, 8, self.TBval, 150, self.set_timebase)
		H.addWidget(self.TBslider)
		l = QLabel(text=self.tr('mS/div'))
		l.setMaximumWidth(60)
		H.addWidget(l)
		right.addLayout(H)
	
		H = QHBoxLayout()
		self.SaveButton = QPushButton(self.tr("Save Data to"))
		self.SaveButton.setMaximumWidth(90)
		self.SaveButton.clicked.connect(self.save_data)		
		H.addWidget(self.SaveButton)
		self.Filename = utils.lineEdit(150, 'RCs-data.txt', 20, None)
		H.addWidget(self.Filename)
		right.addLayout(H)
		
		l = QLabel(text='')
		right.addWidget(l)
		l = QLabel(text=self.tr('<font color="blue">Impedance Calculator'))
		right.addWidget(l)

		
		H = QHBoxLayout()
		l = QLabel(text=self.tr('Frequency'))
		l.setMaximumWidth(100)
		H.addWidget(l)
		self.uFreq = utils.lineEdit(100, 150, 6, None)
		H.addWidget(self.uFreq)
		right.addLayout(H)
		
		H = QHBoxLayout()
		l = QLabel(text=self.tr('C (in uF)'))
		l.setMaximumWidth(100)
		H.addWidget(l)
		self.uCap = utils.lineEdit(100, 1, 6, None)
		#self.uCap.setValidator(QDoubleValidator(0.9,9.99,2))
		H.addWidget(self.uCap)
		right.addLayout(H)
		
		
		H = QHBoxLayout()
		l = QLabel(text=self.tr('R (in Ohm)'))
		l.setMaximumWidth(100)
		H.addWidget(l)
		self.uRes = utils.lineEdit(100, 1000, 6, None)
		H.addWidget(self.uRes)
		right.addLayout(H)
		
		H = QHBoxLayout()
		l = QLabel(text=self.tr('L (in mH)'))
		l.setMaximumWidth(100)
		H.addWidget(l)
		self.uInd = utils.lineEdit(100, 0, 6, None)
		H.addWidget(self.uInd)
		right.addLayout(H)
		
		b=QPushButton('Calculate')
		b.clicked.connect(self.calc)		
		right.addWidget(b)
		self.uResult =QLabel(text='')
		right.addWidget(self.uResult)
		
		
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
	
	
	def calc(self):
		try:
			f = float(self.uFreq.text())
			C = float(self.uCap.text())*1e-6
			L = float(self.uInd.text())*1e-3
			R = float(self.uRes.text())
			Xl = 2*np.pi*f*L
			if C != 0:
				Xc = 1./(2*np.pi*f*C)
			else:
				Xc = 0.0
			dphi = math.atan((Xc-Xl)/R)*180./np.pi
			if L == 0:
				f0 = np.NaN
			else:
				f0 = 1./(2*np.pi*np.sqrt(L*C))
			s = 'Xc = %5.1f\tXl = %5.1f \nphi = %5.1f deg\tFo = %5.1f Hz'%(Xc, Xl, dphi,f0)
			self.uResult.setText(s)
		except:
			self.msg('Invalid Input')


	def update(self):
		try:
			self.timeData[0], self.voltData[0], \
			self.timeData[1], self.voltData[1] = self.p.capture2(self.NP, self.TG)
			self.timeData[2] = self.timeData[0]
			self.voltData[2] = self.voltData[0] - self.voltData[1]
		except:
			self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		
			return 

		for ch in range(3):
			r = 4./self.rangeVals[ch]
			self.traceWidget[ch].setData(self.timeData[ch], self.voltData[ch]*r)
			fa = em.fit_sine(self.timeData[ch],self.voltData[ch])
			if fa != None:
				self.voltDataFit[ch] = fa[0]
				self.Amplitude[ch] = abs(fa[1][0])
				self.Frequency[ch] = fa[1][1]*1000
				self.Phase[ch] = fa[1][2] * 180/em.pi
				self.fitFine[ch] = 1
			else:
				return
		self.Results[0].setText('Frequency = %5.1f Hz'%(self.Frequency[0]))
		self.Results[1].setText('<font color="yellow">Applied Voltage = %5.2f V'%(self.Amplitude[0]))
		self.Results[2].setText('<font color="green">Voltage across R = %5.2f V'%(self.Amplitude[1]))
		self.Results[3].setText('<font color="white">Voltage across C = %5.2f V'%(self.Amplitude[2]))
		pd = (self.Phase[1] - self.Phase[0])
		self.Results[4].setText('Phase change across C = %5.1f deg'%(pd))
		if self.fitFine[0] == 1 and self.fitFine[1] == 1:
			self.draw_phasor()

	def draw_phasor(self):
		if self.phasorEnable.isChecked() == True:
			if self.phasorPlot == None:
				self.phasorPlot = pg.plot()
				self.phasorPlot.showGrid(x=True, y=True)		# with grid
				self.phasorPlot.disableAutoRange()
				self.phasorPlot.setXRange(0,4)
				self.phasorPlot.setYRange(-4, 4)
				#self.phasorPlot.hideButtons()			# Do not show the 'A' button of pg
				for ch in range(3):
					self.phasorTraces[ch] = self.phasorPlot.plot([0,0],[0,0], pen = self.chanpens[ch])
			
			Va = self.Amplitude[0]
			Vr = self.Amplitude[1]
			Vc = self.Amplitude[2]
			pd01 = math.atan(Vr/Va)
			
			phaseDiff = (self.Phase[1]-self.Phase[0])*np.pi/180
			sign = -np.sign(phaseDiff)
			rx = Va * math.sin(phaseDiff)
			ry = Va * math.cos(phaseDiff) 

			
			self.phasorTraces[0].setData([0,Vr], [0,sign*Vc])
			self.phasorTraces[1].setData([0,Vr], [0,0])
			self.phasorTraces[2].setData([0,0], [0,sign*Vc])
		else:
			pass
			#self.phasorPlot.hide()
			

	def save_data(self):
		fn = self.Filename.text()
		dat = []
		for ch in range(3):
			if self.chanStatus[ch] == 1:
				dat.append( [self.timeData[ch], self.voltData[ch] ])
		self.p.save(dat,fn)
		self.msg('Traces saved to %s'%fn)
			
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
			self.msg('AWG set to %6.2f Hz'%res)
		except:
			self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		
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
			self.AWGtext.setText(str(val))
			self.set_wave()
		
	def msg(self, m):
		self.msgwin.setText(self.tr(m))
		

if __name__ == '__main__':
	import eyes17.eyes
	dev = eyes17.eyes.open()
	app = QApplication(sys.argv)
	mw = Expt(dev)
	mw.show()
	sys.exit(app.exec_())
	
