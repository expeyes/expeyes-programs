'''
Code for viewing I2C sensor data using ExpEYES
Logs data from various sensors.
Author  : Jithin B.P, jithinbp@gmail.com
Date    : Sep-2019
License : GNU GPL version 3
'''
import sys

from PyQt5 import QtGui, QtCore, QtWidgets

import time, math, os.path, struct
import utils

from collections import OrderedDict

from layouts import ui_dio_sensor,ui_dio_control,ui_dio_robot
from layouts.advancedLoggerTools import LOGGER

from layouts.gauge import Gauge
import functools
from functools import partial
import time


try:
	from scipy import optimize
except:
	print('scipy not available')




from pyqtgraph.exporters import Exporter
from pyqtgraph.parametertree import Parameter
from pyqtgraph.Qt import QtGui, QtCore, QtSvg, USE_PYSIDE
from pyqtgraph import functions as fn
import pyqtgraph as pg

__all__ = ['PQG_ImageExporter']


class PQG_ImageExporter(Exporter):
    Name = "Working Image Exporter (PNG, TIF, JPG, ...)"
    allowCopy = True

    def __init__(self, item):
        Exporter.__init__(self, item)
        tr = self.getTargetRect()
        if isinstance(item, QtGui.QGraphicsItem):
            scene = item.scene()
        else:
            scene = item
        # scene.views()[0].backgroundBrush()
        bgbrush = pg.mkBrush('w')
        bg = bgbrush.color()
        if bgbrush.style() == QtCore.Qt.NoBrush:
            bg.setAlpha(0)

        self.params = Parameter(name='params', type='group', children=[
            {'name': 'width', 'type': 'int',
                'value': tr.width(), 'limits': (0, None)},
            {'name': 'height', 'type': 'int',
                'value': tr.height(), 'limits': (0, None)},
            {'name': 'antialias', 'type': 'bool', 'value': True},
            {'name': 'background', 'type': 'color', 'value': bg},
        ])
        self.params.param('width').sigValueChanged.connect(self.widthChanged)
        self.params.param('height').sigValueChanged.connect(self.heightChanged)

    def widthChanged(self):
        sr = self.getSourceRect()
        ar = float(sr.height()) / sr.width()
        self.params.param('height').setValue(
            self.params['width'] * ar, blockSignal=self.heightChanged)

    def heightChanged(self):
        sr = self.getSourceRect()
        ar = float(sr.width()) / sr.height()
        self.params.param('width').setValue(
            self.params['height'] * ar, blockSignal=self.widthChanged)

    def parameters(self):
        return self.params

    def export(self, fileName=None, toBytes=False, copy=False):
        if fileName is None and not toBytes and not copy:
            if USE_PYSIDE:
                filter = ["*."+str(f)
                          for f in QtGui.QImageWriter.supportedImageFormats()]
            else:
                filter = ["*."+bytes(f).decode('utf-8')
                          for f in QtGui.QImageWriter.supportedImageFormats()]
            preferred = ['*.png', '*.tif', '*.jpg']
            for p in preferred[::-1]:
                if p in filter:
                    filter.remove(p)
                    filter.insert(0, p)
            self.fileSaveDialog(filter=filter)
            return

        targetRect = QtCore.QRect(
            0, 0, self.params['width'], self.params['height'])
        sourceRect = self.getSourceRect()

        #self.png = QtGui.QImage(targetRect.size(), QtGui.QImage.Format_ARGB32)
        # self.png.fill(pyqtgraph.mkColor(self.params['background']))
        w, h = self.params['width'], self.params['height']
        if w == 0 or h == 0:
            raise Exception(
                "Cannot export image with size=0 (requested export size is %dx%d)" % (w, h))
        bg = np.empty((int(self.params['width']), int(
            self.params['height']), 4), dtype=np.ubyte)
        color = self.params['background']
        bg[:, :, 0] = color.blue()
        bg[:, :, 1] = color.green()
        bg[:, :, 2] = color.red()
        bg[:, :, 3] = color.alpha()
        self.png = fn.makeQImage(bg, alpha=True)

        # set resolution of image:
        origTargetRect = self.getTargetRect()
        resolutionScale = targetRect.width() / origTargetRect.width()
        #self.png.setDotsPerMeterX(self.png.dotsPerMeterX() * resolutionScale)
        #self.png.setDotsPerMeterY(self.png.dotsPerMeterY() * resolutionScale)

        painter = QtGui.QPainter(self.png)
        #dtr = painter.deviceTransform()
        try:
            self.setExportMode(True, {
                               'antialias': self.params['antialias'], 'background': self.params['background'], 'painter': painter, 'resolutionScale': resolutionScale})
            painter.setRenderHint(
                QtGui.QPainter.Antialiasing, self.params['antialias'])
            self.getScene().render(painter, QtCore.QRectF(
                targetRect), QtCore.QRectF(sourceRect))
        finally:
            self.setExportMode(False)
        painter.end()

        if copy:
            QtGui.QApplication.clipboard().setImage(self.png)
        elif toBytes:
            return self.png
        else:
            self.png.save(fileName)


