'''
Code for viewing I2C sensor data using ExpEYES
Logs data from various sensors.
Author  : Jithin B.P, jithinbp@gmail.com
Date    : Sep-2019
License : GNU GPL version 3
'''
import sys
from PyQt5 import QtGui, QtCore, QtWidgets
from collections import OrderedDict
import time, os.path

from sensor_utilities import DIOSENSOR, DIOROBOT, DIOCONTROL, SENSORROW
from sensorscope_utilities import DIOSENSORSCOPE

from layouts import ui_sensor_logger
from layouts.advancedLoggerTools import LOGGER



class Expt(QtWidgets.QWidget, ui_sensor_logger.Ui_Form):
	def __init__(self, device=None):
		QtWidgets.QWidget.__init__(self)
		self.setupUi(self)
		self.p = device
		self.I2C = device.I2C	        #connection to the device hardware
		self.I2C.config(400000)
		self.sensorList = []
		
		#Prepare list of sensor->address map
		self.manualSensor = None
		logger = LOGGER(self.I2C)		
		self.defaultMap = {}
		for addr in logger.sensors:
			self.defaultMap[logger.sensors[addr]['name'].split(' ')[0]] = addr

		self.sensorCombo.addItems(self.defaultMap.keys())
		
		#Non I2C Sensors
		self.nonI2CSensors={}
		self.nonI2CSensors['SR04'] = {'name':'SR04 Distance Sensor','init':lambda **kwargs: print('init sr04'),'read':lambda: [self.p.sr04_distance()],'min':[0],'max':[200],'fields':['Distance']}
		self.nonI2CSensors['Voltage A1'] = {'name':'A1 Voltage Measurement','init':lambda **kwargs: print('init A1'),'read':lambda: [self.p.get_voltage('A1')],'min':[-16],'max':[16],'fields':['V']}
		self.nonI2CSensors['Voltage SEN'] = {'name':'SEN Voltage Measurement','init':lambda **kwargs: print(''),'read':lambda: [self.p.get_voltage('SEN')],'min':[0],'max':[3.3],'fields':['V']}
		self.nonI2CSensors['Resistance'] = {'name':'SEN-GND Resistance Measurement','init':lambda **kwargs: print(''),'read':lambda: [self.p.get_resistance()],'min':[100],'max':[100e3],'fields':['Ohms']}

		self.sensorCombo.addItems(self.nonI2CSensors.keys())

		self.startTime = time.time()
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.updateEverything)
		self.timer.start(2)
		self.scan()

	def setManualSensor(self,name):
		self.manualSensor = str(name)
		self.addressBox.setValue(self.defaultMap.get(self.manualSensor,0))

	def addSensor(self):
		if self.manualSensor in self.defaultMap:
			addr = self.addressBox.value()
			logger = LOGGER(self.I2C)		
			s = logger.sensors[ self.defaultMap[self.manualSensor] ]
			btn = SENSORROW(self,name=s['name'].split(' ')[0],address=addr,description=' '.join(s['name'].split(' ')[1:])+'\n\nA Manually added I2C sensor.')
			dialog = DIOSENSOR(self,s, addr)
			btn.launchButton.clicked.connect(dialog.launch)
			self.sensorLayout.addWidget(btn)
			self.sensorList.append([dialog,btn, logger])
		elif self.manualSensor in self.nonI2CSensors:
			s = self.nonI2CSensors[self.manualSensor]
			btn = SENSORROW(self,name=s['name'].split(' ')[0],address=0,description=' '.join(s['name'].split(' ')[1:])+'\n\nNot an I2C sensor.')
			dialog = DIOSENSOR(self,s, 0)
			btn.launchButton.clicked.connect(dialog.launch)
			self.sensorLayout.addWidget(btn)
			self.sensorList.append([dialog,btn])
			


	def updateEverything(self):
		for a in self.sensorList:
			if a[0].isVisible():
				if a[0].isPaused == 0 or (a[0].currentPage != None and a[0].currentPage == 0): #If on logger page(1) , pause button should be unchecked
					v = a[0].readValues()
					if v is not None:
						a[0].setValue(v)

			if a[2] is not None: #scopedialog
				if a[2].isVisible():
					a[2].iterateScope()

	############ I2C SENSORS #################
	def scan(self):
		if self.p.connected:
			logger = LOGGER(self.I2C)		
			x = logger.I2CScan()
			print('Responses from: ',x)
			self.resultLabel.setText('Responses from addresses: '+str(x))
			for a in self.sensorList:
				a[0].setParent(None)
				a[1].setParent(None)
				a[2].setParent(None)
			self.sensorList = []
			for a in x:
				possiblesensors = logger.sensormap.get(a,None)
				if len(possiblesensors)>0:
					## Check ID and remove duplicates
					if 'BMP180' in possiblesensors:
						ID = self.p.I2C.readBulk(a, 0xD0, 1)
						if ID[0] != 0x55: # Not BMP180
							possiblesensors.remove('BMP180')
						else:
							possiblesensors.remove('MS5611')

					for sens in possiblesensors:

						s = logger.namedsensors.get(sens)
						logger.set_device(self.p)
						btn = SENSORROW(self,name=s['name'].split(' ')[0],address=a,description=' '.join(s['name'].split(' ')[1:])+'\n\nA sensor that uses the I2C port to communicate')
						dialog = DIOSENSOR(self,s, a)
						if 'startscope' in s:
							scopedialog = DIOSENSORSCOPE(self,s, a, self.p)
							btn.launchScopeButton.clicked.connect(scopedialog.launch)
						else:
							btn.launchScopeButton.setVisible(False)
							scopedialog = None
						btn.launchButton.clicked.connect(dialog.launch)
						self.sensorLayout.addWidget(btn)
						self.sensorList.append([dialog,btn,scopedialog, logger])
						continue

				s = logger.controllers.get(a,None)
				if s is not None:
					btn = QtWidgets.QPushButton(s['name']+':'+hex(a))
					dialog = DIOCONTROL(self,s, a)
					btn.clicked.connect(dialog.launch)
					self.sensorLayout.addWidget(btn)
					self.sensorList.append([dialog,btn, logger])
					continue

				s = logger.special.get(a,None)
				if s is not None:
					btn = QtWidgets.QPushButton(s['name']+':'+hex(a))
					dialog = DIOROBOT(self,s, a)
					btn.clicked.connect(dialog.launch)
					self.sensorLayout.addWidget(btn)
					self.sensorList.append([dialog,btn, logger])
					continue

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
	
