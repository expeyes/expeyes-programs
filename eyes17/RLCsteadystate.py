# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
import sys, time, math, os.path
import utils

from QtVersion import *

import sys, time, math
import pyqtgraph as pg
import numpy as np
import eyes17.eyemath17 as em


class Expt(QWidget):
	TIMER = 50
	loopCounter = 0
	AWGmin = 1
	AWGmax = 5000
	AWGval = 150
	waveindex = 0
	wgainindex = 2
	
	RPVspacing = 2											# Right panel Widget spacing
	RPWIDTH = 300
	LABW = 60
		
	# Scope parameters
	MAXCHAN = 5
	timeData    = [None]*MAXCHAN
	voltData    = [None]*MAXCHAN
	voltDataFit = [None]*MAXCHAN
	traceWidget = [None]*MAXCHAN
	traceWidgetF= [None]*MAXCHAN
	fitResWidget= [None]*MAXCHAN
	fitFine     = [0]*MAXCHAN
	Amplitude   = [0]*MAXCHAN
	Frequency   = [0]*MAXCHAN
	Phase       = [0]*MAXCHAN
	rangeVals   = [4]*MAXCHAN			# selected value of range
	rangeTexts  = ['4 V']*MAXCHAN		# selected value of range
	scaleLabs   = [None]*MAXCHAN		# display fullscale value inside pg
	phasorPlot = None
	phasorTraces = [None]*5

	MAXRES = 7	# Number of results to show
	resLabs     = [None]*MAXRES
	Results     = [None]*MAXRES
	MINV = -4.0
	MAXV = 4.0
	#sources = ['A1','A2','A3', 'MIC']
	#chanpens = ['y','g','r','m','c']     #pqtgraph pen colors

	tbvals = [0.100, 0.200, 0.500, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0]	# allowed mS/div values
	NP = 500			# Number of samples
	TG = 1				# Number of channels
	MINDEL = 1			# minimum time between samples, in usecs
	MAXDEL = 1000
	delay = MINDEL		# Time interval between samples
	TBval = 4			# timebase list index
	Trigindex = 0
	Triglevel = 0
	#resCols = ['w','y','g','r','w','m','c']

	def __init__(self, device=None):
		QWidget.__init__(self)
		self.p = device										# connection to the device hardware 
		try:
			self.p.select_range('A1',8.0)
			self.p.select_range('A2',8.0)
			self.p.configure_trigger(1, 'A2', 0)
			self.p.set_sine(self.AWGval)
		except:
			pass	

		self.traceCols = utils.makeTraceColors()
		self.traceColsFit = utils.makeFitTraceColors()
		self.resCols = utils.makeResultColors()
		
		self.pwin = pg.PlotWidget()							# pyqtgraph window
		self.pwin.showGrid(x=True, y=True)					# with grid
		for k in range(self.MAXCHAN):						# pg textItem to show the voltage scales
			self.scaleLabs.append(pg.TextItem(text=''))
		ax = self.pwin.getAxis('bottom')
		ax.setLabel(self.tr('Time (mS)'))	
		ax = self.pwin.getAxis('left')
		ax.setLabel(self.tr('Voltage'))

		self.set_timebase(self.TBval)
		self.pwin.disableAutoRange()
		self.pwin.setXRange(0, self.tbvals[self.TBval]*10)
		self.pwin.setYRange(self.MINV, self.MAXV)
		self.pwin.hideButtons()									# Do not show the 'A' button of pg

		for ch in range(self.MAXCHAN):							# initialize the pg trace widgets
			self.traceWidget[ch] = self.pwin.plot([0,0],[0,0], pen = self.traceCols[ch])
			#x=pg.mkPen(self.chanpens[ch], width=.5, style=Qt.DashLine) 
			self.traceWidgetF[ch] = self.pwin.plot([0,0],[0,0], pen = self.traceColsFit[ch])

		right = QVBoxLayout()									# right side vertical layout
		right.setAlignment(Qt.AlignmentFlag(0x0020)) #Qt.AlignTop
		right.setSpacing(self.RPVspacing)

		# Phasor plot window
		self.ppwin = pg.PlotWidget()						# pyqtgraph window
		self.ppwin.setMaximumWidth(250)
		self.ppwin.setMaximumHeight(250)
		self.ppwin.setMinimumHeight(250)
		self.ppwin.disableAutoRange()
		self.ppwin.setXRange(-0.03,3)
		self.ppwin.setYRange(-3,3)
		self.ppwin.hideButtons()									# Do not show the 'A' button of pg
		right.addWidget(self.ppwin)

		for ch in range(5):
			#x=pg.mkPen(self.chanpens[ch], width=2) 
			self.phasorTraces[ch] = self.ppwin.plot([0,0],[0,0], width=3, pen = self.traceCols[ch])

		#Results
		for k in range(self.MAXRES):						# pg textItem to show the Results
			self.resLabs[k] = pg.TextItem()
			self.pwin.addItem(self.resLabs[k])

		H = QHBoxLayout()
		l = QLabel(text=self.tr('Timebase'))
		l.setMaximumWidth(60)
		H.addWidget(l)
		self.TBslider = utils.slider(0, 8, self.TBval, 200, self.set_timebase)
		H.addWidget(self.TBslider)
		right.addLayout(H)
		
		H = QHBoxLayout()
		l = QLabel(text=self.tr('WG'))
		l.setMaximumWidth(25)
		H.addWidget(l)
		self.AWGslider = utils.slider(self.AWGmin, self.AWGmax, self.AWGval,100,self.awg_slider)
		H.addWidget(self.AWGslider)
		self.AWGtext = utils.lineEdit(70, self.AWGval, 6, self.awg_text)
		H.addWidget(self.AWGtext)
		l = QLabel(text=self.tr('Hz'))
		l.setMaximumWidth(20)
		H.addWidget(l)
		right.addLayout(H)	
		
		H = QHBoxLayout()
		self.VLC = QCheckBox('Show Vl and Vc')
		H.addWidget(self.VLC)
		self.VLC.stateChanged.connect(self.action_vlc)
		self.Pause = QCheckBox('Freeze')
		self.Pause.setMaximumWidth(120)
		H.addWidget(self.Pause)
		right.addLayout(H)

		self.SaveButton = QPushButton(self.tr("Save Data"))
		self.SaveButton.clicked.connect(self.save_data)		
		right.addWidget(self.SaveButton)		
		
		l = QLabel(text='<font color="blue">'+self.tr('Impedance Calculator'))
		right.addWidget(l)

		H = QHBoxLayout()
		l = QLabel(text=self.tr('F (in Hz)'))
		l.setMaximumWidth(50)
		H.addWidget(l)
		self.uFreq = utils.lineEdit(50, 150, 6, None)
		H.addWidget(self.uFreq)		

		l = QLabel(text=self.tr('R (in Ohms)'))
		l.setMaximumWidth(75)
		H.addWidget(l)
		self.uRes = utils.lineEdit(50, 1000, 6, None)
		H.addWidget(self.uRes)
		right.addLayout(H)

		
		H = QHBoxLayout()
		l = QLabel(text=self.tr('C (in uF)'))
		l.setMaximumWidth(50)
		H.addWidget(l)
		self.uCap = utils.lineEdit(50, 1, 6, None)
		H.addWidget(self.uCap)
		l = QLabel(text=self.tr('L (in mH)'))
		l.setMaximumWidth(75)
		H.addWidget(l)
		self.uInd = utils.lineEdit(50, 0, 6, None)
		H.addWidget(self.uInd)
		right.addLayout(H)	
		
				
		b=QPushButton(self.tr('Calculate XL, XC and Fo'))
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


	def verify_fit(self,y,y1):
		sum = 0.0
		for k in range(len(y)):
			sum += abs((y[k] - y1[k])/y[k])
		err = sum/len(y)
		if err/sum > 0.01:
			self.msg(self.tr('Curve fitting result rejected'))
			return False
		else:
			return True

	def update(self):
		if self.Pause.isChecked() == True: return
		try:
			if self.VLC.isChecked() == True:
				self.timeData[0], self.voltData[0],\
				self.timeData[1], self.voltData[1],\
				self.timeData[2], self.voltData[2],\
				self.timeData[3], self.voltData[3] = self.p.capture4(self.NP, self.TG)

				self.timeData[4] = self.timeData[0]			
				self.voltData[3] = self.voltData[2] - self.voltData[0]   # voltage across C				
				self.voltData[4] = self.voltData[1] - self.voltData[2]   # voltage across L
				self.voltData[2] = self.voltData[1] - self.voltData[0]   # voltage across LC	
			else:
				self.timeData[0], self.voltData[0],\
				self.timeData[1], self.voltData[1] = self.p.capture2(self.NP, self.TG)
				self.timeData[2] = self.timeData[0]			
				self.voltData[2] = self.voltData[0] - self.voltData[1]   # voltage across LC
		except:
			self.comerr()
			return

		for ch in range(3):
			self.traceWidget[ch].setData(self.timeData[ch], self.voltData[ch])
			try:
				fa = em.fit_sine(self.timeData[ch],self.voltData[ch])
			except Exception as err:
				print("fit_sine error:", err)	
			if fa != None:
				self.traceWidgetF[ch].setData(self.timeData[ch], fa[0])
				if self.verify_fit(self.voltData[ch], fa[0]) == False:
					return
				self.voltDataFit[ch] = fa[0]
				self.Amplitude[ch] = (fa[1][0])
				self.Frequency[ch] = fa[1][1]*1000
				self.Phase[ch] = fa[1][2] * 180/em.pi
				self.fitFine[ch] = 1
			else:
				self.msg(self.tr('Data Analysis Error'))
				return
		phaseDiff = (self.Phase[0] - self.Phase[1])
	
		if self.VLC.isChecked() == True:
			for ch in range(3,5):
				self.traceWidget[ch].setData(self.timeData[ch], self.voltData[ch])
				try:
					fa = em.fit_sine(self.timeData[ch],self.voltData[ch])
				except Exception as err:
					print("fit_sine error:", err)	
				if fa != None:
					self.traceWidgetF[ch].setData(self.timeData[ch], fa[0])
					if self.verify_fit(self.voltData[ch], fa[0]) == False:
						return
					self.voltDataFit[ch] = fa[0]
					self.Amplitude[ch] = (fa[1][0])
					self.Frequency[ch] = fa[1][1]*1000
					self.Phase[ch] = fa[1][2] * 180/em.pi
					self.fitFine[ch] = 1
				else:
					self.msg(self.tr('Data Analysis Error'))
					return			
		
		for k in range(self.MAXRES): self.Results[k] = ''
		
		self.Results[0] = self.tr('Vtotal (A1 = %5.2f V)') %(self.Amplitude[0])
		self.Results[1] = self.tr('Vr (A2 = %5.2f V)') %(self.Amplitude[1])
		self.Results[2] = self.tr('Vlc (A2-A1 = %5.2f V)') %(self.Amplitude[2])

		self.Results[5] = self.tr('F = %5.1f Hz') %(self.Frequency[0])
		self.Results[6] = self.tr('Phase Diff = %5.1f deg') %phaseDiff

		if self.VLC.isChecked() == True:
			self.Results[3] = self.tr('Vc (A3-A1 = %5.2f V)') %(self.Amplitude[3])
			self.Results[4] = self.tr('Vl (A2-A3 = %5.2f V)') %(self.Amplitude[4])
		else:
			self.Results[3] = ''
			self.Results[4] = ''

		for k in range(5):
			self.pwin.removeItem(self.resLabs[k])
			self.resLabs[k] = pg.TextItem(text=self.Results[k],	color= self.resCols[k%5])
			self.resLabs[k].setPos(0, -4 +0.3*k)
			self.pwin.addItem(self.resLabs[k])
		
		for k in range(5,7):
			self.pwin.removeItem(self.resLabs[k])
			self.resLabs[k] = pg.TextItem(text=self.Results[k],	color= self.resCols[k%5])
			self.resLabs[k].setPos(0, 4 -0.3*(k-5))
			self.pwin.addItem(self.resLabs[k])
		

		if self.fitFine[0] == 1 and self.fitFine[1] == 1 and self.fitFine[2] == 1:
			self.draw_phasor()
		# End of update


	def draw_phasor(self):
		Va = self.Amplitude[0]
		Vr = self.Amplitude[1]
		Vlc = self.Amplitude[2]
		pd01 = math.atan(Vr/Va)
		Vl = self.Amplitude[3]
		Vc = self.Amplitude[4]
		
		
		phaseDiff = (self.Phase[1]-self.Phase[0])*np.pi/180
		sign = -np.sign(phaseDiff)
		rx = Va * math.sin(phaseDiff)
		ry = Va * math.cos(phaseDiff) 

		x0 = -0.03
		if self.VLC.isChecked() == True:
			self.phasorTraces[3].setData([x0, x0], [x0, Vl])
			self.phasorTraces[4].setData([x0, x0], [x0, -Vc])
		else:
			self.phasorTraces[3].setData([0,0], [0,0])
			self.phasorTraces[4].setData([0,0], [0,0])
			
		self.phasorTraces[0].setData([0,Vr], [0,sign*Vlc])
		self.phasorTraces[1].setData([0,Vr], [0,0])
		self.phasorTraces[2].setData([0,0], [0,sign*Vlc])
		

	def action_vlc(self):
		if self.VLC.isChecked() == False:
			self.Results[5] = ''
			self.Results[6] = ''
			for ch in range(3,5):
				self.traceWidget[ch].setData([0,0],[0,0])
				self.traceWidgetF[ch].setData([0,0],[0,0])
		
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

			if L != 0 and C != 0:
				f0 = 1./(2*np.pi*np.sqrt(L*C))
				s = 'Xc = %5.1f     Xl = %5.1f    phi = %5.1f deg\nFo = %5.1f Hz'%(Xc, Xl, dphi,f0)
				self.uResult.setText(self.tr(s))
			else:
				s = 'Xc = %5.1f  Xl = %5.1f  phi = %5.1f deg'%(Xc, Xl, dphi)
				self.uResult.setText(self.tr(s))				
		except:
			self.uResult.setText(self.tr('Invalid Input in some field'))
	
	def save_data(self):
		self.timer.stop()
		fn = QFileDialog.getSaveFileName()
		if fn != '':
			dat = []
			if self.VLC.isChecked() == True:
				nc = 5
			else:
				nc = 3
			for ch in range(nc):
					dat.append( [self.timeData[ch], self.voltData[ch] ])
			self.p.save(dat,fn)
			self.msg(self.tr('Traces saved to ') +fn)
		self.timer.start(self.TIMER)		
			
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
		if 1:
			res = self.p.set_sine(self.AWGval)
			ss = '%6.2f'%res
			self.msg(self.tr('AWG set to ') + ss + self.tr(' Hz'))
			T5 = 2000./res
			for k in range(len(self.tbvals)): 
				tmax = 10* self.tbvals[k]
				if tmax > T5:
					self.TBval = k
					self.TBslider.setValue(self.TBval)
					self.set_timebase(k)
					break
		else:
			self.comerr()
			return

	def awg_text(self, text):
		val = float(text)
		if self.AWGmin <= val <= self.AWGmax:
			self.AWGval = val
			self.AWGslider.setValue(int(self.AWGval))
			self.set_wave()

	def awg_slider(self, val):
		if self.AWGmin <= val <= self.AWGmax:
			self.AWGval = val
			self.AWGtext.setText('%d' % (val))
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
	
