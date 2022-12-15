# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
'''
The CD74HC4067 is an analog multiplexer that can map 16 inputs to a single output based on 4 configuration inputs.
The configuration inputs (S0-S3) are connected to CS1-4. 

This data logger sweeps values of CS1-CS4(4 bit. total 16 combinations), and records plots for each. Thereby making a multi track 
analog data logger.

'''


import sys, time, math, os.path

import utils
from QtVersion import *

import sys, time, functools
from utils import pg
from eyes17.SENSORS import ADS1115

from layouts import ui_multiplexed_logger
from layouts.advancedLoggerTools import LOGGER

class Expt(QtWidgets.QWidget, ui_multiplexed_logger.Ui_Form):
	TIMER = 1 #Every 1 mS
	running = True
	TMAX = 10
	MULTIPLEXER_POSITION=0
	def __init__(self, device=None):
		super(Expt, self).__init__()
		self.setupUi(self)
		self.p = device						# connection to the device hardware 
		self.ADC = ADS1115.connect(self.p.I2C)
		self.ADC.setGain('GAIN_SIXTEEN') #'GAIN_TWOTHIRDS','GAIN_ONE','GAIN_TWO','GAIN_FOUR','GAIN_EIGHT','GAIN_SIXTEEN'
		self.ADC.setDataRate(128)
		
		self.cbs = [self.checkBox_0,self.checkBox_1,self.checkBox_2,self.checkBox_3,self.checkBox_4,self.checkBox_5,self.checkBox_6,self.checkBox_7,self.checkBox_8,self.checkBox_9,self.checkBox_10,self.checkBox_11,self.checkBox_12,self.checkBox_13,self.checkBox_14,self.checkBox_15]
		pos = 0
		colors = ['#00ffff','#008080','#ff0000','#800000','#ff00ff','#800080','#00FF00','#008000','#ffff00','#808000','#0000ff','#000080','#a0a0a4','#808080','#ffffff','#4000a0']
		self.plot=pg.PlotWidget()
		self.plot_area.addWidget(self.plot)
		labelStyle = {'color': 'rgb(200,250,200)', 'font-size': '12pt'}
		self.plot.setLabel('left','Voltage -->', units='V',**labelStyle)
		self.plot.setLabel('bottom','Time -->', units='S',**labelStyle)
		self.plot.setYRange(-.1,.1)
		self.curves=[]
		self.timeData=[]
		self.voltData=[]

		self.valueTable.setHorizontalHeaderLabels(['C'+str(a) for a in range(16)])
		for a in self.cbs:
			a.setStyleSheet('background-color:%s;'%colors[pos])
			a.setText('C'+str(pos))
			self.curves.append(pg.PlotCurveItem(pen=pg.mkPen(colors[pos], width=2),name='C'+str(pos)) )
			self.plot.addItem(self.curves[pos])
			self.timeData.append([])
			self.voltData.append([])
			item = QtGui.QTableWidgetItem()
			self.valueTable.setItem(0,pos,item)
			item.setText('')

			pos+=1
		self.startTime = time.time()
		self.timer = QTimer()
		self.timer.timeout.connect(self.update)
		self.readADC = functools.partial(self.p.get_voltage,'A1')
	

	def setADC(self, i):
		if(str(i)=='A1'): 
			self.readADC = functools.partial(self.p.get_voltage,'A1')
		if(str(i)=='A2'): #A2
			self.readADC = functools.partial(self.p.get_voltage,'A1')
		if(str(i)=='A3'): #A3
			self.readADC = functools.partial(self.p.get_voltage,'A1')
		if(str(i)=='ADS1115_UNI_0'): #ADS1115 unipolar ADS0
			self.readADC = functools.partial(self.ADC.readADC_SingleEnded,0)
		if(str(i)=='ADS1115_UNI_1'): #ADS1115 unipolar ADS1
			self.readADC = functools.partial(self.ADC.readADC_SingleEnded,1)
		if(str(i)=='ADS1115_UNI_2'): #ADS1115 unipolar ADS2
			self.readADC = functools.partial(self.ADC.readADC_SingleEnded,2)
		if(str(i)=='ADS1115_UNI_3'): #ADS1115 unipolar ADS3
			self.readADC = functools.partial(self.ADC.readADC_SingleEnded,3)
		if(str(i)=='ADS1115_DIFF_01'): #ADS1115 bipolar ADS0 - ADS1
			self.readADC = functools.partial(self.ADC.readADC_Differential,'01')
		if(str(i)=='ADS1115_DIFF_23'): #ADS1115 bipolar ADS2 - ADS3
			self.readADC = functools.partial(self.ADC.readADC_Differential,'23')
		

	def update(self):
		if self.running == False:
			return		
		try:
			for pos in range(16):
				if self.cbs[pos].isChecked():
					if(pos!=self.MULTIPLEXER_POSITION):
						self.MULTIPLEXER_POSITION = pos
						self.p.set_multiplexer(pos) #Select the input.
						time.sleep( float(self.settlingBox.value())*0.001 )
					#v = self.p.get_voltage('A3')
					v = self.readADC()
					self.valueTable.item(0,pos).setText('%.3f'%v)

					self.timeData[pos].append(time.time()-self.startTime)
					self.voltData[pos].append(v)
					if len(self.timeData) > 1:
						self.curves[pos].setData(self.timeData[pos], self.voltData[pos])
				else:
					self.valueTable.item(0,pos).setText('')
		except:
			self.comerr()
			
		dt = time.time() - self.startTime

		self.progressBar.setProperty("value", int(100*dt/self.TMAX))

		if dt > self.TMAX:
			self.running = False
			self.msg(self.tr('Data logger plot completed'))
			return


	def updateHandler(self,device):
		if(device.connected):
			self.p = device

	def startLogging(self):
		self.clearTraces()
		self.running = True
		self.TMAX = float(self.durationBox.value())
		self.plot.setXRange(0,self.TMAX)
		self.startTime = time.time()
		self.timer.stop()
		self.timer.start(self.TIMER)
		self.msg(self.tr('Started'))

	def stopLogging(self):
		self.msg(self.tr('User Stopped'))
		self.running = False
		self.timer.stop()

	def clearTraces(self):
		self.msg(self.tr('Cleared Traces and Data'))
		self.timeData=[]
		self.voltData=[]
		for pos in range(16):
			self.curves[pos].setData([],[])
			self.timeData.append([])
			self.voltData.append([])

	def msg(self, m):
		self.msgwin.setText(self.tr(m))
	def saveTraces(self):
		#if self.running == True:
		#	self.msg(self.tr('Measurement in progress'))
		#	return
		import numpy as np
		datasizes = np.zeros(16, np.int32)
		for a in range(16): #Calculate the largest array size.
			datasizes[a] = len(self.timeData[a])
		
		if datasizes.max()==0:
			self.msg(self.tr('No data to save'))
			return
		fn = QFileDialog.getSaveFileName()
		if(len(fn)==2): #Tuple
			fn = fn[0]
		print(fn)
		if fn != '':
			f = open(fn,'wt')
			f.write(','.join(['t%d,C%d'%(a,a) for a in range(16)])+'\n')
			for a in range(datasizes.max()):
				for pos in range(16):
					if a < datasizes[pos]: #Data exists here
						f.write('%.3f,%f,'%(self.timeData[pos][a],self.voltData[pos][a]))
					else: #Data does not exist here
						f.write(',,')
				f.write('\n')
			f.close()
			self.msg(self.tr('Traces saved to ') + fn)






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
