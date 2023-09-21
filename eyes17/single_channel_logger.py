# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
'''
Analog Data logger

'''


import sys, time, math, os.path

import utils
from QtVersion import *

import sys, time, functools
from utils import pg
import numpy as np

from layouts import ui_single_channel_logger

from layouts.gauge import Gauge
from layouts.advancedLoggerTools import LOGGER

import utils



class Expt(QtWidgets.QWidget, ui_single_channel_logger.Ui_Form):
	TIMER = 1 #Every 1 mS
	running = True
	TMAX = 10
	MULTIPLEXER_POSITION=0
	voltmeter=None
	MIN=50
	MAX=1500
	def __init__(self, device=None):
		super(Expt, self).__init__()
		self.setupUi(self)
		self.p = device						# connection to the device hardware 
		labelStyle = {'color': 'rgb(200,250,250)', 'font-size': '14pt'}
		self.graph.setLabel('left','Distance -->', units='mm',**labelStyle)
		self.graph.setLabel('bottom','Time -->', units='S',**labelStyle)
		self.graph.setYRange(self.MIN,self.MAX)
		self.graph.setClipToView(True)
		self.graph.setDownsampling(mode='peak')
		self.logging = False
		if self.voltmeter is not None:
			self.voltmeter.reconnect(self.p)
		else:
			from layouts.oscilloscope_widget import DIOINPUT
			try:
				self.voltmeter = DIOINPUT(self,self.p,confirmValues = None)
			except Exception as e:
				print('device not found',e)

		self.datapoints=0
		self.T = 0
		self.time = np.empty(300)
		self.start_time = time.time()
		self.duration = 5

		self.gauge = Gauge(self)
		self.gauge.set_MinValue(self.MIN)
		self.gauge.set_MaxValue(self.MAX)
		self.gaugeLayout.addWidget(self.gauge)			
		self.curve = self.graph.plot(pen='#ff000f', connect="finite")
		self.fitCurve = self.graph.plot(pen='#ff00ff',width=2, connect="finite")
		self.curveData = np.empty(300)


		self.readSensor = None
		#Prepare list of sensor->address map
		self.manualSensor = None
		self.logger = LOGGER(self.p.I2C)		
		self.defaultMap = {}
		for addr in self.logger.sensors:
			self.defaultMap[self.logger.sensors[addr]['name'].split(' ')[0]] = addr

		self.setInput('VL53L0X')

		#self.graph.setRange(xRange=[0, 10])
		self.region = pg.LinearRegionItem()
		self.region.setBrush([255,0,50,50])
		self.region.setZValue(10)
		for a in self.region.lines: a.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor)); 
		self.graph.addItem(self.region, ignoreBounds=False)
		self.region.setRegion([1,5])
		self.p.set_sine(4)

		self.startTime = time.time()
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.updateEverything)
		self.timer.start(2)

	def setInput(self,i):
		if str(i)=='SR04':
			self.readSensor = lambda: [self.p.sr04_distance()]
			self.gauge.set_MinValue(self.MIN)
			self.gauge.set_MaxValue(self.MAX)
			return

		if str(i) in self.defaultMap:
			s = self.logger.sensors[ self.defaultMap[str(i)] ]
			if s['init']():				
				self.readSensor = s['read']
				self.msg('Detected sensor %s successfully'%str(i))
				self.MIN = 50
				self.MAX = 1500
				self.gauge.set_MinValue(self.MIN)
				self.gauge.set_MaxValue(self.MAX)
				return
			else:
				self.msg('Could not detect %s on I2C bus. Default to SR04 sensor'%str(i))

		self.optionBox.setCurrentIndex(0)
		self.setInput('SR04') #Default to SR04
		
	def startLogging(self,state):
		if state:
			self.logging = True
			self.curve.clear()
			self.fitCurve.clear()
			self.msg(self.tr('Start Logging data'))
			self.graph.setYRange(self.MIN,self.MAX)
			self.setDuration()
			
			self.datapoints=0
			self.T = 0
			self.curveData = np.empty(300)
			self.time = np.empty(300)
			self.start_time = time.time()

		else:
			self.msg(self.tr('Stopped Logging data'))
			self.logging = False

	def setDuration(self):
		self.duration = int(self.durationBox.value())
		#self.graph.setRange(xRange=[0,])

	def setInterval(self,i):
		self.timer.stop()
		self.timer.start(i)

	def show_voltmeter(self):
		self.voltmeter.launch('WG')

	def updateEverything(self):
		if self.voltmeter is not None:
			if self.voltmeter.isVisible() and self.voltmeter.type=='input' and self.voltmeter.autoRefresh:
				try:
					v = self.voltmeter.read()
				except Exception as e:
					self.comerr()
					return
				if v is not None:
					self.voltmeter.setValue(v)


		v = self.readSensor()[0]
		if v == None:
			return
		
		self.gauge.update_value(v)
		
		if self.logging:
			self.T = time.time() - self.start_time
			self.curveData[self.datapoints] = v
			self.time[self.datapoints] = self.T
			self.curve.setData(self.time[:self.datapoints],self.curveData[:self.datapoints])
			self.datapoints += 1 
			
			if self.datapoints >= self.curveData.shape[0]-2:
				tmp = self.time
				self.time = np.empty(self.time.shape[0] * 2) #double the size
				self.time[:tmp.shape[0]] = tmp
				self.T = time.time() - self.start_time

				tmp = self.curveData
				self.curveData = np.empty(self.curveData.shape[0] * 2) #double the size
				self.curveData[:tmp.shape[0]] = tmp
			if self.T> self.duration:
				self.startLogging(False)

	def sineFit(self):
		S,E=self.region.getRegion()
		start = (np.abs(self.time[:self.datapoints]- S)).argmin()
		end = (np.abs(self.time[:self.datapoints] - E)).argmin()
		res = 'Amp, Freq, Phase, Offset<br>'

		try:
				fa=utils.fit_sine(self.time[start:end],self.curveData[start:end])
				if fa is not None:
						amp=abs(fa[0])
						freq=fa[1]
						phase = fa[2]
						offset = fa[3]
						s = '%5.2f , %5.3f Hz, %.2f, %.1f<br>'%(amp,freq, phase, offset)
						res+= s
						x = np.linspace(self.time[start],self.time[end],1000)
						self.fitCurve.clear()
						self.fitCurve.setData(x,utils.sine_eval(x,fa))
						self.fitCurve.setVisible(True)

		except Exception as e:
				res+='--<br>'
				print (e.message)
		self.msgBox = QtWidgets.QMessageBox(self)
		self.msgBox.setWindowModality(QtCore.Qt.NonModal)
		self.msgBox.setWindowTitle('Sine Fit Results')
		self.msgBox.setText(res)
		self.msgBox.show()

	def dampedSineFit(self):
		S,E=self.region.getRegion()
		start = (np.abs(self.time[:self.datapoints] - S)).argmin()
		end = (np.abs(self.time[:self.datapoints]- E)).argmin()
		print(self.T,start,end,S,E,self.time[start],self.time[end])
		res = 'Amplitude, Freq, phase, Damping<br>'
		try:
				fa=utils.fit_dsine(self.time[start:end],self.curveData[start:end])
				if fa is not None:
						amp=abs(fa[0])
						freq=fa[1]
						decay=fa[4]
						phase = fa[2]
						s = '%5.2f , %5.3f Hz, %.3f, %.3e<br>'%(amp,freq,phase,decay)
						res+= s
						x = np.linspace(self.time[start],self.time[end],1000)
						self.fitCurve.clear()
						self.fitCurve.setData(x,utils.dsine_eval(x,fa))
						self.fitCurve.setVisible(True)
		except Exception as e:
				res+='--<br>'
				print (e.message)
		self.msgBox = QtWidgets.QMessageBox(self)
		self.msgBox.setWindowModality(QtCore.Qt.NonModal)
		self.msgBox.setWindowTitle('Damped Sine Fit Results')
		self.msgBox.setText(res)
		self.msgBox.show()




	def updateHandler(self,device):
		if(device.connected):
			self.p = device

	def msg(self, m):
		self.msgwin.setText(self.tr(m))

	def saveTraces(self):
		self.timer.stop()
		fn = QFileDialog.getSaveFileName(self,"Save file",QtCore.QDir.currentPath(),
        "Text files (*.txt);;CSV files (*.csv);;All files (*.*)", "CSV files (*.csv)")
		if(len(fn)==2): #Tuple
			fn = fn[0]
		print(fn)
		if fn != '':
			f = open(fn,'wt')
			f.write('time, value')
			f.write('\n')

			for a in range(self.datapoints):
				f.write('%.3f, %.3f\n'%(self.time[a],self.curveData[a]))
			f.close()
			self.msg(self.tr('Traces saved to ') + fn)
		self.timer.start(int(self.intervalBox.value()))




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
