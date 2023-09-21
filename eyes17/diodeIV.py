import sys, time, math, os.path
import utils

from QtVersion import *

import pyqtgraph as pg
import numpy as np
import eyes17.eyemath17 as em


class Expt(QWidget):
	TIMER = 50
	RPWIDTH = 300
	RPGAP = 4
	running = False
	
	VMIN = 0
	VMAX = 5
	VSET = VMIN
	IMIN = 0
	IMAX = 5
	STEP = 0.050	   # 50 mV
	data = [ [], [] ]
	currentTrace = None
	traces = []
	history = []		# Data store	
	sources = ['A1','A2','A3', 'MIC']
	trial = 0
	
	def __init__(self, device=None):
		QWidget.__init__(self)
		self.p = device										# connection to the device hardware 
		self.traceCols = utils.makeTraceColors()
		
		self.pwin = pg.PlotWidget()							# pyqtgraph window
		self.pwin.showGrid(x=True, y=True)					# with grid
		ax = self.pwin.getAxis('bottom')
		ax.setLabel(self.tr('Voltage (V)'))	
		ax = self.pwin.getAxis('left')
		ax.setLabel(self.tr('Current (mA)'))
		self.pwin.disableAutoRange()
		self.pwin.setXRange(self.VMIN, self.VMAX)
		self.pwin.setYRange(self.IMIN, self.IMAX)
		self.pwin.hideButtons()								# Do not show the 'A' button of pg


		self.region = pg.LinearRegionItem()
		self.region.setBrush([255,0,50,50])
		self.region.setZValue(10)
		for a in self.region.lines: a.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor)); 
		self.pwin.addItem(self.region, ignoreBounds=False)
		self.region.setRegion([0.2,3])


		right = QVBoxLayout()							# right side vertical layout
		right.setAlignment(Qt.AlignmentFlag(0x0020)) #Qt.AlignTop
		right.setSpacing(self.RPGAP)
					
		self.zener = QCheckBox(self.tr('Zener Diode'))
		right.addWidget(self.zener)
		 
		b = QPushButton(self.tr("Start"))
		right.addWidget(b)
		b.clicked.connect(self.start)		
		
		b = QPushButton(self.tr("Stop"))
		right.addWidget(b)
		b.clicked.connect(self.stop)		
		
		b = QPushButton(self.tr("FIT with I=Io* exp(qV/nkT)"))
		right.addWidget(b)
		b.clicked.connect(self.fit_curve)		


		b = QPushButton(self.tr("FIT with I=V/R"))
		right.addWidget(b)
		b.clicked.connect(self.fit_curve_resistance)		

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
		
	
	def fit_curve(self):
		if self.running == True or self.data[0]==[]:
			return

		S,E=self.region.getRegion()
		start = (np.abs(np.array(self.data[0]) - S)).argmin()
		end = (np.abs(np.array(self.data[0]) - E)).argmin()

		f = em.fit_exp(self.data[0][start:end], self.data[1][start:end])
		if f != None:
			self.traces.append(self.pwin.plot(self.data[0][start:end], f[0], pen = self.traceCols[self.trial%5]))
			self.trial += 1
			k = 1.38e-23    # Boltzmann const
			q = 1.6e-19     # unit charge
			Io = f[1][0]
			a1 = f[1][1]
			T = 300.0		# Room temp in Kelvin
			n = q/(a1*k*T)
			ss1 = '%5.2e'%Io
			ss2 = '%5.2f'%n
			self.msg(self.tr('Fitted with Diode Equation : Io = ') +ss1 + self.tr(' mA , Ideality factor = ') + ss2)
			self.history.append((self.data[0][start:end], f[0]))			
		else:
			self.msg(self.tr('Analysis failed. Could not fit data'))

	def fit_curve_resistance(self): #fit_line
		if self.running == True or self.data[0]==[]:
			return

		S,E=self.region.getRegion()
		start = (np.abs(np.array(self.data[0]) - S)).argmin()
		end = (np.abs(np.array(self.data[0]) - E)).argmin()

		f = em.fit_line(self.data[0][start:end], self.data[1][start:end])
		if f != None:
			self.traces.append(self.pwin.plot(self.data[0][start:end], f[0], pen = self.traceCols[self.trial%5]))
			self.trial += 1
			self.msg(self.tr('Fitted with Straight Line : Slope = ') +'%.2e, '%(f[1][0])+ self.tr('offset = ')+ '%.2e'%(f[1][1]))
			self.history.append((self.data[0][start:end], f[0]))			
		else:
			self.msg(self.tr('Analysis failed. Could not fit data'))
				
	def update(self):
		if self.running == False:
			return
		try:
			vs = self.p.set_pv1(self.VSET)	
			time.sleep(0.001)	
			va = self.p.get_voltage('A1')		# voltage across the diode
		except:
			self.comerr()
			return 
		
		i = (vs-va)/1.0 	 		   # in mA, R= 1k
		self.data[0].append(va)
		self.data[1].append(i)
		self.VSET += self.STEP
		if self.VSET > self.VMAX:
			self.running = False
			self.history.append(self.data)
			self.traces.append(self.currentTrace)
			self.msg(self.tr('Completed plotting I-V'))
			return
		if self.index > 1:			  # Draw the line
			self.currentTrace.setData(self.data[0], self.data[1])
		self.index += 1

	def start(self):
		if self.running == True: return
		if self.zener.isChecked() == True:
			self.VMIN = -5
			self.IMIN = -5
		else:
			self.VMIN = 0
			self.IMIN = 0
			
		self.pwin.setXRange(self.VMIN, self.VMAX)
		self.pwin.setYRange(self.IMIN, self.IMAX)
		try:
			self.p.select_range('A1',4)
		except:
			self.comerr()
			return 

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
	
