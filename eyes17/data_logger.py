# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
'''
Analog Data logger

'''


import sys, time, math, os.path

import utils
from QtVersion import *

import sys, time, functools
from utils import pg
import numpy as np

from layouts import ui_data_logger

from layouts.gauge import Gauge

try:
	from scipy import optimize
except:
	print('scipy not available')


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
	off = np.average(ya)
	size = len(ya)
	mx = max(ya)
	mn = min(ya)
	amp = (mx-mn)/2
	if freq == 0:						# Guess frequency not given
		freq = find_frequency(xa,ya)
	if freq == None:
		return None

	print ('guess a, freq, ph = ', amp, freq, 0)
	par = [amp, freq, 0, off] # Amp, freq, phase , offset
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



class Expt(QtWidgets.QWidget, ui_data_logger.Ui_Form):
	TIMER = 1 #Every 1 mS
	running = True
	TMAX = 10
	MULTIPLEXER_POSITION=0
	voltmeter=None
	def __init__(self, device=None):
		super(Expt, self).__init__()
		self.setupUi(self)
		self.p = device						# connection to the device hardware 
		self.currentPage = 0
		self.isPaused = False
		self.fields = ['A1','A2','A3','SEN','IN1','CUSTOM_A1']
		self.min = [-16,-16,-3.3,0,0, 0]
		self.max = [16,  16, 3.3,3.3,3.3,14]
		self.cbs = {'A1':self.A1Box,'A2':self.A2Box,'A3':self.A3Box,'SEN':self.SENBox,'IN1':self.IN1Box,'CUSTOM_A1':self.CUSTOMBox}
		pos = 0
		colors = ['#00ffff','#008080','#ff0000','#800000','#ff00ff','#800080','#00FF00','#008000','#ffff00','#808000','#0000ff','#000080','#a0a0a4','#808080','#ffffff','#4000a0']
		labelStyle = {'color': 'rgb(200,250,200)', 'font-size': '12pt'}
		self.graph.setLabel('left','Voltage -->', units='V',**labelStyle)
		self.graph.setLabel('bottom','Time -->', units='S',**labelStyle)
		self.graph.setYRange(-5,5)

		if self.voltmeter is not None:
			self.voltmeter.reconnect(self.p)
		else:
			from layouts.oscilloscope_widget import DIOINPUT
			try:
				self.voltmeter = DIOINPUT(self,self.p,confirmValues = None)
			except Exception as e:
				print('device not found',e)
		#for a,b in zip([self.WGLabel,self.SQ1Label,self.PV1Label,self.PV2Label],['WG','SQ1','PV1','PV2']):
		#	a.clicked.connect(partial(self.voltmeter.launch,b))


		self.valueTable.setHorizontalHeaderLabels(self.fields)
		for a in self.cbs:
			self.cbs[a].setStyleSheet('background-color:%s;'%colors[pos])
			item = QtWidgets.QTableWidgetItem()
			self.valueTable.setItem(0,pos,item)
			item.setText('')
			pos+=1


		self.curves = {};self.curveData={}; self.fitCurves = {}
		self.gauges = {}
		self.datapoints=0
		self.T = 0
		self.time = np.empty(300)
		self.start_time = time.time()
		row = 1; col=1;

		for a,b,c in zip(self.fields,self.min,self.max):
			gauge = Gauge(self,a)
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
			self.gauges[a] = [gauge,b,c] #Name ,min, max value
			
			curve = self.graph.plot(pen=colors[len(self.curves.keys())], connect="finite")
			fitcurve = self.graph.plot(pen=colors[len(self.curves.keys())],width=2, connect="finite")
			self.curves[a] = curve
			self.curveData[a] = np.empty(300)
			self.fitCurves[a] = fitcurve

		self.graph.setRange(xRange=[-5, 0])
		self.region = pg.LinearRegionItem()
		self.region.setBrush([255,0,50,50])
		self.region.setZValue(10)
		for a in self.region.lines: a.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor)); 
		self.graph.addItem(self.region, ignoreBounds=False)
		self.region.setRegion([-3,-.5])
		self.toggled()


		self.startTime = time.time()
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.updateEverything)
		self.timer.start(2)

	def toggled(self):
		for inp in self.fields:
			if self.cbs[inp].isChecked():
				self.curves[inp].setVisible(True)
				self.gauges[inp][0].set_NeedleColor()
				self.gauges[inp][0].set_enable_filled_Polygon()
			else:
				self.curves[inp].setVisible(False)
				self.gauges[inp][0].set_NeedleColor(255,0,0,30)
				self.gauges[inp][0].set_enable_filled_Polygon(False)

	def setSQ1(self, val):
		self.p.set_sqr1(val)

	def offSQ1(self):
		self.p.set_sqr1(-1)

	def pauseLogging(self,v):
		self.isPaused = v
		for inp in self.fields:
			self.fitCurves[inp].setVisible(False)

	def setDuration(self):
		self.graph.setRange(xRange=[-1*int(self.durationBox.value()), 0])
	def setA1Range(self,r):
		r = float(r[:-2])
		self.p.select_range('A1',r)
		self.gauges['A1'][0].set_MinValue(-1*r)
		self.gauges['A1'][0].set_MaxValue(r)
	def setA2Range(self,r):
		r = float(r[:-2])
		self.p.select_range('A2',r)
		self.gauges['A2'][0].set_MinValue(-1*r)
		self.gauges['A2'][0].set_MaxValue(r)

	def setOD1(self,state):
		self.p.set_state(OD1 = state)

	def show_voltmeter(self):
		self.voltmeter.launch('WG')

	def updateEverything(self):
		if self.voltmeter is not None:
			if self.voltmeter.isVisible() and self.voltmeter.type=='input' and self.voltmeter.autoRefresh:
				try:
					v = self.voltmeter.read()
				except Exception as e:
					self.comerr()
					return
				if v is not None:
					self.voltmeter.setValue(v)

		if self.isPaused: return
		if self.datapoints >= self.time.shape[0]-1:
			tmp = self.time
			self.time = np.empty(self.time.shape[0] * 2) #double the size
			self.time[:tmp.shape[0]] = tmp

		pos = 0
		for inp in self.fields:
			if self.cbs[inp].isChecked():
				if inp != 'CUSTOM_A1':
					v = self.p.get_average_voltage(inp,samples=2)
					if inp=='A3':
						try:
							rg = float(self.rgEdit.text())
							v *= (1.+10.e3/rg)
							print(v)
						except Exception as e:
							print(e,v)
				else:
					v = self.p.get_average_voltage('A1',samples=2)
					v = float(self.slopeEdit.text())*v + float(self.offsetEdit.text())

				self.valueTable.item(0,pos).setText('%.3f'%v)
			else:
				v= 0
				self.valueTable.item(0,pos).setText('')
			self.gauges[inp][0].update_value(v)
			
			if self.isPaused: return

			self.T = time.time() - self.start_time
			self.time[self.datapoints] = self.T

			self.curveData[inp][self.datapoints] = v
			if self.datapoints >= self.curveData[inp].shape[0]-1:
				tmp = self.curveData[inp]
				self.curveData[inp] = np.empty(self.curveData[inp].shape[0] * 2) #double the size
				self.curveData[inp][:tmp.shape[0]] = tmp
			self.curves[inp].setData(self.time[:self.datapoints],self.curveData[inp][:self.datapoints])
			self.curves[inp].setPos(-self.T, 0)
			pos+=1
		self.datapoints += 1 #Increment datapoints once per set. it's shared

	def restartLogging(self):
		self.msg(self.tr('Clear Traces and Data'))
		self.graph.setYRange(-5,5)
		self.pauseLogging(False); self.pauseButton.setChecked(False)
		self.setDuration()
		for pos in self.fields:
			self.curves[pos].setData([],[])
			self.datapoints=0
			self.T = 0
			self.curveData[pos] = np.empty(300)
			self.time = np.empty(300)
			self.start_time = time.time()

	def next(self):
		if self.currentPage==1:
			self.currentPage = 0
			self.switcher.setText("Data Logger")
			self.pauseButton.setChecked(False);self.pauseLogging(False)
		else:
			self.currentPage = 1
			self.switcher.setText("Analog Gauge")

		self.monitors.setCurrentIndex(self.currentPage)

	def sineFit(self):
		self.pauseButton.setChecked(True); self.isPaused = True;
		S,E=self.region.getRegion()
		start = (np.abs(self.time[:self.datapoints]- self.T - S)).argmin()
		end = (np.abs(self.time[:self.datapoints]-self.T - E)).argmin()
		print(self.T,start,end,S,E,self.time[start],self.time[end])
		res = 'Amp, Freq, Phase, Offset<br>'
		for a in self.curves:
			if self.cbs[a].isChecked():
				try:
						fa=fit_sine(self.time[start:end],self.curveData[a][start:end])
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
								self.fitCurves[a].setVisible(True)

				except Exception as e:
						res+='--<br>'
						print (e.message)
						pass
		self.msgBox = QtWidgets.QMessageBox(self)
		self.msgBox.setWindowModality(QtCore.Qt.NonModal)
		self.msgBox.setWindowTitle('Sine Fit Results')
		self.msgBox.setText(res)
		self.msgBox.show()

	def dampedSineFit(self):
		self.pauseButton.setChecked(True); self.isPaused = True;
		S,E=self.region.getRegion()
		start = (np.abs(self.time[:self.datapoints]- self.T - S)).argmin()
		end = (np.abs(self.time[:self.datapoints]-self.T - E)).argmin()
		print(self.T,start,end,S,E,self.time[start],self.time[end])
		res = 'Amplitude, Freq, phase, Damping<br>'
		for a in self.curves:
			if self.cbs[a].isChecked():
				try:
						fa=fit_dsine(self.time[start:end],self.curveData[a][start:end])
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
								self.fitCurves[a].setVisible(True)
				except Exception as e:
						res+='--<br>'
						print (e.message)
						pass
		self.msgBox = QtWidgets.QMessageBox(self)
		self.msgBox.setWindowModality(QtCore.Qt.NonModal)
		self.msgBox.setWindowTitle('Damped Sine Fit Results')
		self.msgBox.setText(res)
		self.msgBox.show()




	def updateHandler(self,device):
		if(device.connected):
			self.p = device

	def msg(self, m):
		self.msgwin.setText(self.tr(m))

	def saveTraces(self):
		self.pauseButton.setChecked(True); self.isPaused = True;
		fn = QFileDialog.getSaveFileName(self,"Save file",QtCore.QDir.currentPath(),
        "Text files (*.txt);;CSV files (*.csv);;All files (*.*)", "CSV files (*.csv)")
		if(len(fn)==2): #Tuple
			fn = fn[0]
		print(fn)
		if fn != '':
			f = open(fn,'wt')
			f.write('time')
			for inp in self.fields:
				if self.cbs[inp].isChecked():
					f.write(',%s'%(inp))
			f.write('\n')

			for a in range(self.datapoints):
				f.write('%.3f'%(self.time[a]-self.time[0]))
				for inp in self.fields:
					if self.cbs[inp].isChecked():
						f.write(',%.5f'%(self.curveData[inp][a]))
				f.write('\n')
			f.close()
			self.msg(self.tr('Traces saved to ') + fn)


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
