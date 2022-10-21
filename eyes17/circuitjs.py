# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
import sys, time, math, os.path

import utils
from QtVersion import *

import sys, time, tempfile, json, socket
from utils import pg
import numpy as np
import eyes17.eyemath17 as em
from functools import partial
import json
from layouts import ui_simulator_layout, syntax
from layouts.advancedLoggerTools import LOGGER

from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineSettings


class webPage(QWebEnginePage):
	def __init__(self, *args, **kwargs):
		super(webPage, self).__init__()
		self.featurePermissionRequested.connect(self.onFeaturePermissionRequested)
	def javaScriptConsoleMessage(self,level, msg, line, source):
		print (' \033[4;33m line %d: %s !! %s , %s \033[0m' % ( line, msg, source,level))

	def onFeaturePermissionRequested(self, url, feature):
		print('feature requested',feature)
		if feature in (QWebEnginePage.MediaAudioCapture, 
			QWebEnginePage.MediaVideoCapture, 
			QWebEnginePage.MediaAudioVideoCapture,
			QWebEnginePage.DesktopVideoCapture,
			QWebEnginePage.DesktopAudioVideoCapture):
			self.setFeaturePermission(url, feature, QWebEnginePage.PermissionGrantedByUser)
		else:
			self.setFeaturePermission(url, feature, QWebEnginePage.PermissionDeniedByUser)


	def certificateError(self, certificateError):
		certificateError.isOverridable()
		certificateError.ignoreCertificateError()
		return True


class webWin(QWebView):
	def closeEvent(self, e):
		"""
		Sends a message to self.parent to tell that the checkbox for
		the help window should be unchecked.
		"""
		print('leaving...')
		return
			
	def setLocalXML(self,fname):
		self.handler.setLocalXML(fname)

	def updateHandler(self,device):
		self.p = device
		self.hwhandler.updateHandler(device)

	def __init__(self, parent, name = '', lang="en"):
		"""
		Class for the help window
		:param parent: this is the main window
		:param name: a tuple (title, HTML file indication)
		name[1] can be either a simple string or another iterable. When it is
		a simple string, it means that the file to open is in htm/<name>.html;
		on the contrary, name[1] is a list of file names, without their
		.html suffix, to be searched in a list of directories; the first
		hit during the search defines the file to open.
		:param lang: the desired language
		"""

		QWebView.__init__(self)

		self.parent=parent
		self.p  = parent.p
		self.lang=lang


		plot_view_settings = self.settings()
		plot_view_settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
		plot_view_settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
		plot_view_settings.setUnknownUrlSchemePolicy(QWebEngineSettings.AllowAllUnknownUrlSchemes)
		#plot_view_settings.setAttribute(QWebEngineSettings.DeveloperExtrasEnabled, True)
		plot_view_settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)


		self.mypage = webPage(self)
		self.setPage(self.mypage)


		try:
			from PyQt5.QtWebChannel import QWebChannel

			fn = os.path.join(self.parent.circuitjsPath , 'circuitjs.html')
			self.load(QUrl.fromLocalFile(fn))
			self.setWindowTitle(self.tr('Simulator: %s') %fn)


		except Exception as e:
			print(e)




class Expt(QtWidgets.QWidget, ui_simulator_layout.Ui_Form):
	def __init__(self, device=None):
		super(Expt, self).__init__()
		self.setupUi(self)
		try:
			self.setStyleSheet(open(os.path.join(os.path.dirname(__file__),"layouts/style.qss"), "r").read())
		except Exception as e:
			print('stylesheet missing. ',e)
		self.p = device						# connection to the device hardware 

		self.circuitjsPath = os.path.join(os.path.dirname(os.path.abspath(__file__)),'site')
		self.web = webWin(self,'Circuit Simulator')
		self.webLayout.addWidget(self.web)

	
	def updateHandler(self,device):
		if(device.connected):
			self.p = device
			self.web.updateHandler(device)
			self.web.mypage.runJavaScript("deviceConnected();")
		else:
			self.web.mypage.runJavaScript("deviceDisconnected();")
		








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