PQG_ImageExporter.register()






import pyqtgraph as pg
import numpy as np

colors=[(0,255,0),(255,0,0),(255,255,100),(10,255,255)]+[(50+np.random.randint(200),50+np.random.randint(200),150+np.random.randint(100)) for a in range(10)]

Byte =     struct.Struct("B") # size 1
ShortInt = struct.Struct("H") # size 2
Integer=   struct.Struct("I") # size 4

############# MATHEMATICAL AND ANALYTICS ###############

def find_peak(va):
	vmax = 0.0
	size = len(va)
	index = 0
	for i in range(1,size):		# skip first 2 channels, DC
		if va[i] > vmax:
			vmax = va[i]
			index = i
	return index

#-------------------------- Fourier Transform ------------------------------------
def fft(ya, si):
	'''
	Returns positive half of the Fourier transform of the signal ya. 
	Sampling interval 'si', in milliseconds
	'''
	NP = len(ya)
	if NP%2: #odd number
		ya = ya[:-1]
		NP-=1
	v = np.array(ya)
	tr = abs(np.fft.fft(v))/NP
	frq = np.fft.fftfreq(NP, si)
	x = frq.reshape(2,int(NP/2))
	y = tr.reshape(2,int(NP/2))
	return x[0], y[0]    

def find_frequency(x,y):		# Returns the fundamental frequency using FFT
	tx,ty = fft(y, x[1]-x[0])
	index = find_peak(ty)
	if index == 0:
		return None
	else:
		return tx[index]

#-------------------------- Sine Fit ------------------------------------------------
def sine_eval(x,p):			# y = a * sin(2*pi*f*x + phi)+ offset
	return p[0] * np.sin(2*np.pi*p[1]*x+p[2])+p[3]

def sine_erf(p,x,y):					
	return y - sine_eval(x,p)


def fit_sine(xa,ya, freq = 0):	# Time in mS, V in volts, freq in Hz, accepts numpy arrays
	size = len(ya)
	mx = max(ya)
	mn = min(ya)
	amp = (mx-mn)/2
	off = np.average(ya)
	if freq == 0:						# Guess frequency not given
		freq = find_frequency(xa,ya)
	if freq == None:
		return None
	#print 'guess a & freq = ', amp, freq
	par = [amp, freq, 0.0, off] # Amp, freq, phase , offset
	par, pcov = optimize.leastsq(sine_erf, par, args=(xa, ya))
	return par
	

#--------------------------Damped Sine Fit ------------------------------------------------
def dsine_eval(x,p):
	return     p[0] * np.sin(2*np.pi*p[1]*x+p[2]) * np.exp(-p[4]*x) + p[3]
def dsine_erf(p,x,y):
	return y - dsine_eval(x,p)


def fit_dsine(xlist, ylist, freq = 0):
	size = len(xlist)
	xa = np.array(xlist, dtype=np.float)
	ya = np.array(ylist, dtype=np.float)
	amp = (max(ya)-min(ya))/2
	off = np.average(ya)
	if freq == 0:
		freq = find_frequency(xa,ya)
	if freq==None: return None
	par = [amp, freq, 0.0, off, 0.] # Amp, freq, phase , offset, decay constant
	par, pcov = optimize.leastsq(dsine_erf, par,args=(xa,ya))

	return par


############# MATHEMATICAL AND ANALYTICS ###############


########### I2C : SENSOR AND CONTROL LAYOUTS ##################


