# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
import sys, time, math, os.path, platform, importlib

import utils
from QtVersion import *

import sys, time, tempfile, json, socket
from utils import pg
import numpy as np
import eyes17.eyemath17 as em
from functools import partial
import json
from layouts import ui_list_layout, syntax
from layouts.advancedLoggerTools import LOGGER

from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage


import os
from PyQt5.QtWidgets import QTreeWidgetItem


pf = platform.platform()
print (pf)	
if 'Windows' in pf:
	import diodeIV, editor, filterCircuit, induction, MPU6050, npnCEout, pendulumVelocity, thermocouplelogger
	import plotIV, pnpCEout, pt100, RCtransient, RLCsteadystate, RLCtransient, BHCurve, lightsensorlogger, data_logger
	import RLtransient, rodPendulum, scope, soundBeats, soundFreqResp, soundVelocity, drivenpendulum
	import sr04dist, utils, logger, XYplot, i2cLogger, tof, advanced_logger, blockcoding

"""
Translations in advance for the menus:
the top menu titles
"""

QT_TRANSLATE_NOOP('MainWindow','Device')
QT_TRANSLATE_NOOP('MainWindow','School Expts')
QT_TRANSLATE_NOOP('MainWindow','Electronics')
QT_TRANSLATE_NOOP('MainWindow','Electrical')
QT_TRANSLATE_NOOP('MainWindow','Sound')
QT_TRANSLATE_NOOP('MainWindow','Mechanics')
QT_TRANSLATE_NOOP('MainWindow','Other Expts')
QT_TRANSLATE_NOOP('MainWindow','I2C Modules')
QT_TRANSLATE_NOOP('MainWindow','PythonCode')

"""
The first submenu
"""
QT_TRANSLATE_NOOP('MainWindow','Reconnect')
QT_TRANSLATE_NOOP('MainWindow','LightBackGround')
QT_TRANSLATE_NOOP('MainWindow','DarkBackGround')
QT_TRANSLATE_NOOP('MainWindow','Choose Language')
QT_TRANSLATE_NOOP('MainWindow','Screenshot')
QT_TRANSLATE_NOOP('MainWindow','Whole Window Alt-s')
QT_TRANSLATE_NOOP('MainWindow','Graph Only Alt-p')
QT_TRANSLATE_NOOP('MainWindow','Credits')
QT_TRANSLATE_NOOP('MainWindow','Experiment List')

schoolExpts = [ 
[QT_TRANSLATE_NOOP('MainWindow',"Voltage measurement"), ('2.1','measure-dc')],
[QT_TRANSLATE_NOOP('MainWindow',"Resistance measurement"), ('2.2','res-measure')],
[QT_TRANSLATE_NOOP('MainWindow',"Resistors in Series"), ('2.3','res-series')],
[QT_TRANSLATE_NOOP('MainWindow',"Resistors in Parallel"), ('2.4','res-parallel')],
[QT_TRANSLATE_NOOP('MainWindow',"Capacitance measurement"), ('2.5','cap-measure')],
[QT_TRANSLATE_NOOP('MainWindow',"Capacitors in Series"), ('2.6','cap-series')],
[QT_TRANSLATE_NOOP('MainWindow',"Capacitors in Parallel"), ('2.7','cap-parallel')],
[QT_TRANSLATE_NOOP('MainWindow',"Resistance by Ohm's law"), ('2.8','res-compare')],
[QT_TRANSLATE_NOOP('MainWindow','Direct and Alternating Currents'), ('2.9','ac-dc')],
[QT_TRANSLATE_NOOP('MainWindow','AC mains pickup'), ('2.10','line-pickup')],
[QT_TRANSLATE_NOOP('MainWindow','Separating AC and DC'), ('2.11','acdc-separating')],
[QT_TRANSLATE_NOOP('MainWindow','Conducting Human body'), ('2.12','conducting-human')],
[QT_TRANSLATE_NOOP('MainWindow','Resistance of Human body'), ('2.13','res-body')],
[QT_TRANSLATE_NOOP('MainWindow','Light Dependent Resistor'), ('2.14','ldr')],
[QT_TRANSLATE_NOOP('MainWindow','Lemon Cell'), ('2.15','lemon-cell')],
[QT_TRANSLATE_NOOP('MainWindow','Simple AC generator'), ('2.16','ac-generator')],
[QT_TRANSLATE_NOOP('MainWindow','Transformer'), ('2.17','transformer')],
[QT_TRANSLATE_NOOP('MainWindow','Resistance of Water'), ('2.18','res-water')],
[QT_TRANSLATE_NOOP('MainWindow','Generating Sound'), ('2.19','sound-generator')],
[QT_TRANSLATE_NOOP('MainWindow','Digitizing Sound'), ('2.20','sound-capture')],
[QT_TRANSLATE_NOOP('MainWindow','Stroboscope'), ('2.21','stroboscope')],
]

