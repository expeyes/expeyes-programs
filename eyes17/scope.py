# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
import sys, time, math, os.path

import utils
from QtVersion import *

import sys, time
from utils import pg
import numpy as np
import eyes17.eyemath17 as em
from functools import partial

from layouts import ui_scope_layout

class Expt(QtWidgets.QWidget, ui_scope_layout.Ui_Form):
	TIMER = 50
	loopCounter = 0
	AWGmin = 1
	AWGmax = 5000
	AWGval = 1000
	SQ1min = 0
	SQ1max = 50000
	SQ1val = 0
	PV1min = -5.0
	PV1max = 5.0
	PV1val = 0.0
	PV2min = -3.3
	PV2max = 3.3
	PV2val = 0.0
	
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
	
	sources = ['A1','A2','A3', 'MIC','SEN','IN1','AN8']

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

	Wgains = ['80 mV','1V','3V']
	wgainindex = 2

	Waves = ['sine', 'tria', 'SQR2']
	waveindex = 0
	voltmeter=None
	def __init__(self, device=None):
		super(Expt, self).__init__()
		self.setupUi(self)
		try:
			self.setStyleSheet(open(os.path.join(os.path.dirname(__file__),"layouts/style.qss"), "r").read())
		except Exception as e:
			print('stylesheet missing. ',e)
		self.resultCols = utils.makeResultColors()
		self.traceCols = utils.makeTraceColors()
		self.htmlColors = utils.makeHtmlColors()
		self.pwin = pg.PlotWidget(self.pwinview)
		self.plotLayout.addWidget(self.pwin)
		self.p = device						# connection to the device hardware 
			
		self.chanStatus = [1,0,0,0]			# PyQt problem. chanStatus somehow getting preserved ???		

		self.offSliders = [self.slider1,self.slider2,self.slider3,self.slider4]
		for ch in range(self.MAXCHAN):
			self.offSliders[ch].valueChanged.connect(partial (self.set_offset,ch))
			self.offSliders[ch].setStyleSheet('''QSlider::handle:vertical{background: %s;};'''%(self.htmlColors[ch]))
		self.pwin.proxy = pg.SignalProxy(self.pwin.scene().sigMouseMoved, rateLimit=60, slot=self.updateTV)				
		self.pwin.showGrid(x=True, y=True)						# with grid
		
		
		for k in range(self.MAXCHAN):							# pg textItem to show the voltage scales
			self.scaleLabs[k] = pg.TextItem(text='')

		for k in range(self.MAXRES):						# pg textItem to show the Results
			self.resLabs[k] = pg.TextItem()
			self.pwin.addItem(self.resLabs[k])
		
		vLine = pg.InfiniteLine(angle=90, movable=False, pen = 'r')
		self.pwin.addItem(vLine, ignoreBounds=True)
		self.pwin.vLine=vLine
		self.pwin.vLine.setPos(-1)
		
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

		self.CAP.clicked.connect(self.measure_cap)

		self.FREQ.clicked.connect(self.measure_freq)

		self.OD1.stateChanged.connect(self.control_od1)
		self.CCS.stateChanged.connect(self.control_ccs)
		

		
		self.chanSelCB = [self.A1Box,self.A2Box,self.A3Box,self.MICBox]
		self.rangeSelPB = [self.A1Range,self.A2Range,self.A3Range,self.MICRange]
		self.fitSelCB = [self.A1Fit,self.A2Fit,self.A3Fit,self.MICFit]
		self.voltMeterCB = [self.voltMeterCB1,self.voltMeterCB2,self.voltMeterCB3]
		for ch in range(4):
			self.chanSelCB[ch].stateChanged.connect(partial (self.select_channel,ch))
			self.chanSelCB[ch].setStyleSheet('''border: 1px solid %s;'''%(self.htmlColors[ch])) #<font color="%s">
			
			self.rangeSelPB[ch].currentIndexChanged['int'].connect(partial(self.select_range,ch))

		self.chanSelCB[0].setChecked(True)

		self.trigBox.addItems(self.sources)
		self.A1Map.addItems(self.sources)
		self.recover()
		self.timer = QTimer()
		self.timer.timeout.connect(self.update)
		self.timer.start(self.TIMER)


	def recover(self):		# Recover the settings before it got disconnected
		self.msgwin.setText('<font color="green">' + self.tr('Reconnecting...'))
		try:
			self.control_od1()
			self.pv1_text()
			self.pv2_text()
			self.p.set_sqr1(self.SQ1val, self.dutyCycle)
			self.select_wave(self.waveindex)
			self.p.set_wave(self.AWGval)
			self.select_wgain(self.wgainindex)
			self.set_trigger(self.Triglevel*1000)
			self.p.set_sine(self.AWGval)
			self.p.configure_trigger(0, 'A1', 0)
			#self.select_range((0,2))
			#self.select_range((1,2))
			#self.select_range((2,0))
			#self.select_range((3,0))
			if self.p.calibrated:
				cal = self.tr('Calibrated ')
			else:
				cal = self.tr('Not Calibrated ')
			self.msgwin.setText('<font color="green">' + self.tr('Device Reconnected:')+cal)
			if self.p.version_number >= 5.0:
				self.pcsFrame.show()
				self.CCS.hide()
			else:
				self.pcsFrame.hide()
				self.CCS.show()

			if self.voltmeter is not None:
				self.voltmeter.reconnect(self.p)
			else:
				from layouts.oscilloscope_widget import DIOINPUT
				try:
					self.voltmeter = DIOINPUT(self,self.p,confirmValues = None)
				except Exception as e:
					print('device not found',e)
			for a,b in zip([self.WGLabel,self.SQ1Label,self.PV1Label,self.PV2Label],['WG','SQ1','PV1','PV2']):
				a.clicked.connect(partial(self.voltmeter.launch,b))


		except Exception as e:
			self.msgwin.setText('<font color="red">' + self.tr('Error. Could not connect. Check cable. ') + str(e))
		

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

	def set_offset(self, ch):
		self.offValues[ch] = self.offSliders[ch].value()

	def cross_hair(self):
		if self.Cross.isChecked() == False:
			self.pwin.vLine.setPos(-1)


	def showVoltagesAtCursor(self,xval):
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

	def updateTV(self, evt):
		if self.p == None: return
		if self.Cross.isChecked() == False:
			self.pwin.vLine.setPos(-1)
			return
		pos = evt[0]  			## using signal proxy turns original arguments into a tuple
		if self.pwin.sceneBoundingRect().contains(pos):
			mousePoint = self.pwin.plotItem.vb.mapSceneToView(pos)
			xval = mousePoint.x()
			self.pwin.vLine.setPos(mousePoint.x())
			self.showVoltagesAtCursor(xval)

			
		
		
	def update(self):
		if self.p is None:
			return
		if not self.p.connected:
			self.comerr()
			return
		if self.voltmeter.isVisible() and self.voltmeter.type=='input' and self.voltmeter.autoRefresh:
			try:
				v = self.voltmeter.read()
			except Exception as e:
				self.comerr()
				return
			if v is not None:
				self.voltmeter.setValue(v)
		if self.Freeze.isChecked(): return

		try:
			if self.chanStatus[2] == 1 or self.chanStatus[3] == 1: # channel 3 or 4 selected  	
				self.timeData[0], self.voltData[0],	\
				self.timeData[1], self.voltData[1], \
				self.timeData[2], self.voltData[2], \
				self.timeData[3], self.voltData[3] = self.p.capture4(self.NP, self.TG,str(self.A1Map.currentText()), trigger=self.trigEnable.isChecked())				
			elif self.chanStatus[1] == 1:    	# channel 2 is selected  	
				self.timeData[0], self.voltData[0], \
				self.timeData[1], self.voltData[1] = self.p.capture2(self.NP, self.TG,str(self.A1Map.currentText()), trigger=self.trigEnable.isChecked())
			elif self.chanStatus[0] == 1: 		# only A1 selected
				self.timeData[0], self.voltData[0] = self.p.capture1(str(self.A1Map.currentText()), self.NP, self.TG, trigger=self.trigEnable.isChecked())
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
						self.fitSelCB[ch].setText(s)
				else:
					self.fitSelCB[ch].setText('')

		if self.Diff.isChecked() == True and self.chanStatus[0] == 1 and self.chanStatus[1] == 1:
			r = 16./self.rangeVals[0]
			self.diffTraceW.setData(self.timeData[0], r*(self.voltData[0]-self.voltData[1]))

		if self.Cross.isChecked():
			self.showVoltagesAtCursor(self.pwin.vLine.x())
		else:
			for k in range(self.MAXRES):
				try:self.pwin.removeItem(self.resLabs[k])
				except: pass

		###PCS Monitoring in version 5+
		if self.p.version_number >= 5.0: #Current source monitoring
			self.pcsVal.display(int(self.p.get_voltage('AN8')*1e3))

		self.loopCounter += 1
		if self.loopCounter % 5 == 0:
			for ch in range(3):
				if self.voltMeterCB[ch].isChecked() == True:
					try:
						v = self.p.get_voltage(self.sources[ch])		# Voltmeter functions
					except:
						self.comerr()
					self.voltMeterCB[ch].setText(unicode(self.tr('A%d %5.3f V')) %(ch+1,v))
				else:
					self.voltMeterCB[ch].setText(self.tr('A%d'%(ch+1)))			

			try:
				res = self.p.get_resistance()
				if res != np.Inf and res > 100  and  res < 100000:
					self.RES.setText('Resistance: <font color="blue">'+unicode(self.tr('%5.0f Ohm')) %(res))
				else:
					self.RES.setText(self.tr('Resistance: <100Ohm  or  >100k'))
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

	
	def select_range(self,ch,index):
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
		src = self.sources[self.Trigindex]
		self.Trigindex = index
		if index>3:
			self.Trigindex = 0
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

	def pv1_text(self):
		try:
			val = float(self.PV1text.value())
		except Exception as e:
			return
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
			self.PV1text.setValue(val)
			try:
				self.p.set_pv1(val)
			except:
				self.comerr()

	def pv2_text(self):
		try:
			val = self.PV2text.value()
		except:
			return
		if self.PV2min <= val <= self.PV2max:
			self.PV2val = val
			try:
				self.p.set_pv2(val)
				self.PV2slider.setValue(int(val*1000))
				self.pcsVal_I.display((val+3.3)/6.6)
			except:
				self.comerr()
				
	def pv2_slider(self, pos):
		val = float(pos)/1000.0
		if self.PV2min <= val <= self.PV2max:
			self.PV2val = val
			self.PV2text.setValue(val)
			self.pcsVal_I.setText('%.2f mA'%(3.3-3.3*((val+3.3)/6.6)))
			try:
				self.p.set_pv2(val)
			except:
				self.comerr()

	def pcs_slider(self,val):
		self.PV2slider.setValue(val)
				
	def sq1_dc(self):
		try:
			val = self.SQ1DCtext.value()
		except:
			return
		if 1 <= val <= 99:
			self.dutyCycle = val
			self.sq1_text()

	def sq1_text(self):
		try:
			val = float(self.SQ1text.value())
		except Exception as e:
			print(e)
			return
		if self.SQ1min <= val <= self.SQ1max:
			self.SQ1val = val
			self.SQ1slider.setValue(self.SQ1val)
			try:
				if 0 <= val < 4 : val = 0
				self.SQ1text.setValue(val)
				res = self.p.set_sqr1(val, self.dutyCycle)
				ss = '%5.1f'%res
				self.msg(self.tr('sqr1 set to ') + ss)
			except:
				self.comerr()
		else:
			self.SQ1text.setValue(self.SQ1min)

	def sq1_slider(self, val):
		if self.SQ1min <= val <= self.SQ1max:
			self.SQ1val = val
			self.SQ1text.setValue(val)
			self.sq1_text()
				
	def select_wgain(self,index):
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
		except Exception as e:
			print('what',e)
			self.comerr()

	def select_wave(self,index):
		self.waveindex = index
		self.set_wave()

	def awg_text(self):
		text = self.AWGtext.value()
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
			self.AWGtext.setValue(val)
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
					self.CAP.setText('MEASURE CAP(IN1) '+ ss +self.tr(' pF'))
				elif cap < 1.0e-6:
					ss = '%6.1f'%(cap*1e9)
					self.CAP.setText('MEASURE CAP(IN1) '+ ss +self.tr(' nF'))
				elif cap < 1.0e-3:
					ss = '%6.1f'%(cap*1e6)
					self.CAP.setText('MEASURE CAP(IN1) '+ ss +self.tr(' uF'))
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
			self.FREQ.setText(u'MEASURE FREQUENCY(IN2) '+unicode(self.tr('%5.1fHz %4.1f%%')) %(fr,dc))
		else:
			self.FREQ.setText(u'MEASURE FREQUENCY(IN2) '+self.tr('No signal'))
	
	def show_voltmeter(self):
		self.voltmeter.launch('Voltmeter')
		
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
	