class DIOSENSOR(QtWidgets.QDialog,ui_dio_sensor.Ui_Dialog):
	def __init__(self,parent,sensor):
		super(DIOSENSOR, self).__init__(parent)
		name = sensor['name']
		self.initialize = sensor['init']
		self.read = sensor['read']
		self.isPaused = False
		self.setupUi(self)
		self.currentPage = 0
		self.scale = 1.
		self.max = sensor.get('max',None)
		self.min = sensor.get('min',None)
		self.fields = sensor.get('fields',None)
		self.widgets =[]
		for a in sensor.get('config',[]): #Load configuration menus
			l = QtWidgets.QLabel(a.get('name',''))
			self.configLayout.addWidget(l) ; self.widgets.append(l)
			l = QtWidgets.QComboBox(); l.addItems(a.get('options',[]))
			l.currentIndexChanged['int'].connect(a.get('function',None))
			self.configLayout.addWidget(l) ; self.widgets.append(l)
			
		self.graph.setRange(xRange=[-5, 0])
		import pyqtgraph as pg
		self.region = pg.LinearRegionItem()
		self.region.setBrush([255,0,50,50])
		self.region.setZValue(10)
		for a in self.region.lines: a.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor)); 
		self.graph.addItem(self.region, ignoreBounds=False)
		self.region.setRegion([-3,-.5])



		self.curves = {}; self.fitCurves = {}
		self.gauges = {}
		self.datapoints=0
		self.T = 0
		self.time = np.empty(300)
		self.start_time = time.time()
		row = 1; col=1;
		for a,b,c in zip(self.fields,self.min,self.max):
			gauge = Gauge(self)
			gauge.setObjectName(a)
			gauge.set_MinValue(b)
			gauge.set_MaxValue(c)
			#listItem = QtWidgets.QListWidgetItem()
			#self.listWidget.addItem(listItem)
			#self.listWidget.setItemWidget(listItem, gauge)
			self.gaugeLayout.addWidget(gauge,row,col)
			col+= 1
			if col == 4:
				row += 1
				col = 1
			self.gauges[gauge] = [a,b,c] #Name ,min, max value
			
			curve = self.graph.plot(pen=colors[len(self.curves.keys())])
			fitcurve = self.graph.plot(pen=colors[len(self.curves.keys())],width=2)
			self.curves[curve] = np.empty(300)
			self.fitCurves[curve] = fitcurve

		
		self.setWindowTitle('Sensor : %s'%name)

	def next(self):
		if self.currentPage==1:
			self.currentPage = 0
			self.switcher.setText("Data Logger")
		else:
			self.currentPage = 1
			self.switcher.setText("Analog Gauge")

		self.monitors.setCurrentIndex(self.currentPage)

	def changeRange(self,state):
		for a in self.gauges:
			self.scale = self.gauges[a][1]/65535. if state else 1.
			a.set_MaxValue(self.gauges[a][1] if state else 65535)

	def setValue(self,vals):
		if vals is None:
			print('check connections')
			return
		if self.currentPage == 0: #Update Analog Gauges
			p=0
			for a in self.gauges:
				a.update_value(vals[p]*self.scale)
				p+=1
		elif self.currentPage == 1: #Update Data Logger
			if self.isPaused: return
			p=0
			self.T = time.time() - self.start_time
			self.time[self.datapoints] = self.T
			if self.datapoints >= self.time.shape[0]-1:
				tmp = self.time
				self.time = np.empty(self.time.shape[0] * 2) #double the size
				self.time[:tmp.shape[0]] = tmp

			for a in self.curves:
				self.curves[a][self.datapoints] = vals[p] * self.scale
				if not p: self.datapoints += 1 #Increment datapoints once per set. it's shared

				if self.datapoints >= self.curves[a].shape[0]-1:
					tmp = self.curves[a]
					self.curves[a] = np.empty(self.curves[a].shape[0] * 2) #double the size
					self.curves[a][:tmp.shape[0]] = tmp
				a.setData(self.time[:self.datapoints],self.curves[a][:self.datapoints])
				a.setPos(-self.T, 0)
				p+=1

	def sineFit(self):
		self.pauseBox.setChecked(True)
		S,E=self.region.getRegion()
		start = (np.abs(self.time[:self.datapoints]- self.T - S)).argmin()
		end = (np.abs(self.time[:self.datapoints]-self.T - E)).argmin()
		print(self.T,start,end,S,E,self.time[start],self.time[end])
		res = 'Amp, Freq, Phase, Offset<br>'
		for a in self.curves:
			try:
					fa=fit_sine(self.time[start:end],self.curves[a][start:end])
					if fa is not None:
							amp=abs(fa[0])
							freq=fa[1]
							phase = fa[2]
							offset = fa[3]
							s = '%5.2f , %5.3f Hz, %.2f, %.1f<br>'%(amp,freq, phase, offset)
							res+= s
							x = np.linspace(self.time[start],self.time[end],1000)
							self.fitCurves[a].clear()
							self.fitCurves[a].setData(x-self.T,sine_eval(x,fa))
			except Exception as e:
					res+='--<br>'
					print (e.message)
					pass
		QtWidgets.QMessageBox.information(self, ' Sine Fit Results ', res)


	def dampedSineFit(self):
		self.pauseBox.setChecked(True)
		S,E=self.region.getRegion()
		start = (np.abs(self.time[:self.datapoints]- self.T - S)).argmin()
		end = (np.abs(self.time[:self.datapoints]-self.T - E)).argmin()
		print(self.T,start,end,S,E,self.time[start],self.time[end])
		res = 'Amplitude, Freq, phase, Damping<br>'
		for a in self.curves:
			try:
					fa=fit_dsine(self.time[start:end],self.curves[a][start:end])
					if fa is not None:
							amp=abs(fa[0])
							freq=fa[1]
							decay=fa[4]
							phase = fa[2]
							s = '%5.2f , %5.3f Hz, %.3f, %.3e<br>'%(amp,freq,phase,decay)
							res+= s
							x = np.linspace(self.time[start],self.time[end],1000)
							self.fitCurves[a].clear()
							self.fitCurves[a].setData(x-self.T,dsine_eval(x,fa))
			except Exception as e:
					res+='--<br>'
					print (e.message)
					pass
		QtWidgets.QMessageBox.information(self, ' Damped Sine Fit Results ', res)


	def pause(self,val):
		self.isPaused = val
		if not val: #clear fit plots
			for a in self.curves:
				self.fitCurves[a].clear()

	def launch(self):
		if self.initialize is not None:
			self.initialize()
		self.show()


