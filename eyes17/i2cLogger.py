'''
Code for viewing I2C sensor data using ExpEYES
Logs data from various sensors.
Author  : Jithin B.P, jithinbp@gmail.com
Date    : Sep-2019
License : GNU GPL version 3
'''
import sys

if sys.version_info.major==3:
	from PyQt5 import QtGui, QtCore, QtWidgets
else:
	from PyQt4 import QtGui, QtCore
	from PyQt4 import QtGui as QtWidgets

import time, utils, math, os.path, struct
from collections import OrderedDict

from layouts import ui_dio_sensor,ui_dio_control,ui_dio_robot

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
			l.setOrientation(QtCore.Qt.Horizontal)
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
			l.setOrientation(QtCore.Qt.Horizontal)
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


########### I2C : SENSOR AND CONTROL LAYOUTS ##################


class LOGGER:	
	def __init__(self,I2C):
		self.sensors={
			0x39:{
				'name':'TSL2561 Luminosity Sensor',
				'init':self.TSL2561_init,
				'read':self.TSL2561_all,
				'fields':['total','IR'],
				'min':[0,0],
				'max':[2**15,2**15],
				'config':[{
							'name':'gain',
							'options':['1x','16x'],
							'function':self.TSL2561_gain
							},
							{
							'name':'Integration Time',
							'options':['3 mS','101 mS','402 mS'],
							'function':self.TSL2561_timing
							}
					] },
			0x1E:{
				'name':'HMC5883L 3 Axis Magnetometer ',
				'init':self.HMC5883L_init,
				'read':self.HMC5883L_all,
				'fields':['Mx','My','Mz'],
				'min':[-5000,-5000,-5000],
				'max':[5000,5000,5000],
				'config':[{
							'name':'gain',
							'options':['1x','16x'],
							'function':self.TSL2561_gain
							},
							{
							'name':'Integration Time',
							'options':['3 mS','101 mS','402 mS'],
							'function':self.TSL2561_timing
							}
					] },
			0x68:{
				'name':'MPU6050 3 Axis Accelerometer and Gyro (Ax, Ay, Az, Temp, Gx, Gy, Gz) ',
				'init':self.MPU6050_init,
				'read':self.MPU6050_all,
				'fields':['Ax','Ay','Az','Temp','Gx','Gy','Gz'],
				'min':[-1*2**15,-1*2**15,-1*2**15,0,-1*2**15,-1*2**15,-1*2**15],
				'max':[2**15,2**15,2**15,2**16,2**15,2**15,2**15],
				'config':[{
					'name':'Gyroscope Range',
					'options':['250','500','1000','2000'],
					'function':self.MPU6050_gyro_range
					},
					{
					'name':'Accelerometer Range',
					'options':['2x','4x','8x','16x'],
					'function':self.MPU6050_accel_range
					},
					{
					'name':'Kalman',
					'options':['OFF','0.001','0.01','0.1','1','10'],
					'function':self.MPU6050_kalman_set
					}
			]},
			118:{
				'name':'BMP280 Pressure and Temperature sensor',
				'init':self.BMP280_init,
				'read':self.BMP280_all,
				'fields':['Pressure','Temp','Alt'],
				'min':[0,0,0],
				'max':[1600,100,10],
				},
			119:{
				'name':'MS5611 Pressure and Temperature Sensor',
				'init':self.MS5611_init,
				'read':self.MS5611_all,
				'fields':['Pressure','Temp','Alt'],
				'min':[0,0,0],
				'max':[1600,100,10],
				},
			0x41:{  #A0 pin connected to Vs . Otherwise address 0x40 conflicts with PCA board.
				'name':'INA3221 Current Sensor',
				'init':self.INA3221_init,
				'read':self.INA3221_all,
				'fields':['CH1','CH2','CH3'],
				'min':[0,0,0],
				'max':[1000,1000,1000],
				},
			0x5A:{
				'name':'MLX90614 Passive IR thermometer',
				'init':self.MLX90614_init,
				'read':self.MLX90614_all,
				'fields':['TEMP'],
				'min':[0],
				'max':[350]}
		}
		self.controllers={
			0x62:{
				'name':'MCP4725 DAC',
				'init':self.MCP4725_init,
				'write':[['CH0',0,4095,0,self.MCP4725_set]],
				},
		}

		self.special={
			0x40:{
				'name':'PCA9685 PWM',
				'init':self.PCA9685_init,
				'write':[['Channel 1',0,180,90,functools.partial(self.PCA9685_set,1)], #name, start, stop, default, function
						['Channel 2',0,180,90,functools.partial(self.PCA9685_set,2)],
						['Channel 3',0,180,90,functools.partial(self.PCA9685_set,3)],
						['Channel 4',0,180,90,functools.partial(self.PCA9685_set,4)],
						],
				}
		}
		self.I2C = I2C
		self.I2CWriteBulk = I2C.writeBulk
		self.I2CReadBulk = I2C.readBulk
		self.I2CScan = I2C.scan

	'''
	def I2CScan(self):
	def I2CWriteBulk(self,address,bytestream): 
	def I2CReadBulk(self,address,register,total): 
	'''
	class KalmanFilter(object):
		'''
		Credits:http://scottlobdell.me/2014/08/kalman-filtering-python-reading-sensor-input/
		'''
		def __init__(self, var, est,initial_values): #var = process variance. est = estimated measurement var
			self.var = np.array(var)
			self.est = np.array(est)
			self.posteri_estimate = np.array(initial_values)
			self.posteri_error_estimate = np.ones(len(var),dtype=np.float16)

		def input(self, vals):
			vals = np.array(vals)
			priori_estimate = self.posteri_estimate
			priori_error_estimate = self.posteri_error_estimate + self.var

			blending_factor = priori_error_estimate / (priori_error_estimate + self.est)
			self.posteri_estimate = priori_estimate + blending_factor * (vals - priori_estimate)
			self.posteri_error_estimate = (1 - blending_factor) * priori_error_estimate

		def output(self):
			return self.posteri_estimate


	MPU6050_kalman = 0
	def MPU6050_init(self):
		self.I2CWriteBulk(0x68,[0x1B,0<<3]) #Gyro Range . 250
		self.I2CWriteBulk(0x68,[0x1C,0<<3]) #Accelerometer Range. 2
		self.I2CWriteBulk(0x68,[0x6B, 0x00]) #poweron

	def MPU6050_gyro_range(self,val):
		self.I2CWriteBulk(0x68,[0x1B,val<<3]) #Gyro Range . 250,500,1000,2000 -> 0,1,2,3 -> shift left by 3 positions

	def MPU6050_accel_range(self,val):
		print(val)
		self.I2CWriteBulk(0x68,[0x1C,val<<3]) #Accelerometer Range. 2,4,8,16 -> 0,1,2,3 -> shift left by 3 positions

	def MPU6050_kalman_set(self,val):
		if not val:
			self.MPU6050_kalman = 0
			return
		noise=[]
		for a in range(50):
			noise.append(np.array(self.MPU6050_all(disableKalman=True)))
		noise = np.array(noise)
		self.MPU6050_kalman = self.KalmanFilter(1e6*np.ones(noise.shape[1])/(10**val), np.std(noise,0)**2, noise[-1])


	def MPU6050_accel(self):
		b = self.I2CReadBulk(0x68, 0x3B ,6)
		if b is None:return None
		if None not in b:
			return [(b[x*2+1]<<8)|b[x*2] for x in range(3)] #X,Y,Z

	def MPU6050_gyro(self):
		b = self.I2CReadBulk(0x68, 0x3B+6 ,6)
		if b is None:return None
		if None not in b:
			return [(b[x*2+1]<<8)|b[x*2] for x in range(3)] #X,Y,Z

	def MPU6050_all(self,disableKalman=False):
		'''
		returns a 7 element list. Ax,Ay,Az,T,Gx,Gy,Gz
		returns None if communication timed out with I2C sensor
		disableKalman can be set to True if Kalman was previously enabled.
		'''
		b = self.I2CReadBulk(0x68, 0x3B ,14)
		if b is None:return None
		if None not in b:
			if (not self.MPU6050_kalman) or disableKalman:
				return [ np.int16((b[x*2]<<8)|b[x*2+1]) for x in range(7) ] #Ax,Ay,Az, Temp, Gx, Gy,Gz
			else:
				self.MPU6050_kalman.input([ np.int16((b[x*2]<<8)|b[x*2+1]) for x in range(7) ])
				return self.MPU6050_kalman.output()


	####### BMP280 ###################
	## Ported from https://github.com/farmerkeith/BMP280-library/blob/master/farmerkeith_BMP280.cpp
	BMP280_ADDRESS = 118
	BMP280_REG_CONTROL = 0xF4
	BMP280_REG_RESULT = 0xF6
	BMP280_oversampling = 0
	_BMP280_PRESSURE_MIN_HPA = 0
	_BMP280_PRESSURE_MAX_HPA = 1600
	_BMP280_sea_level_pressure = 1013.25 #for calibration.. from circuitpython library
	def BMP280_init(self):
		b = self.I2CReadBulk(self.BMP280_ADDRESS, 0xD0 ,1)
		if b is None:return None
		b = b[0]
		if b in [0x58,0x56,0x57]:
			print('BMP280. ID:',b)
		elif b==0x60:
			print('BME280 . includes humidity')
		else:
			print('ID unknown',b)
		# get calibration data
		b = self.I2CReadBulk(self.BMP280_ADDRESS, 0x88 ,24) #24 bytes containing calibration data
		coeff = list(struct.unpack('<HhhHhhhhhhhh', bytes(b)))
		coeff = [float(i) for i in coeff]
		self._BMP280_temp_calib = coeff[:3]
		self._BMP280_pressure_calib = coeff[3:]
		self._BMP280_t_fine = 0.

		#details of register 0xF4
		#mode[1:0] F4bits[1:0] 00=sleep, 01,10=forced, 11=normal
		#osrs_p[2:0] F4bits[4:2] 000=skipped, 001=16bit, 010=17bit, 011=18bit, 100=19bit, 101,110,111=20 bit
		#osrs_t[2:0] F4bits[7:5] 000=skipped, 001=16bit, 010=17bit, 011=18bit, 100=19bit, 101,110,111=20 bit
		#VALUE = (osrs_t & 0x7) << 5 | (osrs_p & 0x7) << 2 | (mode & 0x3); #
		self.I2CWriteBulk(self.BMP280_ADDRESS, [0xF4,0xFF]) #


	def _BMP280_calcTemperature(self,adc_t):
		v1 = (adc_t / 16384.0 - self._BMP280_temp_calib[0] / 1024.0) * self._BMP280_temp_calib[1]
		v2 = ((adc_t / 131072.0 - self._BMP280_temp_calib[0] / 8192.0) * ( adc_t / 131072.0 - self._BMP280_temp_calib[0] / 8192.0)) * self._BMP280_temp_calib[2]
		self._BMP280_t_fine = int(v1+v2)
		return (v1+v2) / 5120.0  #actual temperature. 

	def _BMP280_calcPressure(self,adc_p,adc_t):
		self._BMP280_calcTemperature(adc_t) #t_fine has been set now.
		# Algorithm from the BMP280 driver. adapted from adafruit adaptation of
		# https://github.com/BoschSensortec/BMP280_driver/blob/master/bmp280.c
		var1 = self._BMP280_t_fine / 2.0 - 64000.0
		var2 = var1 * var1 * self._BMP280_pressure_calib[5] / 32768.0
		var2 = var2 + var1 * self._BMP280_pressure_calib[4] * 2.0
		var2 = var2 / 4.0 + self._BMP280_pressure_calib[3] * 65536.0
		var3 = self._BMP280_pressure_calib[2] * var1 * var1 / 524288.0
		var1 = (var3 + self._BMP280_pressure_calib[1] * var1) / 524288.0
		var1 = (1.0 + var1 / 32768.0) * self._BMP280_pressure_calib[0]
		if not var1:
			return _BMP280_PRESSURE_MIN_HPA
		pressure = 1048576.0 - adc_p
		pressure = ((pressure - var2 / 4096.0) * 6250.0) / var1
		var1 = self._BMP280_pressure_calib[8] * pressure * pressure / 2147483648.0
		var2 = pressure * self._BMP280_pressure_calib[7] / 32768.0
		pressure = pressure + (var1 + var2 + self._BMP280_pressure_calib[6]) / 16.0
		pressure /= 100
		if pressure < self._BMP280_PRESSURE_MIN_HPA:
			return self._BMP280_PRESSURE_MIN_HPA
		if pressure > self._BMP280_PRESSURE_MAX_HPA:
			return self._BMP280_PRESSURE_MAX_HPA
		return pressure

	def BMP280_all(self):
		data = self.I2CReadBulk(self.BMP280_ADDRESS, 0xF7,6)
		if data is None:return None
		if None not in data:
			# Convert pressure and temperature data to 19-bits
			adc_p = (((data[0] & 0xFF) * 65536.) + ((data[1] & 0xFF) * 256.) + (data[2] & 0xF0)) / 16.
			adc_t = (((data[3] & 0xFF) * 65536.) + ((data[4] & 0xFF) * 256.) + (data[5] & 0xF0)) / 16.
		return [self._BMP280_calcPressure(adc_p,adc_t), self._BMP280_calcTemperature(adc_t), 0]

	####### MS5611 Altimeter ###################
	MS5611_ADDRESS = 119

	def MS5611_init(self):
		self.I2CWriteBulk(self.MS5611_ADDRESS, [0x1E]) # reset
		time.sleep(0.5)
		self._MS5611_calib = np.zeros(6)

		#calibration data.
		#pressure gain, offset . T coeff of P gain, offset. Ref temp. T coeff of T. all unsigned shorts.
		b = self.I2CReadBulk(self.MS5611_ADDRESS, 0xA2 ,2) 
		if b is None:return None
		self._MS5611_calib[0] = struct.unpack('!H', bytes(b))[0]
		b = self.I2CReadBulk(self.MS5611_ADDRESS, 0xA4 ,2) 
		self._MS5611_calib[1] = struct.unpack('!H', bytes(b))[0]
		b = self.I2CReadBulk(self.MS5611_ADDRESS, 0xA6 ,2) 
		self._MS5611_calib[2] = struct.unpack('!H', bytes(b))[0]
		b = self.I2CReadBulk(self.MS5611_ADDRESS, 0xA8 ,2) 
		self._MS5611_calib[3] = struct.unpack('!H', bytes(b))[0]
		b = self.I2CReadBulk(self.MS5611_ADDRESS, 0xAA ,2) 
		self._MS5611_calib[4] = struct.unpack('!H', bytes(b))[0]
		b = self.I2CReadBulk(self.MS5611_ADDRESS, 0xAC ,2) 
		self._MS5611_calib[5] = struct.unpack('!H', bytes(b))[0]
		print('Calibration for MS5611:',self._MS5611_calib)
		

	def MS5611_all(self):
		self.I2CWriteBulk(self.MS5611_ADDRESS, [0x48]) #  0x48 Pressure conversion(OSR = 4096) command
		time.sleep(0.01) #10mS
		b = self.I2CReadBulk(self.MS5611_ADDRESS, 0x00 ,3) #data.
		D1 = b[0]*65536 + b[1]*256 + b[2] #msb2, msb1, lsb

		self.I2CWriteBulk(self.MS5611_ADDRESS, [0x58]) #  0x58 Temperature conversion(OSR = 4096) command
		time.sleep(0.01)
		b = self.I2CReadBulk(self.MS5611_ADDRESS, 0x00 ,3) #data.
		D2 = b[0]*65536 + b[1]*256 + b[2] #msb2, msb1, lsb
		

		dT = D2 - self._MS5611_calib[4] * 256
		TEMP = 2000 + dT * self._MS5611_calib[5] / 8388608
		OFF = self._MS5611_calib[1] * 65536 + (self._MS5611_calib[3] * dT) / 128
		SENS = self._MS5611_calib[0] * 32768 + (self._MS5611_calib[2] * dT ) / 256
		T2 = 0;	OFF2 = 0;	SENS2 = 0
		if TEMP >= 2000 :
			T2 = 0
			OFF2 = 0
			SENS2 = 0
		elif TEMP < 2000 :
			T2 = (dT * dT) / 2147483648
			OFF2 = 5 * ((TEMP - 2000) * (TEMP - 2000)) / 2
			SENS2 = 5 * ((TEMP - 2000) * (TEMP - 2000)) / 4
			if TEMP < -1500 :
				OFF2 = OFF2 + 7 * ((TEMP + 1500) * (TEMP + 1500))
				SENS2 = SENS2 + 11 * ((TEMP + 1500) * (TEMP + 1500)) / 2

		TEMP = TEMP - T2
		OFF = OFF - OFF2
		SENS = SENS - SENS2
		pressure = ((((D1 * SENS) / 2097152) - OFF) / 32768.0) / 100.0
		cTemp = TEMP / 100.0
		return [pressure,cTemp,0]


	### INA3221 3 channel , high side current sensor #############
	INA3221_ADDRESS  = 0x41
	_INA3221_REG_CONFIG = 0x0
	_INA3221_SHUNT_RESISTOR_VALUE = 0.1
	_INA3221_REG_SHUNTVOLTAGE = 0x01
	_INA3221_REG_BUSVOLTAGE = 0x02

	def INA3221_init(self):
		self.I2CWriteBulk(self.INA3221_ADDRESS,[self._INA3221_REG_CONFIG, 0b01110101, 0b00100111 ])  #cont shunt.

	def INA3221_all(self):
		I = [0.,0.,0.]
		b = self.I2CReadBulk(self.INA3221_ADDRESS,self._INA3221_REG_SHUNTVOLTAGE  , 2) 
		if b is None:return None
		b[1]&=0xF8; I[0] = struct.unpack('!h',bytes(b))[0]
		b = self.I2CReadBulk(self.INA3221_ADDRESS,self._INA3221_REG_SHUNTVOLTAGE  +2 , 2) 
		if b is None:return None
		b[1]&=0xF8; I[1] = struct.unpack('!h',bytes(b))[0]
		b = self.I2CReadBulk(self.INA3221_ADDRESS,self._INA3221_REG_SHUNTVOLTAGE  +4 , 2) 
		if b is None:return None
		b[1]&=0xF8; I[2] = struct.unpack('!h',bytes(b))[0]
		return [0.005*I[0]/self._INA3221_SHUNT_RESISTOR_VALUE,0.005*I[1]/self._INA3221_SHUNT_RESISTOR_VALUE,0.005*I[2]/self._INA3221_SHUNT_RESISTOR_VALUE]
	

	TSL_GAIN = 0x00 # 0x00=1x , 0x10 = 16x
	TSL_TIMING = 0x00 # 0x00=3 mS , 0x01 = 101 mS, 0x02 = 402mS
	def TSL2561_init(self):
		self.I2CWriteBulk(0x39,[0x80 , 0x03 ]) #poweron
		self.I2CWriteBulk(0x39,[0x80 | 0x01, self.TSL_GAIN|self.TSL_TIMING ]) 
		return self.TSL2561_all()

	def TSL2561_gain(self,gain):
		self.TSL_GAIN = gain<<4
		self.TSL2561_config(self.TSL_GAIN,self.TSL_TIMING)
		
	def TSL2561_timing(self,timing):
		self.TSL_TIMING = timing
		self.TSL2561_config(self.TSL_GAIN,self.TSL_TIMING)

	def TSL2561_rate(self,timing):
		self.TSL_TIMING = timing
		self.TSL2561_config(self.TSL_GAIN,self.TSL_TIMING)

	def TSL2561_config(self,gain,timing):
		self.I2CWriteBulk(0x39,[0x80 | 0x01, gain|timing]) #Timing register 0x01. gain[1x,16x] | timing[13mS,100mS,400mS]

	def TSL2561_all(self):
		'''
		returns a 2 element list. total,IR
		returns None if communication timed out with I2C sensor
		'''
		b = self.I2CReadBulk(0x39,0x80 | 0x20 | 0x0C ,4)
		if b is None:return None
		if None not in b:
			return [ (b[x*2+1]<<8)|b[x*2] for x in range(2) ] #total, IR

	def MLX90614_init(self):
		pass

	def MLX90614_all(self):
		'''
		return a single element list.  None if failed
		'''
		vals = self.I2CReadBulk(0x5A, 0x07 ,3)
		if vals is None:return None
		if vals:
			if len(vals)==3:
				return [((((vals[1]&0x007f)<<8)+vals[0])*0.02)-0.01 - 273.15]
			else:
				return None
		else:
			return None

	def MCP4725_init(self):
		pass

	def MCP4725_set(self,val):
		'''
		Set the DAC value. 0 - 4095
		'''
		self.I2CWriteBulk(0x62, [0x40,(val>>4)&0xFF,(val&0xF)<<4])

	####################### HMC5883L MAGNETOMETER ###############

	HMC5883L_ADDRESS = 0x1E
	HMC_CONFA=0x00
	HMC_CONFB=0x01
	HMC_MODE=0x02
	HMC_STATUS=0x09

	#--------CONFA register bits. 0x00-----------
	HMCSamplesToAverage=0
	HMCSamplesToAverage_choices=[1,2,4,8]
	
	HMCDataOutputRate=6
	HMCDataOutputRate_choices=[0.75,1.5,3,7.5,15,30,75]
	
	HMCMeasurementConf=0
	
	#--------CONFB register bits. 0x01-----------
	HMCGainValue = 7 #least sensitive
	HMCGain_choices = [8,7,6,5,4,3,2,1]
	HMCGainScaling=[1370.,1090.,820.,660.,440.,390.,330.,230.]

	def HMC5883L_init(self):
		self.__writeHMCCONFA__()
		self.__writeHMCCONFB__()
		self.I2CWriteBulk(self.HMC5883L_ADDRESS,[self.HMC_MODE,0]) #enable continuous measurement mode

	def __writeHMCCONFB__(self):
		self.I2CWriteBulk(self.HMC5883L_ADDRESS,[self.HMC_CONFB,self.HMCGainValue<<5]) #set gain

	def __writeHMCCONFA__(self):
		self.I2CWriteBulk(self.HMC5883L_ADDRESS,[self.HMC_CONFA,(self.HMCDataOutputRate<<2)|(self.HMCSamplesToAverage<<5)|(self.HMCMeasurementConf)])

	def HMC5883L_getVals(self,addr,bytes):
		vals = self.I2C.readBulk(self.ADDRESS,addr,bytes) 
		return vals
	
	def HMC5883L_all(self):
		vals=self.HMC5883L_getVals(0x03,6)
		if vals:
			if len(vals)==6:
				return [np.int16(vals[a*2]<<8|vals[a*2+1])/self.HMCGainScaling[self.HMCGainValue] for a in range(3)]
			else:
				return False
		else:
			return False

	PCA9685_address = 64
	def PCA9685_init(self):
		prescale_val = int((25000000.0 / 4096 / 60.)  - 1) # default clock at 25MHz
		#self.I2CWriteBulk(self.PCA9685_address, [0x00,0x10]) #MODE 1 , Sleep
		print('clock set to,',prescale_val)
		self.I2CWriteBulk(self.PCA9685_address, [0xFE,prescale_val]) #PRESCALE , prescale value
		self.I2CWriteBulk(self.PCA9685_address, [0x00,0x80]) #MODE 1 , restart
		self.I2CWriteBulk(self.PCA9685_address, [0x01,0x04]) #MODE 2 , Totem Pole
		
		pass

	CH0 = 0x6	 		    #LED0 start register
	CH0_ON_L =  0x6		#channel0 output and brightness control byte 0
	CH0_ON_H =  0x7		#channel0 output and brightness control byte 1
	CH0_OFF_L = 0x8		#channel0 output and brightness control byte 2
	CH0_OFF_H = 0x9		#channel0 output and brightness control byte 3
	CHAN_WIDTH = 4
	def PCA9685_set(self,chan,angle):
		'''
		chan: 1-16
		Set the servo angle for SG90: angle(0 - 180)
		'''
		Min = 180
		Max = 650
		val = int((( Max-Min ) * ( angle/180. ))+Min)
		print(chan,angle,val)
		self.I2CWriteBulk(self.PCA9685_address, [self.CH0_ON_L + self.CHAN_WIDTH * (chan - 1),0]) #
		self.I2CWriteBulk(self.PCA9685_address, [self.CH0_ON_H + self.CHAN_WIDTH * (chan - 1),0]) # Turn on immediately. At 0.
		self.I2CWriteBulk(self.PCA9685_address, [self.CH0_OFF_L + self.CHAN_WIDTH * (chan - 1),val&0xFF]) #Turn off after val width 0-4095
		self.I2CWriteBulk(self.PCA9685_address, [self.CH0_OFF_H + self.CHAN_WIDTH * (chan - 1),(val>>8)&0xFF])




class Expt(QtWidgets.QWidget):
	def __init__(self, device=None):
		QtWidgets.QWidget.__init__(self)
		self.p = device
		self.I2C = device.I2C		#connection to the device hardware 	
		self.sensorList = []
		self.logger = LOGGER(self.I2C)
		right = QtWidgets.QVBoxLayout()							# right side vertical layout
		right.setAlignment(QtCore.Qt.AlignTop)
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
					a[0].setValue(a[0].read())



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
	
