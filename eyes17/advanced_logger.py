'''
An advanced data logger for X vs Y plotting where X and Y can be any float parameter in the following list
- Time
- Voltage outputs: PV1, PV2, 
- Frequency outputs: WG, SQ1
- Voltage inputs : A1,A2,A3,IN1,SEN,CCS,AN8
- Frequency Input
- Capacitance
- Resistance
- Oscilloscope
   - Single Channel with sinusoidal fitting implemented
   - fitted parameters: Freq, Amp, Phase, Offset
- I2C Sensors : Automatically detected
   - Select 1 parameter from any of the detected sensors added automatically to the list
- SR04 Ultrasound Echo Module

Author  : Jithin B.P, jithinbp@gmail.com
Date    : Sep-2019
License : GNU GPL version 3
'''
import sys,time
t = time.time()

import utils
from PyQt5 import QtGui, QtCore, QtWidgets

import pyqtgraph as pg

import math, os.path, struct
from collections import OrderedDict

from layouts import ui_advancedLogger
from layouts.oscilloscope_widget import DIOINPUT, colors
from utils import ConfigParser
import functools
from functools import partial


import numpy as np

class Expt(QtWidgets.QMainWindow, ui_advancedLogger.Ui_MainWindow):
	def __init__(self, device=None):
		super(Expt, self).__init__()
		self.setupUi(self)
		self.splitter.setSizes([100, 400])
		self.logging = False

		self.p = device
		self.I2C = device.I2C		#connection to the device hardware

		self.curve = self.plot.plot(pen=colors[0])
		self.X = []
		self.Y = []
		#Define some keyboard shortcuts for ease of use
		self.shortcutActions={}
		self.shortcuts={" ":self.setRecord,'x':self.setX,'y':self.setY}
		for a in self.shortcuts:
			shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(a), self)
			shortcut.activated.connect(self.shortcuts[a])
			self.shortcutActions[a] = shortcut

		self.XInput = DIOINPUT(self,self.p,confirmValues = self.setXParameters,title="X Axis Parameter")
		self.YInput = DIOINPUT(self,self.p,confirmValues = self.setYParameters,title="Y Axis Parameter")
		#self.XInput.show()

		self.startTime = time.time()
		self.interval = 0.1 #Seconds 
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.updateEverything)
		self.timer.start(2)

	def setConfig(self,text):
		config = ConfigParser(allow_no_value=True)
		config.read_string(text)
		print('received configuration:',config)
		if 'logging' in config:
			if 'interval' in config['logging']:
				self.delayBox.setValue(int(config['logging']['interval']))
			if 'settling' in config['logging']:
				self.settlingTimeBox.setValue(int(config['logging']['settling']))
			if 'datapoints' in config['logging']:
				self.datapointsBox.setValue(int(config['logging']['datapoints']))

		for name, axis in zip(['x-axis', 'y-axis'], [self.XInput, self.YInput]):
			if name in config:
				if 'tool' in config[name]:
					axis.setWindow(config[name]['tool'])
					print(name, ' set to ', config[name]['tool'])
				if 'minimum' in config[name]:
					axis.minValue.setValue(float(config[name]['minimum']))
				if 'maximum' in config[name]:
					axis.maxValue.setValue(float(config[name]['maximum']))
				if 'meter' in config[name]:
					index = axis.subSelection.findText(config[name]['meter'], QtCore.Qt.MatchFixedString)
					if index >= 0:
						 axis.subSelection.setCurrentIndex(index)
				if 'channel' in config[name]:
					index = axis.miniscope.A1Box.findText(config[name]['channel'], QtCore.Qt.MatchFixedString)
					if index >= 0:
						 axis.miniscope.A1Box.setCurrentIndex(index)
				if 'parameter' in config[name]:
					axis.miniscope.activeParameter = int(config[name]['parameter'])-1
					axis.miniscope.list.setCurrentRow(axis.miniscope.activeParameter)
					if 'cross-check-frequency' in config[name]:
						axis.miniscope.freqCheckBox.setChecked(True)
					else:
						axis.miniscope.freqCheckBox.setChecked(False)
				axis.launch()
				axis.activateWindow()
		self.XInput.reposition('bottom-left')		
		self.YInput.reposition('top-left')		

	def setXParameters(self,s):
		self.xLabel.setText(s)
	def setYParameters(self,s):
		self.yLabel.setText(s)

	def setRecord(self,s):
		if s:
			if self.XInput.type == 'output':
				self.XInput.initSweep(self.datapointsBox.value())
			if self.YInput.type == 'output':
				self.YInput.initSweep(self.datapointsBox.value())
			self.plot.setRange(xRange=[self.XInput.minValue.value(),self.XInput.maxValue.value()],yRange=[self.YInput.minValue.value(),self.YInput.maxValue.value()])
			self.logging = True
			time.sleep(0.5)
			#self.XInput.hide()
			#self.YInput.hide()
			self.curve.clear()
			self.X = []
			self.Y = []

			for a in [self.XInput,self.YInput]:
				if a.name == 'Time':
					a.initialize()

			self.startTime = time.time()
			self.interval = self.delayBox.value()/1000.
		else:
			self.logging = False
			self.XInput.message.setText("Done")
			self.YInput.message.setText("Done")

	def setX(self):
		self.XInput.launch()
		self.XInput.activateWindow()
	def setY(self):
		self.YInput.launch()
		self.YInput.activateWindow()

	def updateEverything(self):
		if self.logging:
			if (time.time() - self.startTime) > self.interval:
				self.startTime = time.time()
				x = self.XInput.nextValue()
				time.sleep(self.settlingTimeBox.value()/1000.)
				y = self.YInput.nextValue(freq = x)
				if x == None or y == None:
					self.logging = False #Stop the logging. 
					self.logBox.setChecked(False)
				if x and y:
					self.X.append(x)
					self.Y.append(y)
					self.curve.setData(self.X,self.Y)
		else:
			for a in [self.XInput,self.YInput]:
				if a.isVisible() and a.type=='input' and a.autoRefresh:
					v = a.read()
					if v is not None:
						a.setValue(v)




if __name__ == '__main__':
	import eyes17.eyes
	dev = eyes17.eyes.open()
	app = QtWidgets.QApplication(sys.argv)

	# translation stuff
	lang=QtCore.QLocale.system().name()
	t=QtCore.QTranslator()
	t.load("lang/"+lang, os.path.dirname(__file__))
	app.installTranslator(t)
	t1=QtCore.QTranslator()
	t1.load("qt_"+lang,
	        QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath))
	app.installTranslator(t1)
	mw = Expt(dev)
	mw.show()
	sys.exit(app.exec_())
	