class DIOCONTROL(QtWidgets.QDialog,ui_dio_control.Ui_Dialog):
	def __init__(self,parent,sensor):
		super(DIOCONTROL, self).__init__(parent)
		name = sensor['name']
		self.initialize = sensor['init']
		self.setupUi(self)
		self.widgets =[]
		self.gauges = {}
		self.functions = {}

		for a in sensor.get('write',[]): #Load configuration menus
			l = QtWidgets.QSlider(self); l.setMinimum(a[1]); l.setMaximum(a[2]);l.setValue(a[3]);
			l.setOrientation(QtCore.Qt.Orientation(0x1)) #Qt.Horizontal
			l.valueChanged['int'].connect(functools.partial(self.write,l))
			self.configLayout.addWidget(l) ; self.widgets.append(l)
			
			gauge = Gauge(self)
			gauge.setObjectName(a[0])
			gauge.set_MinValue(a[1])
			gauge.set_MaxValue(a[2])
			gauge.update_value(a[3])
			self.gaugeLayout.addWidget(gauge)
			self.gauges[l] = gauge #Name ,min, max value,default value, func
			self.functions[l] = a[4]
			
		self.setWindowTitle('Control : %s'%name)

	def write(self,w,val):
		self.gauges[w].update_value(val)
		self.functions[w](val)


	def launch(self):
		self.initialize()
		self.show()




