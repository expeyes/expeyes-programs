import sys, time, math, os.path
import utils

from QtVersion import *

import pyqtgraph as pg
import numpy as np
import eyes17.eyemath17 as em
from eyes17.SENSORS import MPU925x

class Expt(QWidget):
	TIMER = 80
	RPWIDTH = 300
	RPGAP = 4
	running = False
	
	VMIN = -3
	VMAX = 3
	VSET = VMIN
	ZMIN = -3000
	ZMAX = 3000
	STEP = 0.050	   # 50 mV
	data = [ [], [] ]
	currentTrace = None
	traces = []
	history = []		# Data store	
	sources = ['A1','A2','A3', 'MIC']
	trial = 0
	zero = 0.
	
	def __init__(self, device=None):
		QWidget.__init__(self)
		self.p = device		# connection to the device hardware 
		self.p.set_pv1(0)
		self.traceCols = utils.makeTraceColors()
		
		self.pwin = pg.PlotWidget() #pyqtgraph window
		self.pwin.showGrid(x=True, y=True)					# with grid
		ax = self.pwin.getAxis('bottom')
		ax.setLabel(self.tr('Voltage (V) -> Current -> Magnetic Field(B)'))	
		ax = self.pwin.getAxis('left')
		ax.setLabel(self.tr('Magnetic Field (H)'))
		self.pwin.disableAutoRange()
		self.pwin.setXRange(self.VMIN, self.VMAX)
		self.pwin.setYRange(self.ZMIN, self.ZMAX)
		self.pwin.hideButtons()								# Do not show the 'A' button of pg

		right = QVBoxLayout()							# right side vertical layout
		right.setAlignment(Qt.AlignmentFlag(0x0020)) #Qt.AlignTop
		right.setSpacing(self.RPGAP)


		 
		b = QPushButton(self.tr("Start"))
		right.addWidget(b)
		b.clicked.connect(self.start)		
		
		b = QPushButton(self.tr("Stop"))
		right.addWidget(b)
		b.clicked.connect(self.stop)		

		b = QPushButton(self.tr("Set Zero"))
		right.addWidget(b)
		b.clicked.connect(self.zero)		
		
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
		
		self.t = MPU925x.connect(self.p.I2C)
		self.t.initMagnetometer()
		self.zero =0
		if MPU925x.MPU925x.ADDRESS not in self.p.I2C.scan():
			self.msg(self.tr('MPU925x Sensor Not Found'))

		#----------------------------- end of init ---------------
			
	def update(self):
		if self.running == False:
			return
		try:
			vs = self.p.set_pv1(self.VSET)	
			time.sleep(0.05)	
			X,Y,Z = self.t.getMag()		# voltage across the diode
			Z -= self.zero
		except Exception as e:
			print(e)
			self.comerr()
			return 
		
		self.data[0].append(vs)
		self.data[1].append(Z)
		self.VSET += self.STEP
		if self.VSET > self.VMAX:
			self.STEP*=-1
		
		if self.VSET < self.VMIN:
			self.running = False
			self.history.append(self.data)
			self.traces.append(self.currentTrace)
			self.msg(self.tr('Completed plotting B-H'))
			self.p.set_pv1(0)
			return
		if self.index > 1:			  # Draw the line
			self.currentTrace.setData(self.data[0], self.data[1])
		self.index += 1

	def zero(self):
		X,Y,Z = self.t.getMag()
		self.zero = Z
		self.msg(self.tr('Residual Magnetic Field: %.2f'%Z))

	def start(self):
		if self.running == True: return
		self.VSET = self.VMIN
		self.p.set_pv1(self.VSET)
		time.sleep(0.5)
		self.STEP = 0.05	   # 50 mV

			
		self.pwin.setXRange(self.VMIN, self.VMAX)
		self.pwin.setYRange(self.ZMIN, self.ZMAX)

		self.running = True
		self.data = [ [], [] ]
		self.VSET = self.VMIN
		self.currentTrace = self.pwin.plot([0,0],[0,0], pen = self.traceCols[self.trial%5])
		self.index = 0
		self.trial += 1
		self.msg(self.tr('Started'))

	def stop(self):
		if self.running == False: return
		self.running = False
		self.history.append(self.data)
		self.traces.append(self.currentTrace)
		self.msg(self.tr('User Stopped'))

	def clear(self):
		for k in self.traces:
			self.pwin.removeItem(k)
		self.history = []
		self.data = [ [], [] ]
		self.trial = 0
		self.msg(self.tr('Cleared Traces and Data'))
		
	def save_data(self):
		if self.history == []:
			self.msg(self.tr('No data to save'))
			return
		fn = QFileDialog.getSaveFileName()
		if fn != '':
			self.p.save(self.history, fn)
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
	