'''
testEquipment = [ 
[QT_TRANSLATE_NOOP('MainWindow','Oscilloscope'),('3.1', 'scope')]
#[QT_TRANSLATE_NOOP('MainWindow','Monitor and Control'), 'mon-con']
]
'''


electronicsExptsScope = [ 
[QT_TRANSLATE_NOOP('MainWindow','Oscilloscope'),('3.1', 'scope')],
[QT_TRANSLATE_NOOP('MainWindow','Halfwave Rectifier'),('3.2','halfwave')],
[QT_TRANSLATE_NOOP('MainWindow','Fullwave Rectifier'),('3.3','fullwave')],
[QT_TRANSLATE_NOOP('MainWindow','Diode Clipping'),('3.4','clipping')],
[QT_TRANSLATE_NOOP('MainWindow','Diode Clamping'),('3.5','clamping')],
[QT_TRANSLATE_NOOP('MainWindow','IC555 Multivibrator'),('3.6','osc555')],
[QT_TRANSLATE_NOOP('MainWindow','Transistor Amplifier (CE)'),('3.7','npnCEamp')],
[QT_TRANSLATE_NOOP('MainWindow','Inverting Amplifier'),('3.8','opamp-inv')],
[QT_TRANSLATE_NOOP('MainWindow','Non-Inverting Amplifier'),('3.9','opamp-noninv')],
[QT_TRANSLATE_NOOP('MainWindow','Summing Amplifier'),('3.10','opamp-sum')],
[QT_TRANSLATE_NOOP('MainWindow','Logic Gates'),('3.11','logic-gates')],
[QT_TRANSLATE_NOOP('MainWindow','Clock Divider Circuit'),('3.12','clock-divider')]
]

electronicsExpts = [ 
[QT_TRANSLATE_NOOP('MainWindow','Diode Characteristics'),('3.13','diodeIV')],
[QT_TRANSLATE_NOOP('MainWindow','NPN Output Characteristics'),('3.14','npnCEout')],
[QT_TRANSLATE_NOOP('MainWindow','PNP Output Characteristics'),('3.15','pnpCEout')],
#[QT_TRANSLATE_NOOP('MainWindow','AM and FM'), 'amfm']
]


electricalExpts = [ 
[QT_TRANSLATE_NOOP('MainWindow','Plot I-V Curve'),('4.1','plotIV')],
[QT_TRANSLATE_NOOP('MainWindow','XY Plotting'),('4.2','XYplot')],
[QT_TRANSLATE_NOOP('MainWindow','RLC Steady state response'),('4.3','RLCsteadystate')],
[QT_TRANSLATE_NOOP('MainWindow','RC Transient response'),('4.4','RCtransient')],
[QT_TRANSLATE_NOOP('MainWindow','RL Transient response'),('4.5','RLtransient')],
[QT_TRANSLATE_NOOP('MainWindow','RLC transient response'),('4.6','RLCtransient')],
[QT_TRANSLATE_NOOP('MainWindow','Frequency Response of Filter Circuit'),('4.7','filterCircuit')],
[QT_TRANSLATE_NOOP('MainWindow','Electromagnetic Induction'),('4.8','induction')]
]

soundExpts = [
[QT_TRANSLATE_NOOP('MainWindow','Frequency Response of Piezo Buzzer'),('5.1','soundFreqResp')],
[QT_TRANSLATE_NOOP('MainWindow','Velocity of Sound'), ('5.2','soundVelocity')],
[QT_TRANSLATE_NOOP('MainWindow','Sound beats'), ('5.3','soundBeats')]
]

mechanicsExpts = [
[QT_TRANSLATE_NOOP('MainWindow','Rod Pendulum with Light barrier'), ('6.1','rodPendulum')],
[QT_TRANSLATE_NOOP('MainWindow','Pendulum Waveform'),('6.2','pendulumVelocity')],
[QT_TRANSLATE_NOOP('MainWindow','Driven Pendulum resonance'),('6.3','driven-pendulum')],
[QT_TRANSLATE_NOOP('MainWindow','Distance by HY-SRF04 Echo module'), ('6.4','sr04dist')],
[QT_TRANSLATE_NOOP('MainWindow','Gravity by Time of Flight'), ('6.5','tof')]
]

