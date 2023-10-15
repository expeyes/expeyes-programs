# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
import sys, os, os.path, metaconfig

from PyQt5 import QtGui, QtCore, QtWidgets
try:
	from configparser import ConfigParser
except:
	try:
		from ConfigParser import ConfigParser
	except:
		from metaconfig import ConfigParser

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSlider

try:
	from scipy import optimize
except:
	print('scipy not available')


import pyqtgraph as pg

from pyqtgraph.exporters import Exporter
from pyqtgraph.parametertree import Parameter
from pyqtgraph.Qt import QtGui, QtCore, QtSvg
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
            filter = ["*."+bytes(f).decode('utf-8') for f in QtGui.QImageWriter.supportedImageFormats()]
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



# path to the configuration file
cnf = os.path.expanduser("~/.config/seelab3/seelab3.ini")

################ create default configuration if necessary ############
for d in ("~/.config", "~/.config/seelab3"):
	# create a path to the configuration file
	e=os.path.expanduser(d)
	if not os.path.exists(e): os.mkdir(e)
if not os.path.exists(cnf):
	# push a default configuration
	defaultConfiguration="""\
# config file for seelab3
# do not edit by hand, it is managed by the application
[DEFAULT]

[ScreenTheme]
Background = dark
language = en_IN
"""
	with open(cnf,"w") as out: out.write(defaultConfiguration)
#######################################################################

config = ConfigParser()
config.read(cnf)

penCols   = ['y','g','r','m','c']     #pqtgraph pen colors
penCols2  = ['#000000','b','r','m','g']     #pqtgraph pen colors
htmlcols  = ['yellow', 'green', 'red','magenta','cyan']
htmlcols2 = ['black', 'blue', 'red','magenta','cyan']

def makeFitTraceColors():
	config.read(cnf)
	forprint = "dark" not in config['ScreenTheme']['Background']
	pens = []
	if forprint == True:
		pg.setConfigOption('background', (227, 241, 209))
		for p in penCols2:
			x=pg.mkPen(p, width=1, style=Qt.PenStyle(3)) #Qt.DotLine
			pens.append(x)
	else:
		for p in penCols:
			x=pg.mkPen(p, width=1, style=Qt.PenStyle(3)) #Qt.DotLine
			pens.append(x)
	return pens	
		
def makeTraceColors():
	config.read(cnf)
	forprint = "dark" not in config['ScreenTheme']['Background']
	pens = []
	if forprint == True:
		pg.setConfigOption('background', (227, 241, 209))
		for p in penCols2:
			x=pg.mkPen(p, width=2)
			pens.append(x)
	else:
		pg.setConfigOption('background', (0, 0, 0))
		for p in penCols:
			x=pg.mkPen(p, width=1)
			pens.append(x)
	return pens	
	
def makeResultColors():
	config.read(cnf)
	forprint = "dark" not in config['ScreenTheme']['Background']
	if forprint == True:
		return penCols2
	else:
		return penCols
		
def makeHtmlColors():
	config.read(cnf)
	forprint = "dark" not in config['ScreenTheme']['Background']
	if forprint == True:
		return htmlcols2
	else:
		return htmlcols
	


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
