import sys, os

from QtVersion import *

import pyqtgraph as pg

#forprint = True             # Edit this line to change color scheme

try:
	open('white.mode','r')
	forprint = True             # Edit this line to change color scheme
except:
	forprint = False

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
		