otherExpts = [ 
[QT_TRANSLATE_NOOP('MainWindow','Temperatue, PT100 Sensor'), ('7.1','pt100')],
[QT_TRANSLATE_NOOP('MainWindow','Simple Data Logger'), ('7.2','logger')],
[QT_TRANSLATE_NOOP('MainWindow','Continuous Data Logger'),('3.16','data_logger')],
[QT_TRANSLATE_NOOP('MainWindow','Advanced Data Logger'), ('7.3','advanced_logger')],
[QT_TRANSLATE_NOOP('MainWindow','Visual Programming Editor'), ('7.4','blockcoding')]
]

modulesI2C = [ 
[QT_TRANSLATE_NOOP('MainWindow','Magnetic Hysteresis (MPU925x Sensor)'),('8.1', 'BHCurve')],
[QT_TRANSLATE_NOOP('MainWindow','Luminosity(TSL2561) Logger'),('8.2', 'lightsensorlogger')],
[QT_TRANSLATE_NOOP('MainWindow','Temperature(MAX6675) Logger'),('8.5', 'thermocouplelogger')],
[QT_TRANSLATE_NOOP('MainWindow','MPU-6050 Acccn, Velocity and Temp'), ('8.3', 'MPU6050')],
[QT_TRANSLATE_NOOP('MainWindow','General Purpose I2C Sensors'), ('8.4', 'i2cLogger')]
]

pythonCodes = [ 
[QT_TRANSLATE_NOOP('MainWindow','Read Inputs'),  'readInputs'],
[QT_TRANSLATE_NOOP('MainWindow','Set DC Voltages'), 'setVoltages'],
[QT_TRANSLATE_NOOP('MainWindow','Capture Single Input'), 'capture1'],
[QT_TRANSLATE_NOOP('MainWindow','Capture Two Inputs'), 'capture2'],
[QT_TRANSLATE_NOOP('MainWindow','Capture Four Inputs'), 'capture4'],
[QT_TRANSLATE_NOOP('MainWindow','Triangular Waveform'), 'triangularWave'],
[QT_TRANSLATE_NOOP('MainWindow','Arbitrary Waveform'), 'waveforms'],
[QT_TRANSLATE_NOOP('MainWindow','Waveform Table'), 'table'],
[QT_TRANSLATE_NOOP('MainWindow','RC Transient'), 'RCtransient'],
[QT_TRANSLATE_NOOP('MainWindow','RL Transient'), 'RLtransient'],
[QT_TRANSLATE_NOOP('MainWindow','RC Integration'), 'RCintegration'],
[QT_TRANSLATE_NOOP('MainWindow','Clipping with Diode'), 'clipping'],
[QT_TRANSLATE_NOOP('MainWindow','Clamping with Diode'), 'clamping'],
[QT_TRANSLATE_NOOP('MainWindow','Fullwave Rectifier'), 'fullwave'],
[QT_TRANSLATE_NOOP('MainWindow','NPN Ib vs IC plot'), 'npnTransferChar'],
[QT_TRANSLATE_NOOP('MainWindow','Fourier Transform'), 'FourierTransform'],
[QT_TRANSLATE_NOOP('MainWindow','Rod Pendulum'), 'rodpend']
]


class helpWin(QWebView):
		
	def closeEvent(self, e):
		"""
		Sends a message to self.parent to tell that the checkbox for
		the help window should be unchecked.
		"""
		self.parent.uncheckHelpBox.emit()
		return
			
	def __init__(self, parent, name = '', lang="en"):
		"""
		Class for the help window
		:param parent: this is the main window
		:param name: a tuple (title, HTML file indication)
		name[1] can be either a simple string or another iterable. When it is
		a simple string, it means that the file to open is in htm/<name>.html;
		on the contrary, name[1] is a list of file names, without their
		.html suffix, to be searched in a list of directories; the first
		hit during the search defines the file to open.
		:param lang: the desired language
		"""

		QWebView.__init__(self)
		self.parent=parent
		self.helpPath = os.path.join(os.path.dirname(os.path.abspath(__file__)),'helpFiles/')

	def setHelp(self,name = '', lang = "en"):
		self.lang=lang
		fn = self.helpPath + lang[:2] + '/' + name + '.html'
		print(fn)
		self.load(QUrl.fromLocalFile(fn))