class DIOROBOT(QtWidgets.QDialog,ui_dio_robot.Ui_Dialog):
	def __init__(self,parent,sensor):
		super(DIOROBOT, self).__init__(parent)
		name = sensor['name']
		self.initialize = sensor['init']
		self.setupUi(self)
		self.widgets =[]
		self.gauges = OrderedDict()
		self.lastPos = OrderedDict()
		self.functions = OrderedDict()
		self.positions = []

		for a in sensor.get('write',[]): #Load configuration menus
			l = QtWidgets.QSlider(self); l.setMinimum(a[1]); l.setMaximum(a[2]);l.setValue(a[3]);
			l.setOrientation(QtCore.Qt.Orientation(0x1)) #Qt.Horizontal
			l.valueChanged['int'].connect(functools.partial(self.write,l))
			self.configLayout.addWidget(l) ; self.widgets.append(l)
			
			gauge = Gauge(self)
			gauge.setObjectName(a[0])
			gauge.set_MinValue(a[1])
			gauge.set_MaxValue(a[2])
			gauge.update_value(a[3])
			self.lastPos[l] = a[3]
			self.gaugeLayout.addWidget(gauge)
			self.gauges[l] = gauge #Name ,min, max value,default value, func
			self.functions[l] = a[4]
			
		self.setWindowTitle('Control : %s'%name)

	def write(self,w,val):
		self.gauges[w].update_value(val)
		self.lastPos[w] = val
		self.functions[w](val)

	def add(self):
		self.positions.append([a.value() for a in self.lastPos.keys()])
		item = QtWidgets.QListWidgetItem("%s" % str(self.positions[-1]))
		self.listWidget.addItem(item)
		print(self.positions)

	def play(self):
		mypos = [a.value() for a in self.lastPos.keys()] # Current position
		sliders = list(self.gauges.keys())
		for nextpos in self.positions:
			dx = [(x-y) for x,y in zip(nextpos,mypos)]  #difference between next position and current
			distance = max(dx)
			for travel in range(20):
				for step in range(4):
						self.write(sliders[step],int(mypos[step]))
						mypos[step] += dx[step]/20.
				time.sleep(0.01)
							
						

	def launch(self):
		self.initialize()
		self.show()



class Expt(QtWidgets.QWidget):
	def __init__(self, device=None):
		QtWidgets.QWidget.__init__(self)
		self.p = device
		device.set_pv1(2)
		self.I2C = device.I2C	        #connection to the device hardware
		self.sensorList = []
		self.logger = LOGGER(self.I2C)
		right = QtWidgets.QVBoxLayout() # right side vertical layout
		right.setAlignment(QtCore.Qt.AlignmentFlag(0x0020)) # Qt.AlignTop
		right.setSpacing(4)
	
		b = QtWidgets.QPushButton(self.tr("Scan"))
		right.addWidget(b)
		b.clicked.connect(self.scan)
		
		self.sensorLayout = QtWidgets.QHBoxLayout()
		
		full = QtWidgets.QVBoxLayout()
		full.addLayout(right)
		full.addLayout(self.sensorLayout)
		self.msgwin = QtWidgets.QLabel(text=self.tr(''))
		self.msgwin.setMinimumWidth(500)
		full.addWidget(self.msgwin)
				
		self.setLayout(full)

		self.startTime = time.time()
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.updateEverything)
		self.timer.start(2)

	def updateEverything(self):
		for a in self.sensorList:
			if a[0].isVisible():
				if a[0].currentPage == 0 or a[0].isPaused == 0: #If on logger page(1) , pause button should be unchecked
					v = a[0].read()
					if v is not None:
						a[0].setValue(v)



	############ I2C SENSORS #################
	def scan(self):
		if self.p.connected:
			x = self.logger.I2CScan()
			print('Responses from: ',x)
			for a in self.sensorList:
				a[0].setParent(None)
				a[1].setParent(None)
			self.sensorList = []
			for a in x:
				s = self.logger.sensors.get(a,None)
				if s is not None:
					btn = QtWidgets.QPushButton(s['name']+':'+hex(a))
					dialog = DIOSENSOR(self,s)
					btn.clicked.connect(dialog.launch)
					self.sensorLayout.addWidget(btn)
					self.sensorList.append([dialog,btn])
					continue

				s = self.logger.controllers.get(a,None)
				if s is not None:
					btn = QtWidgets.QPushButton(s['name']+':'+hex(a))
					dialog = DIOCONTROL(self,s)
					btn.clicked.connect(dialog.launch)
					self.sensorLayout.addWidget(btn)
					#self.sensorList.append([dialog,btn])
					continue

				s = self.logger.special.get(a,None)
				if s is not None:
					btn = QtWidgets.QPushButton(s['name']+':'+hex(a))
					dialog = DIOROBOT(self,s)
					btn.clicked.connect(dialog.launch)
					self.sensorLayout.addWidget(btn)
					#self.sensorList.append([dialog,btn])
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
	
