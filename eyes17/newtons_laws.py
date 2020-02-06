'''
Code for studying newton's laws using sr04 sensor
Logs data from various sensors.
Author  : Jithin B.P, jithinbp@gmail.com
Date    : Sep-2019
License : GNU GPL version 3
'''
import sys,time
t = time.time()

from utils import *
if sys.version_info.major==3:
	from PyQt5 import QtGui, QtCore, QtWidgets
else:
	from PyQt4 import QtGui, QtCore
	from PyQt4 import QtGui as QtWidgets

import pyqtgraph as pg

import math, os.path, struct
from collections import OrderedDict

from layouts import ui_newtonslaws

from layouts.gauge import Gauge
import functools
from functools import partial


import numpy as np
import math
import numpy.linalg

print(time.time()-t)
colors=['#00ff00','#ff0000','#ffff80',(10,255,255)]+[(50+np.random.randint(200),50+np.random.randint(200),150+np.random.randint(100)) for a in range(10)]

Byte =     struct.Struct("B") # size 1
ShortInt = struct.Struct("H") # size 2
Integer=   struct.Struct("I") # size 4

############# MATHEMATICAL AND ANALYTICS ###############

#TODO

############# MATHEMATICAL AND ANALYTICS ###############


class Expt(QtWidgets.QMainWindow, ui_newtonslaws.Ui_MainWindow):
	def __init__(self, device=None):
		super(Expt, self).__init__()
		self.setupUi(self)

		self.p = device

		self.rec = True #Recording enabled

		#Define some keyboard shortcuts for ease of use
		self.shortcutActions={}
		self.shortcuts={" ":self.toggleRecord}
		for a in self.shortcuts:
			shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(a), self)
			shortcut.activated.connect(self.shortcuts[a])
			self.shortcutActions[a] = shortcut

		self.T = 0
		self.start_time = time.time()
		self.points=0
		self.time = np.empty(300)
		self.pcurve_data = np.empty(300)
		self.vcurve_data = []
		self.acurve_data = []

		self.pcurve = self.graphPosition.plot(pen=colors[0])
		self.graphPosition.setRange(xRange=[-5, 0])

		self.pcurve2 = self.graphResults.plot(pen=colors[0],name='Position')
		self.graphResults.setLabel('left', "Position", units='cm',color='#00ff00')

		self.graphResults.viewBoxes=[]

		## Add secondary Axis for Velocity
		self.p3 = pg.ViewBox()
		ax3 = pg.AxisItem('right')
		self.graphResults.plotItem.layout.addItem(ax3, 2, 3) 
		self.graphResults.plotItem.scene().addItem(self.p3)
		ax3.linkToView(self.p3)
		self.p3.setXLink(self.graphResults)
		ax3.setZValue(-10000)
		ax3.setLabel('Velocity', color=colors[1])
		self.p3.setGeometry(self.graphResults.plotItem.vb.sceneBoundingRect())
		self.p3.linkedViewChanged(self.graphResults.plotItem.vb, self.p3.XAxis)
		self.graphResults.viewBoxes.append(self.p3)
		self.vcurve = pg.PlotDataItem(pen=colors[1],name='Velocity')
		self.p3.addItem(self.vcurve)

		## Add third Axis for Acceleration
		self.p2 = pg.ViewBox()
		ax2 = pg.AxisItem('right')
		self.graphResults.plotItem.layout.addItem(ax2, 2, 4) 
		self.graphResults.plotItem.scene().addItem(self.p2)
		ax2.linkToView(self.p2)
		self.p2.setXLink(self.graphResults)
		ax2.setZValue(-10000)
		ax2.setLabel('Acceleration', color=colors[2])
		self.p2.setGeometry(self.graphResults.plotItem.vb.sceneBoundingRect())
		self.p2.linkedViewChanged(self.graphResults.plotItem.vb, self.p2.XAxis)
		self.graphResults.viewBoxes.append(self.p2)
		self.acurve = pg.PlotDataItem(pen=colors[2],name='Acceleration')
		self.p2.addItem(self.acurve)

		Callback = functools.partial(self.updateViews,self.graphResults)
		self.graphResults.getViewBox().sigStateChanged.connect(Callback)

		self.graphResults.setRange(xRange=[0, 5])

		self.region = pg.LinearRegionItem()
		self.region.setBrush([255,0,50,50])
		self.region.setZValue(10)
		for a in self.region.lines: a.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor)); 
		self.graphPosition.addItem(self.region, ignoreBounds=False)
		self.region.setRegion([-3,-.5])

		#cross hair
		self.vLine = pg.InfiniteLine(angle=90, movable=False)
		self.hLine = pg.InfiniteLine(angle=0, movable=False)
		self.graphResults.addItem(self.vLine, ignoreBounds=True)
		self.graphResults.addItem(self.hLine, ignoreBounds=True)
		self.graphResults.setTitle('Pause acquisition to view derivates here',justify='left')
		self.resultslabel = self.graphResults.plotItem.titleLabel
		self.proxy = pg.SignalProxy(self.graphResults.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)

		# Populate contents of samplesBox(For moving average) and polyBox(Degree of polynomial)
		self.samplesBox.addItems(['30']+[str(a*5) for a in range(1,20)])
		self.polyBox.addItems([str(a) for a in range(2,7)])
		self.samplesBox.setCurrentIndex(5)
		self.samplesBox.setCurrentIndex(0)

		self.gauge = Gauge(self)
		self.gauge.setObjectName("distance")
		self.gauge.set_MinValue(0)
		self.gauge.set_MaxValue(50)
		self.gaugeLayout.addWidget(self.gauge)

		self.startTime = time.time()
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.updateEverything)
		self.timer.start(2)

	def mouseMoved(self,evt):
		pos = evt[0]  ## using signal proxy turns original arguments into a tuple
		vb = self.graphResults.plotItem.vb
		if vb.sceneBoundingRect().contains(pos):
			mousePoint = vb.mapSceneToView(pos)
			index = int(np.abs(self.time - mousePoint.x()).argmin()) #(np.abs(arr-val)).argmin()
			if index > 0 and index < len(self.vcurve_data):
				self.resultslabel.setText("<span style='font-size: 12pt'>x=%0.3f,   <span style='color: green'>P=%0.1f cm</span>,<span style='color: red'>V=%0.2f</span>,   <span style='color: yellow'>A=%0.2f</span>" % (mousePoint.x(), self.pcurve_data[index], self.vcurve_data[index], self.acurve_data[index]))
			self.vLine.setPos(mousePoint.x())
			self.hLine.setPos(mousePoint.y())


	def updateViews(self,plot):
			for a in plot.viewBoxes:
				a.setGeometry(plot.getViewBox().sceneBoundingRect())
				a.linkedViewChanged(plot.plotItem.vb, a.XAxis)

	def updateEverything(self):
		if self.rec:
			D = self.p.sr04_distance()
			if D is None: return
			self.gauge.update_value(D)
			self.T = time.time() - self.start_time
			self.time[self.points] = self.T
			self.pcurve_data[self.points] = D
			self.pcurve.setData(self.time[:self.points],self.pcurve_data[:self.points])
			self.pcurve.setPos(-self.T, 0)


			self.points+=1
			if self.points >= self.time.shape[0]-1:
				tmp = self.time
				self.time = np.empty(self.time.shape[0] * 2) #double the size
				self.time[:tmp.shape[0]] = tmp
				tmp = self.pcurve_data
				self.pcurve_data = np.empty(self.pcurve_data.shape[0] * 2) #double the size
				self.pcurve_data[:tmp.shape[0]] = tmp


	### ANALYSIS : https://dsp.stackexchange.com/a/9512
	### Accepted answer on using moving averages for this particular problem.

	def sg_filter(self,x, m, k=0):
		"""
		x = Vector of sample times
		m = Order of the smoothing polynomial
		k = Which derivative
		"""
		mid = int(len(x) / 2)        
		a = x - x[mid]
		expa = lambda x: list(map(lambda i: i**x, a))
		mp = list(map(expa, range(0,m+1)))
		A = np.r_[mp].transpose()
		Ai = np.linalg.pinv(A)
		return Ai[k]

	def smooth(self,x, y, size=5, order=2, deriv=0):
		if deriv > order:
			print( "deriv must be <= order")
			return None

		n = len(x)
		m = size
		result = np.zeros(n)
		for i in range(m, n-m):
			start, end = i - m, i + m + 1
			f = self.sg_filter(np.array(x[start:end]), order, deriv)
			result[i] = np.dot(f, np.array(y[start:end]))

		if deriv > 1:
			result *= math.factorial(deriv)

		return result

	def redoAnalysis(self,s):
		if not self.rec: #Analysis mode
			self.analysis()

	def analysis(self):
		self.recordBox.setChecked(False)
		self.setRecord(False)

		T = np.array(self.time[:self.points])
		pos = np.array(self.pcurve_data[:self.points])

		if self.splineBox.currentIndex()!=0:
			z = np.polyfit(T,pos,10)
			zp = np.poly1d(z)
			pos = zp(T)


		self.pcurve2.setData(T,pos)
		smoothing_size = int(self.samplesBox.currentText()) # points for smoothing
		order = int(self.polyBox.currentText()) #  degree of polynomial

		params = (T, pos, smoothing_size, order)
		V = self.smooth(*params, deriv=1) #1st derivative
		A = self.smooth(*params, deriv=2) #2nd derivative

		self.vcurve_data = V
		self.acurve_data = A

		#self.pcurve2.setData(T,pos)
		self.vcurve.setData(T,V)
		self.acurve.setData(T,A)
		self.graphResults.autoRange()
		self.p2.autoRange()
		self.p3.autoRange()

	def clearAll(self):
		self.T = 0
		self.start_time = time.time()
		self.points=0
		self.time = np.empty(300)
		self.pcurve_data = np.empty(300)
		self.vcurve_data = []
		self.acurve_data = []

		self.graphPosition.setRange(xRange=[-5, 0])
		self.pcurve.setPos(0, 0)

		for a in [self.pcurve,self.pcurve2,self.vcurve,self.acurve]:
			a.clear()

	def setRecord(self,val):
		self.rec = val
		if self.rec:
			self.clearAll()
			self.resultslabel.setText('Acquiring data...')
			self.splitter.setSizes([200,100])
		else:
			self.splitter.setSizes([100,200])
	def toggleRecord(self):
		if self.rec:
			self.recordBox.setChecked(False)
			self.setRecord(False)
			self.analysis()
		else:
			self.recordBox.setChecked(True)
			self.setRecord(True)

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
	
