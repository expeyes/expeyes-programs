'''
Code for science experiments using expEYES-17 interface
Author  : Ajith Kumar B.P, bpajith@gmail.com
Date    : Aug-2017
License : GNU GPL version 3
'''

import sys, time, utils, math, os.path

if utils.PQT5 == True:
	from PyQt5.QtCore import Qt, QTimer, \
                QTranslator, QLocale, QLibraryInfo
	from PyQt5.QtWidgets import QApplication,QWidget, QLabel, QHBoxLayout, QVBoxLayout,\
	QCheckBox, QPushButton 
	from PyQt5.QtGui import QPalette, QColor
else:
	from PyQt4.QtCore import Qt, QTimer, \
                QTranslator, QLocale, QLibraryInfo
	from PyQt4.QtGui import QPalette, QColor, QApplication, QWidget,\
	QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QCheckBox

import pyqtgraph as pg
import numpy as np
import eyes17.eyemath17 as em


class Expt(QWidget):
	TIMER = 5
	RPWIDTH = 300
	RPGAP = 4
	running = False
	
	TPMIN = 0
	TPMAX = 100
	TMIN = 0
	TMAX = 10
	TGAP = 1.0
	Gain = 11.0
	CCval = 1.1
	Offset = 0.0
	data = [ [], [] ]
	currentTrace = None
	traces = []
	history = []		# Data store	
	sources = ['A1','A2','A3', 'MIC']
	pencol = 2
	
	def __init__(self, device=None):
		QWidget.__init__(self)
		self.p = device										# connection to the device hardware 
		
		try:
			self.p.set_state(CCS=1)
		except:
			pass	

		
		self.pwin = pg.PlotWidget()							# pyqtgraph window
		self.pwin.showGrid(x=True, y=True)					# with grid
		ax = self.pwin.getAxis('bottom')
		ax.setLabel(self.tr('Time (mS)'))
		ax = self.pwin.getAxis('left')
		ax.setLabel(self.tr('Temparature (C)'))
		self.pwin.disableAutoRange()
		self.pwin.setXRange(self.TMIN, self.TMAX)
		self.pwin.setYRange(self.TPMIN, self.TPMAX)
		self.pwin.hideButtons()								# Do not show the 'A' button of pg

		right = QVBoxLayout()							# right side vertical layout
		right.setAlignment(Qt.AlignTop)
		right.setSpacing(self.RPGAP)

		H = QHBoxLayout()
		b = QPushButton(self.tr("Measure A3"))
		b.setMaximumWidth(120)
		H.addWidget(b)
		b.clicked.connect(self.measureA3)		
		self.A3val = QLabel(text='')
		H.addWidget(self.A3val)
		right.addLayout(H)


		H = QHBoxLayout()
		l = QLabel(text=self.tr('A3 Gain'))
		l.setMaximumWidth(100)
		H.addWidget(l)
		self.GAINtext = utils.lineEdit(40, self.Gain, 6, None)
		H.addWidget(self.GAINtext)
		l = QLabel(text=self.tr('1+10k/Rg'))
		l.setMaximumWidth(60)
		H.addWidget(l)
		right.addLayout(H)

		H = QHBoxLayout()
		l = QLabel(text=self.tr('A3 Offset'))
		l.setMaximumWidth(100)
		H.addWidget(l)
		self.OFFSETtext = utils.lineEdit(40, self.Offset, 6, None)
		H.addWidget(self.OFFSETtext)
		l = QLabel(text=self.tr('mV '))
		l.setMaximumWidth(60)
		H.addWidget(l)
		right.addLayout(H)

		H = QHBoxLayout()
		l = QLabel(text=self.tr('CCS Value'))
		l.setMaximumWidth(100)
		H.addWidget(l)
		self.CCtext = utils.lineEdit(40, self.CCval, 6, None)
		H.addWidget(self.CCtext)
		l = QLabel(text=self.tr('mA'))
		l.setMaximumWidth(60)
		H.addWidget(l)
		right.addLayout(H)
		
					
		H = QHBoxLayout()
		l = QLabel(text=self.tr('Lowest Temp'))
		l.setMaximumWidth(100)
		H.addWidget(l)
		self.TPMINtext = utils.lineEdit(40, self.TPMIN, 6, None)
		H.addWidget(self.TPMINtext)
		l = QLabel(text=self.tr('deg C'))
		l.setMaximumWidth(60)
		H.addWidget(l)
		right.addLayout(H)

		H = QHBoxLayout()
		l = QLabel(text=self.tr('Highest Temp'))
		l.setMaximumWidth(100)
		H.addWidget(l)
		self.TPMAXtext = utils.lineEdit(40, self.TPMAX, 6, None)
		H.addWidget(self.TPMAXtext)
		l = QLabel(text=self.tr('deg C'))
		l.setMaximumWidth(60)
		H.addWidget(l)
		right.addLayout(H)
		
		H = QHBoxLayout()
		l = QLabel(text=self.tr('Total Duration'))
		l.setMaximumWidth(100)
		H.addWidget(l)
		self.TMAXtext = utils.lineEdit(40, self.TMAX, 6, None)
		H.addWidget(self.TMAXtext)
		l = QLabel(text=self.tr('Seconds'))
		l.setMaximumWidth(60)
		H.addWidget(l)
		right.addLayout(H)

		H = QHBoxLayout()
		l = QLabel(text=self.tr('Measure every'))
		l.setMaximumWidth(100)
		H.addWidget(l)
		self.TGAPtext = utils.lineEdit(40, self.TGAP, 6, None)
		H.addWidget(self.TGAPtext)
		l = QLabel(text=self.tr('Seconds'))
		l.setMaximumWidth(60)
		H.addWidget(l)
		right.addLayout(H)

		b = QPushButton(self.tr("Start"))
		right.addWidget(b)
		b.clicked.connect(self.start)		
		
		b = QPushButton(self.tr("Stop"))
		right.addWidget(b)
		b.clicked.connect(self.stop)		
		
		b = QPushButton(self.tr("Analyze last Trace"))
		right.addWidget(b)
		b.clicked.connect(self.fit_curve)		

		b = QPushButton(self.tr("Clear Traces"))
		right.addWidget(b)
		b.clicked.connect(self.clear)		

		H = QHBoxLayout()
		self.SaveButton = QPushButton(self.tr("Save to"))
		self.SaveButton.setMaximumWidth(90)
		self.SaveButton.clicked.connect(self.save_data)		
		H.addWidget(self.SaveButton)
		self.Filename = utils.lineEdit(150, self.tr('pt100.txt'), 20, None)
		H.addWidget(self.Filename)
		right.addLayout(H)

		#------------------------end of right panel ----------------
		
		top = QHBoxLayout()
		top.addWidget(self.pwin)
		top.addLayout(right)
		
		full = QVBoxLayout()
		full.addLayout(top)
		self.msgwin = QLabel(text='')
		full.addWidget(self.msgwin)
				
		self.setLayout(full)
		
		self.timer = QTimer()
		self.timer.timeout.connect(self.update)
		self.timer.start(self.TIMER)
		

		#----------------------------- end of init ---------------
	
	def fit_curve(self):
		if self.running == True or self.data[0]==[]:
			return

		if (len(self.data[0])%2) == 1:			# make it an even size, for fitting
			self.data[0] = self.data[0][:-1]
			self.data[1] = self.data[1][:-1]
			
		fa = em.fit_exp(self.data[0], self.data[1])   # fit exponential reduction
		if fa != None:
			pa = fa[1]
			self.traces.append(self.pwin.plot(self.data[0], fa[0], pen = 'w'))
			self.msg('Data Fitted with T = T0 * exp(-at). T0= %5.2f  a = %5.3f'%(pa[1], pa[2]))
		else:
			self.msg('Analysis failed. Could not fit data')


	def v2t(self, v):					# Convert Voltage to Temperature for PT100
		v = v - self.Offset* 0.001      # Convert Offset to volts
		vr = v/self.Gain    		    # voltage across PT100
		r = vr / (self.CCval * 1.0e-3)  # mA to Ampere
		r0 = 100.0						# PT100 parameters r0, A and B 
		A = 3.9083e-3
		B = -5.7750e-7
		c = 1 - r/r0
		b4ac = math.sqrt( A*A - 4 * B * c)
		temp = (-A + b4ac) / (2.0 * B)
		return temp

	def measureA3(self):
		try:	
			sum = 0.0
			NT = 4
			for k in range(NT):
				v = self.p.get_voltage('A3')  		# Read A3
				sum += v
			v = sum/NT
			self.A3val.setText(str(self.tr('%5.3f V')) %v)
		except:
			self.comerr()
			return 
			
	def update(self):
		if self.running == False:
			return
		try:	
			sum = 0.0
			NT = 4
			for k in range(NT):
				t,v = self.p.get_voltage_time('A3')  		# Read A3
				sum += v
			v = sum/NT
		except:
			self.comerr()
			return 

		if len(self.data[0]) == 0:
			self.start_time = t
			elapsed = 0
		else:
			elapsed = t - self.start_time

		self.data[0].append(elapsed)
		temp = self.v2t(v)
		self.data[1].append(temp)
		if elapsed > self.TMAX:
			self.running = False
			self.history.append(self.data)
			self.traces.append(self.currentTrace)
			self.msg('Time Vs Temperature plot completed')
			return
		if self.index > 1:			  # Draw the line
			self.currentTrace.setData(self.data[0], self.data[1])
		self.index += 1


	def start(self):
		if self.running == True: return
		try:
			self.TMAX = float(self.TMAXtext.text())
			self.TPMAX = float(self.TPMAXtext.text())
		except:
			self.msg('Invalid Duration')
			return
			
		try:
			self.TGAP = float(self.TGAPtext.text())
			self.TIMER = self.TGAP * 1000    # into mS
			self.timer.stop()
			self.timer.start(self.TIMER)
		except:
			self.msg('Invalid time interval between reads')
			return

		try:
			self.TPMIN = float(self.TPMINtext.text())
			self.TPMAX = float(self.TPMAXtext.text())
		except:
			self.msg('Invalid temperature limit')
			return
			
		try:
			self.Offset = float(self.OFFSETtext.text())
			self.Gain = float(self.GAINtext.text())
		except:
			self.msg('Invalid Offset or Gain')
			return

		try:
			self.CCval = float(self.CCtext.text())
		except:
			self.msg('Invalid CCS input')
			return
		
		self.pwin.setXRange(self.TMIN, self.TMAX)
		self.pwin.setYRange(self.TPMIN, self.TPMAX)
		self.running = True
		self.data = [ [], [] ]
		self.currentTrace = self.pwin.plot([0,0],[0,0], pen = self.pencol)
		self.index = 0
		self.pencol += 2
		self.msg('Started Measurements')

	def stop(self):
		if self.running == False: return
		self.running = False
		self.history.append(self.data)
		self.traces.append(self.currentTrace)
		self.msg('User Stopped')

	def clear(self):
		if self.running == True: return
		for k in self.traces:
			self.pwin.removeItem(k)
		self.history = []
		self.pencol = 2
		self.msg('Cleared Traces and Data')
		
	def save_data(self):
		if self.history == []:
			self.msg('No Traces available for saving')
			return
		fn = self.Filename.text()
		self.p.save(self.history, fn)
		self.msg('Traces saved to %s'%fn)
		
	def msg(self, m):
		self.msgwin.setText(m)
		
	def comerr(self):
		self.msgwin.setText('<font color="red">' + self.tr('Error. Try Device->Reconnect'))

if __name__ == '__main__':
	import eyes17.eyes
	dev = eyes17.eyes.open()
	
	dev.set_pv1(0.120)
	dev.set_pv2(0.120)
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
	
