# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
import sys, os, os.path, configparser

from QtVersion import *

import pyqtgraph as pg

# path to the configuration file
cnf = os.path.expanduser("~/.config/eyes17/eyes17.ini")

################ create default configuration if necessary ############
for d in ("~/.config", "~/.config/eyes17"):
	# create a path to the configuration file
	e=os.path.expanduser(d)
	if not os.path.exists(e): os.mkdir(e)
if not os.path.exists(cnf):
	# push a default configuration
	defaultConfiguration="""\
# config file for eyes17
# do not edit by hand, it is managed by the application
[DEFAULT]

[ScreenTheme]
Background = dark
"""
	with open(cnf,"w") as out: out.write(defaultConfiguration)
#######################################################################

config = configparser.ConfigParser()
config.read(cnf)
forprint = "dark" not in config['ScreenTheme']['Background']

penCols   = ['y','g','r','m','c']     #pqtgraph pen colors
penCols2  = ['#000000','b','r','m','g']     #pqtgraph pen colors
htmlcols  = ['yellow', 'green', 'red','magenta','cyan']
htmlcols2 = ['black', 'blue', 'red','magenta','cyan']

def makeFitTraceColors():
	pens = []
	if forprint == True:
		pg.setConfigOption('background', (227, 241, 209))
		for p in penCols2:
			x=pg.mkPen(p, width=1, style=Qt.DotLine)
			pens.append(x)
	else:
		for p in penCols:
			x=pg.mkPen(p, width=1, style=Qt.DotLine)
			pens.append(x)
	return pens	
		
def makeTraceColors():
	pens = []
	if forprint == True:
		pg.setConfigOption('background', (227, 241, 209))
		for p in penCols2:
			x=pg.mkPen(p, width=2)
			pens.append(x)
	else:
		for p in penCols:
			x=pg.mkPen(p, width=1)
			pens.append(x)
	return pens	
	
def makeResultColors():
	if forprint == True:
		return penCols2
	else:
		return penCols
		
def makeHtmlColors():
	if forprint == True:
		return htmlcols2
	else:
		return htmlcols
	

class slider(QSlider):
	def __init__(self, minval, maxval, setval, maxw, cback):
		QSlider.__init__(self,Qt.Horizontal)
		self.setMaximumWidth(maxw)
		self.setMinimum(minval)
		self.setMaximum(maxval)	
		self.setValue(setval)
		self.setSingleStep(1)
		self.setPageStep(1)
		if cback != None: self.valueChanged.connect(cback)
		#self.setStyleSheet("handle: width 10px;")


class sliderVert(QSlider):
	def __init__(self, minval, maxval, setval, maxw, cback):
		QSlider.__init__(self,Qt.Vertical)
		self.setMaximumWidth(maxw)
		self.setMinimum(minval)
		self.setMaximum(maxval)	
		self.setValue(setval)
		self.setSingleStep(1)
		self.setPageStep(1)
		if cback != None: self.valueChanged.connect(cback)

class lineEdit(QLineEdit):
	def __init__(self, width, val, maxsize, cback):
		QLineEdit.__init__(self)
		self.setFixedWidth(width)
		self.setText(unicode(val))
		#self.setValidator(QDoubleValidator(0.9,9.99,2))
		if cback != None: self.textChanged.connect(cback)
		self.setMaxLength(maxsize)
		self.setStyleSheet("border: 1px solid white;")
		