class Expt(QtWidgets.QWidget, ui_list_layout.Ui_Form):
	def __init__(self, device=None):
		super(Expt, self).__init__()
		self.clickCallbacks={}
		self.helpFiles={}
		self.setupUi(self)
		self.expName = ''
		self.samplepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),"blockly/samples") 
		try:
			self.setStyleSheet(open(os.path.join(os.path.dirname(__file__),"layouts/style.qss"), "r").read())
		except Exception as e:
			print('stylesheet missing. ',e)
		self.p = device						# connection to the device hardware 

		self.web = helpWin(self,'block coding')
		self.webLayout.addWidget(self.web)
		self.lang="en"
		
		menus = {"School Expts":schoolExpts, "Electronics":electronicsExptsScope}
		for a in menus:
			parent_itm = QTreeWidgetItem(self.directoryBrowser, [self.tr(a)])
			for e in menus[a]:
				item = QTreeWidgetItem(parent_itm, [self.tr(e[0])])
				self.clickCallbacks[item.text(0)] = lambda item=e: self.scope_help(item)
				self.helpFiles[item.text(0)] = e[1][0]


		menus = {"Electronics":electronicsExpts,"Electrical":electricalExpts, "Sound":soundExpts, "Mechanics":mechanicsExpts, "Other Expts":otherExpts, "I2C Modules":modulesI2C}
		for a in menus:
			parent_itm = QTreeWidgetItem(self.directoryBrowser, [self.tr(a)])
			for e in menus[a]:
				item = QTreeWidgetItem(parent_itm, [self.tr(e[0])])
				self.clickCallbacks[item.text(0)] = lambda exp = e: self.callExpt(exp)
				self.helpFiles[item.text(0)] = e[1][0]


		menus = {"PythonCode":pythonCodes}
		for a in menus:
			parent_itm = QTreeWidgetItem(self.directoryBrowser, [self.tr(a)])
			for e in menus[a]:
				item = QTreeWidgetItem(parent_itm, [self.tr(e[0])])
				self.clickCallbacks[item.text(0)] = lambda exp = e: self.runCode(exp)
				self.helpFiles[item.text(0)] = e[1][0]


	def callExptReference(self,exptref, scoperef, coderef):
		self.callExpt = exptref
		self.scope_help = scoperef
		self.runCode = coderef
	

	def loadExample(self, item, col):
		if item.text(col) in self.clickCallbacks:
			self.clickCallbacks[item.text(col)]()

	def loadHelp(self, item, col):
		if item.text(col) in self.helpFiles:
			expt = self.helpFiles[item.text(col)]
			print(expt)
			self.web.setHelp(expt,self.lang)


	'''
	def callExpt(self, e):
		"""
		:parm: e lst with a title and a HTML file designation; when e[1]
		is not a string, then it is an iterable with possible HTML file names,
		and the last file name may also be a module name.
		"""	
		self.title=e[0] # record the title of the experiments, for snapshots
		module_name =  e[1] if type(e[1]) is str else e[1][-1]
		explib = importlib.import_module(module_name)
		try:
			try:
				self.expWidget.timer.stop()     # Stop the timer loop of current widget			
			except:
				pass
			self.expWidget= None				 # Let python delete it
			w = explib.Expt(self.p)
			self.setWindowTitle(self.tr(e[0]))

			for i in reversed(range(self.exptLayout.count())): 
				self.exptLayout.itemAt(i).widget().setParent(None)

			self.exptLayout.addWidget(w)
			self.expWidget = w
			self.expName = e[1]
		except Exception as err:
			print("Exception:", err)	
			self.expName = ''
			self.setWindowTitle(self.tr('Failed to load %s') %e[0])
		return




	def scope_help(self,e):
		if self.expName != 'scope':
			explib = importlib.import_module('scope')
			try:
				try:
					self.expWidget.timer.stop()     # Stop the timer loop of current widget			
				except:
					pass
				for i in reversed(range(self.exptLayout.count())): 
					self.exptLayout.itemAt(i).widget().setParent(None)

				self.expWidget = None
				w = explib.Expt(self.p) 
				self.exptLayout.addWidget(w)
				self.expWidget = w
				self.expName = 'scope'
			except:
				self.expName = ''
				self.setWindowTitle(self.tr('Failed to load scope'))

		self.setWindowTitle(self.tr(e[0]))
		self.title = e[0]
	


	def runCode(self, e):
		if self.expName != 'editor': #Moved here from some other non coding expt
			self.hlpName = e
			self.callExpt( ['Python Coding', ('9.0','editor')])
		self.expWidget.mycode = e[1]
		self.expWidget.update()

	'''

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
