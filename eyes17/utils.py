import sys, os

PQT5 = False

if PQT5 == True:
	from PyQt5.QtCore import Qt, QT_VERSION_STR
	from PyQt5.QtWidgets import QSlider, QLineEdit
	from PyQt5.QtWebKitWidgets import QWebView
else:
	from PyQt4.QtCore import Qt, QT_VERSION_STR
	from PyQt4.QtGui import QSlider, QLineEdit
	
print("Qt version:", QT_VERSION_STR)

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
		self.setText(str(val))
		#self.setValidator(QDoubleValidator(0.9,9.99,2))
		if cback != None: self.textChanged.connect(cback)
		self.setMaxLength(maxsize)
		

