import sys, time, utils, math, os.path

if utils.PQT5 == True:
	from PyQt5.QtCore import Qt, QTimer, QTranslator, QLocale, QLibraryInfo
	from PyQt5.QtWidgets import QApplication,QWidget, QLabel, QHBoxLayout, QVBoxLayout,\
	QCheckBox, QPushButton , QMenu
	from PyQt5.QtGui import QPalette, QColor
else:
	from PyQt4.QtCore import Qt, QTimer, QTranslator, QLocale, QLibraryInfo
	from PyQt4.QtGui import QPalette, QColor, QApplication, QWidget,\
	QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QCheckBox, QMenu
	
import pyqtgraph as pg
import numpy as np
import eyes17.eyemath17 as em


class Expt(QWidget):
	TIMER = 5
	RPWIDTH = 300
	RPGAP = 4
	NP = 500
	TG = 400
	running = False
	
	VMIN = -4
	VMAX = 4
	TMIN = 0
	TMAX = 200
	data = [ [], [] ]
	baseTrace = None
	trial = 0
	traces = []
	history = []		# Data store	
	sources = ['A1','A2','A3', 'MIC']
	pencol = 2
	Ranges12 = ['16 V', '8 V','4 V', '2.5 V', '1 V', '.5V']	# Voltage ranges for A1 and A2
	RangeVals12 = [16., 8., 4., 2.5, 1., 0.5]
	rangeVal   = 4			# selected value of range
	rangeText = '4 V'
	
	def __init__(self, device=None):
		QWidget.__init__(self)
		self.p = device										# connection to the device hardware 
		try:
			self.p.select_range('A1',4.0)
		except:
			pass		

		self.pwin = pg.PlotWidget()							# pyqtgraph window
		self.pwin.showGrid(x=True, y=True)					# with grid
		ax = self.pwin.getAxis('bottom')
		ax.setLabel(self.tr('Time (mS)'))	
		ax = self.pwin.getAxis('left')
		ax.setLabel(self.tr('Voltage (V)'))
		self.pwin.disableAutoRange()
		self.pwin.setXRange(self.TMIN, self.TMAX)
		self.pwin.setYRange(self.VMIN, self.VMAX)
		self.pwin.hideButtons()								# Do not show the 'A' button of pg
		self.baseTrace = self.pwin.plot([0,0],[0,0], pen = 'w')

		right = QVBoxLayout()							# right side vertical layout
		right.setAlignment(Qt.AlignTop)
		right.setSpacing(self.RPGAP)

		H = QHBoxLayout()
		H.setAlignment(Qt.AlignLeft)
		l = QLabel(text=self.tr('Select Range of A1'))
		l.setMaximumWidth(150)
		H.addWidget(l)
		self.rangeSelPB = QPushButton(self.tr('4 V'))
		self.rangeSelPB.setMaximumWidth(60)
		menu = QMenu()
		for k in range(len(self.Ranges12)):
			menu.addAction(self.Ranges12[k], lambda index=k: self.select_range(index))
		self.rangeSelPB.setMenu(menu)
		H.addWidget(self.rangeSelPB)
		right.addLayout(H)

		b = QPushButton(self.tr("Start Scanning"))
		right.addWidget(b)
		b.clicked.connect(self.start_scan)		
				
		b = QPushButton(self.tr("Clear Traces"))
		right.addWidget(b)
		b.clicked.connect(self.clear)		

		H = QHBoxLayout()
		self.SaveButton = QPushButton(self.tr("Save Data to"))
		self.SaveButton.setMaximumWidth(90)
		self.SaveButton.clicked.connect(self.save_data)		
		H.addWidget(self.SaveButton)
		self.Filename = utils.lineEdit(150, self.tr('induction.txt'), 20, None)
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
		
	def select_range(self, index):
		self.rangeText = self.Ranges12[index]
		self.rangeVal = self.RangeVals12[index]
		try:
			self.p.select_range('A1', self.RangeVals12[index])
		except:
			self.comerr()
			return		
		self.rangeSelPB.setText(self.rangeText)
		self.VMAX = self.RangeVals12[index]
		self.VMIN = -self.VMAX
		self.pwin.setYRange(self.VMIN, self.VMAX)
	
	def start_scan(self):
		self.pwin.setXRange(self.TMIN, self.TMAX)
		self.pwin.setYRange(self.VMIN, self.VMAX)
		try:
			t, v = self.p.capture1('A1',self.NP, self.TG)
		except:
			self.comerr()
			return 
		
		self.noise = abs(np.max(v)-np.min(v))
		self.running = True
		data = [ [], [] ]
		self.msg('Noise = %5.3f V. Drop the Magnet until a trace is captured'%self.noise)
		self.baseTrace.setData(t,v)
		self.pencol += 2
	
	def update(self):
		if self.running == False:
			return
		try:
			t,v = self.p.capture1('A1', self.NP, self.TG)		
		except:
			self.comerr()
			return 
		tmin = np.argmin(v) 
		tmax = np.argmax(v) 
		span = abs(v[tmax] - v[tmin])
		self.msg('Induced voltage %5.3f V'%span)
		if abs(span - self.noise) > 0.5 and tmin > 0.1 * self.NP and tmax < 0.9 * self.NP: 
			self.msg('Detected voltage above threshold. Peak voltages %5.3f and %5.3f'%(v[tmin], v[tmax]))
			self.traces.append(self.pwin.plot(t,v, pen = self.trial*2))
			self.history.append((t,v))
			self.trial += 1
			self.running = False
			
	def clear(self):
		self.baseTrace.setData([0,0],[0,0])
		for k in self.traces: self.pwin.removeItem(k)
		self.history = []
		self.trial = 0
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
	
