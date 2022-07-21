import sys, time, math, os.path
import utils

from QtVersion import *

import pyqtgraph as pg
import numpy as np
import eyes17.eyemath17 as em

from eyes17.SENSORS import MPU6050
from eyes17.SENSORS.supported import supported,nameMap
from eyes17.sensorlist import sensors as sensorHints


class Expt(QWidget):
	TIMER = 10
	RPWIDTH = 300
	RPGAP = 4
	running = False
	sensor = None
	
	VMIN = -5
	VMAX = 5
	TMIN = 0
	TMAX = 5
	TGAP = 10
	MAXCHAN = 7
	dataVals =  [[] for x in range(MAXCHAN)]
	timeVal = []
	
	sensorNames = [
	        QT_TRANSLATE_NOOP('Expt','Ax'),
	        QT_TRANSLATE_NOOP('Expt','Ay'),
	        QT_TRANSLATE_NOOP('Expt','Az'),
	        QT_TRANSLATE_NOOP('Expt','Temperature'),
	        QT_TRANSLATE_NOOP('Expt','Vx'),
	        QT_TRANSLATE_NOOP('Expt','Vy'),
	        QT_TRANSLATE_NOOP('Expt','Vz')
	]
	sensorSelectCB = [None]*MAXCHAN
	sensorFlags = [False]*MAXCHAN
	dataTraces = [None]*MAXCHAN
	history = []		# Data store	
	chanpens = ['y','g','r','m', 'c','w','b']     #pqtgraph pen colors
	
	def __init__(self, device=None):
		QWidget.__init__(self)
		self.p = device										# connection to the device hardware 
		
		self.pwin = pg.PlotWidget()							# pyqtgraph window
		self.pwin.showGrid(x=True, y=True)					# with grid
		ax = self.pwin.getAxis('bottom')
		ax.setLabel(self.tr('Time (mS)'))	
		ax = self.pwin.getAxis('left')
		ax.setLabel(self.tr('Value'))
		#self.pwin.disableAutoRange()
		self.pwin.setXRange(self.TMIN, self.TMAX)
		#self.pwin.setYRange(self.VMIN, self.VMAX)
		#self.pwin.hideButtons()								# Do not show the 'A' button of pg

		right = QVBoxLayout()							# right side vertical layout
		right.setAlignment(Qt.AlignmentFlag(0x0020)) #Qt.AlignTop
		right.setSpacing(self.RPGAP)

		for k in range(self.MAXCHAN):
			self.dataTraces[k] = self.pwin.plot([0,0],[0,0], pen = self.chanpens[k])
			self.sensorSelectCB[k] = QCheckBox(self.tr(self.sensorNames[k]))
			right.addWidget(self.sensorSelectCB[k])
		self.sensorSelectCB[3].setChecked(True)		# Temperature is enabled by default
					
		H = QHBoxLayout()
		l = QLabel(text=self.tr('Duration'))
		l.setMaximumWidth(80)
		H.addWidget(l)
		self.TMAXtext = utils.lineEdit(40, self.TMAX, 6, None)
		H.addWidget(self.TMAXtext)
		l = QLabel(text=self.tr('Seconds'))
		l.setMaximumWidth(60)
		H.addWidget(l)
		right.addLayout(H)

		H = QHBoxLayout()
		l = QLabel(text=self.tr('Read every'))
		l.setMaximumWidth(80)
		H.addWidget(l)
		self.TGAPtext = utils.lineEdit(40, self.TGAP, 6, None)
		H.addWidget(self.TGAPtext)
		l = QLabel(text=self.tr('mS'))
		l.setMaximumWidth(60)
		H.addWidget(l)
		right.addLayout(H)

		b = QPushButton(self.tr("Start"))
		right.addWidget(b)
		b.clicked.connect(self.start)		
		
		b = QPushButton(self.tr("Stop"))
		right.addWidget(b)
		b.clicked.connect(self.stop)				
		
		b = QPushButton(self.tr("Clear Traces"))
		right.addWidget(b)
		b.clicked.connect(self.clear)		

		self.SaveButton = QPushButton(self.tr("Save Data"))
		self.SaveButton.clicked.connect(self.save_data)		
		right.addWidget(self.SaveButton)


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

				
	def update(self):
		if self.running == False:
			return
						
		try:	
			senData = self.sensor.getRaw()
		except:
			self.msg(self.tr('I2C device communication error'))
			return 
		
		#print senData
		
		if self.timeVal == []:
			self.start_time = time.time()
			elapsed = 0
		else:
			elapsed = time.time() - self.start_time

		self.timeVal.append(elapsed)
		for k in range(self.MAXCHAN):
			if self.sensorFlags[k] == True:
				self.dataVals[k].append(senData[k])

		if elapsed > self.TMAX:
			self.running = False
			self.msg(self.tr('MPU6050 data plot completed'))
			return

		if len(self.timeVal) > 1:			  # Draw the traces
			for k in range(self.MAXCHAN):
				if self.sensorFlags[k] == True:
					self.dataTraces[k].setData(self.timeVal, self.dataVals[k])


	def start(self):
		if self.running == True: return
		try:
			self.TMAX = float(self.TMAXtext.text())
			self.TGAP = float(self.TGAPtext.text())
		except:
			self.msg(self.tr('Invalid Duration or Time between reads (> 10 mSec)'))
			return
			
		self.timer.stop()
		self.timer.start(self.TGAP)
			
		lst =  self.p.I2C.scan()
		for a in lst:
			sen = sensorHints.get(a,['unknown'])[0]
			if 'MPU-6050' in sen:
				self.sensor = supported[a].connect(self.p.I2C,address = a)
				break			

		for k in range(self.MAXCHAN):
			self.dataVals[k] = []	       # Clear data and traces
			self.dataTraces[k].setData([0,0],[0,0])
			if self.sensorSelectCB[k].isChecked() == True:
				self.sensorFlags[k] = True
			else:
				self.sensorFlags[k] = False
		self.timeVal = []
		
		self.pwin.setXRange(self.TMIN, self.TMAX)
		#self.pwin.setYRange(self.VMIN, self.VMAX)
		self.running = True
		self.msg(self.tr('Started Measurements'))
		


	def stop(self):
		self.running = False
		self.msg(self.tr('User Stopped'))

	def clear(self):
		self.timeVal = []
		for k in range(self.MAXCHAN):
			self.dataVals[k] = []	       # Clear data and traces
			self.dataTraces[k].setData([0,0],[0,0])
		self.msg(self.tr('Cleared Traces and Data'))
		
	def save_data(self):
		if self.timeVal == []:
			self.msg(self.tr('No Traces available for saving'))
			return
		fn = QFileDialog.getSaveFileName()
		if fn != '':
			data = []
			for k in range(self.MAXCHAN):
				if self.sensorFlags[k] == True:
					data.append([self.timeVal, self.dataVals[k]])
			self.p.save(data, fn)
			self.msg(self.tr('Traces saved to ') + fn)
		
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
	
