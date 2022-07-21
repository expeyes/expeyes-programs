# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
import sys, time, math, os.path
import utils

from QtVersion import *

import pyqtgraph as pg
import numpy as np
import eyes17.eyemath17 as em


class Expt(QWidget):
	RPWIDTH = 300
	RPGAP = 4
	
	VMIN = 0
	VMAX = 5
	TG = 100
	sources = ['A1','A2','A3', 'MIC']
	chanpens = ['y','g','w','m']     #pqtgraph pen colors

	total_duration=0
	low_duration=0

	def __init__(self, device=None):
		QWidget.__init__(self)
		self.p = device										# connection to the device hardware 
		try:
			self.p.select_range('A1',4.0)
		except:
			pass		
		self.traceCols = utils.makeTraceColors()
			
		self.pwin = pg.PlotWidget()							# pyqtgraph window
		self.pwin.showGrid(x=True, y=True)					# with grid
		self.plot = self.pwin.plot([0,0],[0,0], pen = self.traceCols[-1])
		ax = self.pwin.getAxis('bottom')
		ax.setLabel(self.tr('Time (S)'))	
		ax = self.pwin.getAxis('left')
		ax.setLabel(self.tr('Voltage'))
		self.pwin.disableAutoRange()
		self.pwin.setYRange(-1, 5)
		self.pwin.setXRange(0, 1e-6*10000*self.TG)
		#self.pwin.hideButtons()								# Do not show the 'A' button of pg

		right = QVBoxLayout()							# right side vertical layout
		right.setAlignment(Qt.AlignmentFlag(0x0020)) #Qt.AlignTop
		right.setSpacing(self.RPGAP)
					
		self.ratioLabel = QLabel(self.tr("Ratio ="))
		right.addWidget(self.ratioLabel)
		self.occupancyNowLabel = QLabel(self.tr("Occupancy ="))
		right.addWidget(self.occupancyNowLabel)
		self.occupancyLabel = QLabel(self.tr("Average Occupancy ="))
		right.addWidget(self.occupancyLabel)
		self.occupancyLabelC = QLabel(self.tr("Concentration ="))
		right.addWidget(self.occupancyLabelC)

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

		self.p.capture_traces(1,10000,self.TG,'A1')
		self.timer.singleShot(1e-3*10000*self.TG+200,self.update) #uS to mS

	def r2c(self,r):
		return 10000*(r)/19

	def update(self):
		try:
			while 1:
				x = self.p.oscilloscope_progress()
				time.sleep(0.01)
				if x[0]:break
				print('waiting...')
					
			#print('fetched.')
			self.p.__fetch_channel__(1)
			self.p.capture_traces(1,10000,self.TG,'A1')
			self.timer.singleShot(1e-3*10000*self.TG+100,self.update) #uS to mS
			#print('acquire ...')
		except Exception as e:
			print(e)
			self.p.capture_traces(1,10000,self.TG,'A1')
			self.timer.singleShot(1e-3*10000*self.TG+200,self.update) #uS to mS
			print('failed. comerr')
			return 

		x=self.p.achans[0].get_xaxis()
		y=self.p.achans[0].get_yaxis()
		self.plot.setData(x*1e-6,y)

		self.total_duration += 10000
		self.low_duration += len(y[y<2.5])

		ratio = len(y[y<2.5])*100 / (10000)
		C_Now = self.r2c(ratio)
		#C_Now = 1.1 * pow( ratio, 3) - 3.8 *pow(ratio, 2) + 520 * ratio + 0.62; #using spec sheet curve
		ratio = self.low_duration*100 / (self.total_duration)
		C_Avg = self.r2c(ratio)
		C_AvgF = 1.1 * pow( ratio, 3) - 3.8 *pow(ratio, 2) + 520 * ratio + 0.62; #using spec sheet curve
		self.ratioLabel.setText("Ratio: %.2f%%"%(ratio))
		self.occupancyNowLabel.setText("Occupancy:%.2f"%C_Now)
		self.occupancyLabel.setText("Average Occupancy:%.2f"%C_Avg)
		self.occupancyLabelC.setText("Concentration:%.2f"%C_AvgF)
		
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
	
