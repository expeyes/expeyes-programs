# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
import sys, time, math, os.path

import utils
from QtVersion import *

import sys, time
from utils import pg
import numpy as np
import eyes17.eyemath17 as em
from functools import partial
import json
from layouts import ui_blockly_layout, syntax
from layouts.advancedLoggerTools import LOGGER

class webWin(QWebView):
		
	def closeEvent(self, e):
		"""
		Sends a message to self.parent to tell that the checkbox for
		the help window should be unchecked.
		"""
		print('leaving...')
		return
			
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
		self.p  = self.parent.p
		self.lang=lang
		self.path = os.path.join(self.parent.blocksPath,'samples')


		try:
			from PyQt5.QtWebChannel import QWebChannel
			self.channel = QWebChannel()
			self.handler = self.dataHandler(self.parent)
			self.channel.registerObject('backend', self.handler)
			self.page().setWebChannel(self.channel)

			fn = os.path.join(self.parent.blocksPath , 'webview.html')
			print(fn)

			self.load(QUrl.fromLocalFile(fn))
			self.setWindowTitle(unicode(self.tr('Block Coding: %s')) %fn)


		except Exception as e:
			print(e)


	class dataHandler(QtCore.QObject):
		def __init__(self,parent):
			QMainWindow.__init__(self)
			self.p = parent.p
			self.parent = parent
			self.active_sensors = {}

		@QtCore.pyqtSlot(str, result=float)
		def get_voltage(self,chan):
			return self.p.get_voltage(chan)


		@QtCore.pyqtSlot(result=bool)
		def get_device_status(self):
			print('devstat',self.p.connected)
			return self.p.connected

		@QtCore.pyqtSlot(str)
		def updateCode(self,code):
			code = "import eyes17.eyes as eyes\np = eyes.open()\n\n"+code
			self.parent.editor.setPlainText(code)


		@QtCore.pyqtSlot(str, result=list)
		def loadXMLFile(self,tp):
			return ['''
 <xml xmlns="https://developers.google.com/blockly/xml">
      <block type="controls_repeat_ext" id="Mm^6|oM;+Z@e){tU@H-D" x="16" y="66">
        <value name="TIMES">
          <shadow type="math_number" id="FS)@SW9w!grBo$PN?kc2">
            <field name="NUM">10</field>
          </shadow>
        </value>
        <statement name="DO">
          <block type="wait_seconds" id="r#H-^Lg}:/JeUrdUE[b0">
            <field name="SECONDS">0.1</field>
            <next>
              <block type="cs_print" id="^c7PQB~?I3$6`}cI(YL]">
                <value name="TEXT">
                  <shadow type="text" id="S;Wo(5qr^XD=T+Q!ho1-">
                    <field name="TEXT">abc</field>
                  </shadow>
                  <block type="get_voltage" id="^qjm6WY}9*Q/I{1Yje*]">
                    <field name="CHANNEL">A1</field>
                  </block>
                </value>
                <next>
                  <block type="wait_seconds" id="9#4w,dJu*TuT7P)Ouo+R">
                    <field name="SECONDS">0.1</field>
                  </block>
                </next>
              </block>
            </next>
          </block>
        </statement>
      </block>
    </xml>
			''']


		@QtCore.pyqtSlot(str, str, result=float)
		def get_sensor(self,sensor, param):
			return self.p.get_sensor(sensor, int(param))


class Expt(QtWidgets.QWidget, ui_blockly_layout.Ui_Form):
	def __init__(self, device=None):
		super(Expt, self).__init__()
		self.setupUi(self)
		try:
			self.setStyleSheet(open(os.path.join(os.path.dirname(__file__),"layouts/style.qss"), "r").read())
		except Exception as e:
			print('stylesheet missing. ',e)
		self.p = device						# connection to the device hardware 

		self.blocksPath = os.path.join(os.path.dirname(os.path.abspath(__file__)),'blockly')
		self.web = webWin(self,'block coding')
		self.webLayout.addWidget(self.web)

		self.highlight = syntax.PythonHighlighter(self.editor.document())
		self.editorFont = QtGui.QFont()
		self.editorFont.setPointSize(10)

	def fontPlus(self):
		size = self.editorFont.pointSize()
		if size>40: return
		self.editorFont.setPointSize(size+1)
		self.editor.setFont(self.editorFont)

	def fontMinus(self):
		size = self.editorFont.pointSize()
		if size<5: return
		self.editorFont.setPointSize(size-1)
		self.editor.setFont(self.editorFont)

	def setFont(self,font):
		self.editorFont.setFamily(font)
		self.editor.setFont(self.editorFont)








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
