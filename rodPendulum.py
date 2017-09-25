import sys, time, utils, math

if utils.PQT5 == True:
	from PyQt5.QtCore import Qt, QTimer
	from PyQt5.QtWidgets import QApplication,QWidget, QLabel, QHBoxLayout, QVBoxLayout,\
	QCheckBox, QPushButton, QTextEdit
	from PyQt5.QtGui import QPalette, QColor
else:
	from PyQt4.QtCore import Qt, QTimer
	from PyQt4.QtGui import QPalette, QColor, QApplication, QWidget,\
	QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QCheckBox, QTextEdit
	
import pyqtgraph as pg
import numpy as np
import eyes17.eyemath17 as em


class Expt(QWidget):
	TIMER = 5
	RPWIDTH = 300
	RPGAP = 4
	running = False
	
	NMIN = 0
	NMAX = 10
	TMIN = 0
	TMAX = 2000		# milliseconds
	data = [ [], [] ]
	currentTrace = None
	traces = []
	history = []		# Data store	
	sources = ['A1','A2','A3', 'MIC']
	pencol = 2
	res = ''
	
	def __init__(self, device=None):
		QWidget.__init__(self)
		self.p = device										# connection to the device hardware 
		
		self.pwin = pg.PlotWidget()							# pyqtgraph window
		self.pwin.showGrid(x=True, y=True)					# with grid
		ax = self.pwin.getAxis('bottom')
		ax.setLabel('Trials')	
		ax = self.pwin.getAxis('left')
		ax.setLabel('Time Period (mSec)')
		self.pwin.disableAutoRange()
		self.pwin.setXRange(self.NMIN, self.NMAX)
		self.pwin.setYRange(self.TMIN, self.TMAX)
		self.pwin.hideButtons()								# Do not show the 'A' button of pg

		right = QVBoxLayout()							# right side vertical layout
		right.setAlignment(Qt.AlignTop)
		right.setSpacing(self.RPGAP)
					
		H = QHBoxLayout()
		l = QLabel(text=self.tr('Number of trials'))
		l.setMaximumWidth(110)
		H.addWidget(l)
		self.NMAXtext = utils.lineEdit(40, self.NMAX, 6, None)
		H.addWidget(self.NMAXtext)
		right.addLayout(H)

		b = QPushButton(self.tr("Start"))
		right.addWidget(b)
		b.clicked.connect(self.start)		
		
		b = QPushButton(self.tr("Stop"))
		right.addWidget(b)
		b.clicked.connect(self.stop)		

		'''
		b = QPushButton(self.tr("Analyze last Trace"))
		right.addWidget(b)
		b.clicked.connect(self.fit_curve)		
		'''

		b = QPushButton(self.tr("Clear Data and Traces"))
		right.addWidget(b)
		b.clicked.connect(self.clear)		

		H = QHBoxLayout()
		self.SaveButton = QPushButton(self.tr("Save to"))
		self.SaveButton.setMaximumWidth(90)
		self.SaveButton.clicked.connect(self.save_data)		
		H.addWidget(self.SaveButton)
		self.Filename = utils.lineEdit(150, 'rod-pendulum.txt', 20, None)
		H.addWidget(self.Filename)
		right.addLayout(H)
					
		H = QHBoxLayout()
		self.Results = QTextEdit()	
		self.Results.setMaximumWidth(self.RPWIDTH-10)
		H.addWidget(self.Results)
		right.addLayout(H)
	
					


		#------------------------end of right panel ----------------
		
		top = QHBoxLayout()
		top.addWidget(self.pwin)
		top.addLayout(right)
		
		full = QVBoxLayout()
		full.addLayout(top)
		self.msgwin = QLabel(text=self.tr(''))
		full.addWidget(self.msgwin)
				
		self.setLayout(full)
		
		self.timer = QTimer()
		self.timer.timeout.connect(self.update)
		self.timer.start(self.TIMER)
		

		#----------------------------- end of init ---------------
	
	def fit_curve(self):
		if self.running == True or self.data[0]==[]:
			return
		return
		# Make histogram to be added

		if (len(self.data[0])%2) == 1:			# make it an even size, for fitting
			self.data[0] = self.data[0][:-1]
			self.data[1] = self.data[1][:-1]
			
		fa = em.fit_dsine(self.data[0], self.data[1])
		if fa != None:
			pa = fa[1]
			self.traces.append(self.pwin.plot(self.data[0], fa[0], pen = 'w'))
			self.msg('Frequency of Oscillation = %5.2f Hz. Damping Factor = %5.3f'%(pa[1], pa[4]))
		else:
			self.msg('Analysis failed. Could not fit data')

				
	def update(self):
		if self.running == False:
			return
		if self.p == None:
			self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		
			return
		try:
			T = self.p.multi_r2rtime('SEN', 1)
		except:
			self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		
		
		if T < 0:
			#self.msg('<font color="red">Timeout Error')
			s = 'Timeout\n'
		else:
			s ='T = %f\n'%T
		self.res += s 
		self.Results.setText(self.res)

		T *= 1000			#seconds  to milliseconds
		self.data[0].append(self.index)
		self.data[1].append(T)
		if self.index > self.NMAX:
			self.running = False
			self.history.append(self.data)
			self.traces.append(self.currentTrace)
			self.msg('Period of pendulum measured for %5.0f times'%self.NMAX)
			return
		if self.index > 1:			  # Draw the line
			self.currentTrace.setData(self.data[0], self.data[1])
		self.index += 1


	def start(self):
		if self.p == None:
			self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		
			return
		
		if self.running == True: return
		try:
			val = float(self.NMAXtext.text())
		except:
			self.msg('Invalid Number')
			return
		self.NMAX = val
		try:
			self.p.set_sqr1(0)						# Light the LED
		except:
			self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		
		
		self.pwin.setXRange(self.NMIN, self.NMAX)
		self.pwin.setYRange(self.TMIN, self.TMAX)
		self.running = True
		self.data = [ [], [] ]
		self.currentTrace = self.pwin.plot([0,0],[0,0], pen = self.pencol)
		self.index = 0
		self.pencol += 2
		self.p.set_sqr1(0)
		self.msg('Started Measurements')

	def stop(self):
		if self.running == False: return
		self.running = False
		self.history.append(self.data)
		self.traces.append(self.currentTrace)
		try:
			self.p.set_sqr1(-1)						# trurn off the LED
			self.msg('User Stopped')
		except:
			self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		

	def clear(self):
		for k in self.traces:
			self.pwin.removeItem(k)
		self.history = []
		self.pencol = 2
		self.Results.setText('')
		self.msg('Cleared Traces and Data')
		
	def save_data(self):
		if self.history == []:
			self.msg('No Traces available for saving')
			return
		fn = self.Filename.text()
		self.p.save(self.history, fn)
		self.msg('Traces saved to %s'%fn)
		
	def msg(self, m):
		self.msgwin.setText(self.tr(m))
		

if __name__ == '__main__':
	import eyes17.eyes
	dev = eyes17.eyes.open()
	app = QApplication(sys.argv)
	mw = Expt(dev)
	mw.show()
	sys.exit(app.exec_())
	
