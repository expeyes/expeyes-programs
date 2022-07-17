# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
import sys, time, math, importlib, os, platform, os.path, configparser, csv
from datetime import datetime
from utils import cnf
from language import languages
from server import ScreenShotThread
from PyQt6.QtCore import pyqtSignal, QObject, pyqtSlot, Qt, QTimer
from PyQt6.QtGui import QIcon
from QtVersion import *
showVersions()


### Image export feature
import numpy as np
import pyqtgraph as pg
from pyqtgraph import functions as fn
from pyqtgraph.exporters import Exporter
from pyqtgraph.parametertree import Parameter

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
        bgbrush = scene.views()[0].backgroundBrush()
        #bgbrush = pg.mkBrush('w')
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



pf = platform.platform()
print (pf)	
if 'Windows' in pf:
	import diodeIV, editor, filterCircuit, induction, MPU6050, npnCEout, pendulumVelocity
	import plotIV, pnpCEout, pt100, RCtransient, RLCsteadystate, RLCtransient
	import RLtransient, rodPendulum, scope, soundBeats, soundFreqResp, soundVelocity
	import sr04dist, utils, logger, XYplot, i2cLogger, tof, advanced_logger

"""
Translations in advance for the menus:
the top menu titles
"""

QT_TRANSLATE_NOOP('MainWindow','Device')
QT_TRANSLATE_NOOP('MainWindow','School Expts')
QT_TRANSLATE_NOOP('MainWindow','Electronics')
QT_TRANSLATE_NOOP('MainWindow','Electrical')
QT_TRANSLATE_NOOP('MainWindow','Sound')
QT_TRANSLATE_NOOP('MainWindow','Mechanics')
QT_TRANSLATE_NOOP('MainWindow','Other Expts')
QT_TRANSLATE_NOOP('MainWindow','I2C Modules')
QT_TRANSLATE_NOOP('MainWindow','PythonCode')

"""
The first submenu
"""
QT_TRANSLATE_NOOP('MainWindow','Reconnect')
QT_TRANSLATE_NOOP('MainWindow','LightBackGround')
QT_TRANSLATE_NOOP('MainWindow','DarkBackGround')
QT_TRANSLATE_NOOP('MainWindow','Choose Language')
QT_TRANSLATE_NOOP('MainWindow','Screenshot')
QT_TRANSLATE_NOOP('MainWindow','Whole Window Alt-s')
QT_TRANSLATE_NOOP('MainWindow','Graph Only Alt-p')
QT_TRANSLATE_NOOP('MainWindow','Credits')
QT_TRANSLATE_NOOP('MainWindow','Experiment List')

schoolExpts = [ 
[QT_TRANSLATE_NOOP('MainWindow',"Voltage measurement"), ('2.1','measure-dc')],
[QT_TRANSLATE_NOOP('MainWindow',"Resistance measurement"), ('2.2','res-measure')],
[QT_TRANSLATE_NOOP('MainWindow',"Resistors in Series"), ('2.3','res-series')],
[QT_TRANSLATE_NOOP('MainWindow',"Resistors in Parallel"), ('2.4','res-parallel')],
[QT_TRANSLATE_NOOP('MainWindow',"Capacitance measurement"), ('2.5','cap-measure')],
[QT_TRANSLATE_NOOP('MainWindow',"Capacitors in Series"), ('2.6','cap-series')],
[QT_TRANSLATE_NOOP('MainWindow',"Capacitors in Parallel"), ('2.7','cap-parallel')],
[QT_TRANSLATE_NOOP('MainWindow',"Resistance by Ohm's law"), ('2.8','res-compare')],
[QT_TRANSLATE_NOOP('MainWindow','Direct and Alternating Currents'), ('2.9','ac-dc')],
[QT_TRANSLATE_NOOP('MainWindow','AC mains pickup'), ('2.10','line-pickup')],
[QT_TRANSLATE_NOOP('MainWindow','Separating AC and DC'), ('2.11','acdc-separating')],
[QT_TRANSLATE_NOOP('MainWindow','Conducting Human body'), ('2.12','conducting-human')],
[QT_TRANSLATE_NOOP('MainWindow','Resistance of Human body'), ('2.13','res-body')],
[QT_TRANSLATE_NOOP('MainWindow','Light Dependent Resistor'), ('2.14','ldr')],
[QT_TRANSLATE_NOOP('MainWindow','Lemon Cell'), ('2.15','lemon-cell')],
[QT_TRANSLATE_NOOP('MainWindow','Simple AC generator'), ('2.16','ac-generator')],
[QT_TRANSLATE_NOOP('MainWindow','Transformer'), ('2.17','transformer')],
[QT_TRANSLATE_NOOP('MainWindow','Resistance of Water'), ('2.18','res-water')],
[QT_TRANSLATE_NOOP('MainWindow','Generating Sound'), ('2.19','sound-generator')],
[QT_TRANSLATE_NOOP('MainWindow','Digitizing Sound'), ('2.20','sound-capture')],
[QT_TRANSLATE_NOOP('MainWindow','Stroboscope'), ('2.21','stroboscope')],
]

'''
testEquipment = [ 
[QT_TRANSLATE_NOOP('MainWindow','Oscilloscope'),('3.1', 'scope')]
#[QT_TRANSLATE_NOOP('MainWindow','Monitor and Control'), 'mon-con']
]
'''


electronicsExptsScope = [ 
[QT_TRANSLATE_NOOP('MainWindow','Oscilloscope'),('3.1', 'scope')],
[QT_TRANSLATE_NOOP('MainWindow','Halfwave Rectifier'),('3.2','halfwave')],
[QT_TRANSLATE_NOOP('MainWindow','Fullwave Rectifier'),('3.3','fullwave')],
[QT_TRANSLATE_NOOP('MainWindow','Diode Clipping'),('3.4','clipping')],
[QT_TRANSLATE_NOOP('MainWindow','Diode Clamping'),('3.5','clamping')],
[QT_TRANSLATE_NOOP('MainWindow','IC555 Multivibrator'),('3.6','osc555')],
[QT_TRANSLATE_NOOP('MainWindow','Transistor Amplifier (CE)'),('3.7','npnCEamp')],
[QT_TRANSLATE_NOOP('MainWindow','Inverting Amplifier'),('3.8','opamp-inv')],
[QT_TRANSLATE_NOOP('MainWindow','Non-Inverting Amplifier'),('3.9','opamp-noninv')],
[QT_TRANSLATE_NOOP('MainWindow','Summing Amplifier'),('3.10','opamp-sum')],
[QT_TRANSLATE_NOOP('MainWindow','Logic Gates'),('3.11','logic-gates')],
[QT_TRANSLATE_NOOP('MainWindow','Clock Divider Circuit'),('3.12','clock-divider')]
]

electronicsExpts = [ 
[QT_TRANSLATE_NOOP('MainWindow','Diode Characteristics'),('3.13','diodeIV')],
[QT_TRANSLATE_NOOP('MainWindow','NPN Output Characteristics'),('3.14','npnCEout')],
[QT_TRANSLATE_NOOP('MainWindow','PNP Output Characteristics'),('3.15','pnpCEout')],
#[QT_TRANSLATE_NOOP('MainWindow','AM and FM'), 'amfm']
]


electricalExpts = [ 
[QT_TRANSLATE_NOOP('MainWindow','Plot I-V Curve'),('4.1','plotIV')],
[QT_TRANSLATE_NOOP('MainWindow','XY Plotting'),('4.2','XYplot')],
[QT_TRANSLATE_NOOP('MainWindow','RLC Steady state response'),('4.3','RLCsteadystate')],
[QT_TRANSLATE_NOOP('MainWindow','RC Transient response'),('4.4','RCtransient')],
[QT_TRANSLATE_NOOP('MainWindow','RL Transient response'),('4.5','RLtransient')],
[QT_TRANSLATE_NOOP('MainWindow','RLC transient response'),('4.6','RLCtransient')],
[QT_TRANSLATE_NOOP('MainWindow','Frequency Response of Filter Circuit'),('4.7','filterCircuit')],
[QT_TRANSLATE_NOOP('MainWindow','Electromagnetic Induction'),('4.8','induction')]
]

soundExpts = [
[QT_TRANSLATE_NOOP('MainWindow','Frequency Response of Piezo Buzzer'),('5.1','soundFreqResp')],
[QT_TRANSLATE_NOOP('MainWindow','Velocity of Sound'), ('5.2','soundVelocity')],
[QT_TRANSLATE_NOOP('MainWindow','Sound beats'), ('5.3','soundBeats')]
]

mechanicsExpts = [
[QT_TRANSLATE_NOOP('MainWindow','Rod Pendulum with Light barrier'), ('6.1','rodPendulum')],
[QT_TRANSLATE_NOOP('MainWindow','Pendulum Waveform'),('6.2','pendulumVelocity')],
[QT_TRANSLATE_NOOP('MainWindow','Driven Pendulum resonance'),('6.3','driven-pendulum')],
[QT_TRANSLATE_NOOP('MainWindow','Distance by HY-SRF04 Echo module'), ('6.4','sr04dist')],
[QT_TRANSLATE_NOOP('MainWindow','Gravity by Time of Flight'), ('6.5','tof')]
]

otherExpts = [ 
[QT_TRANSLATE_NOOP('MainWindow','Temperatue, PT100 Sensor'), ('7.1','pt100')],
[QT_TRANSLATE_NOOP('MainWindow','Data Logger'), ('7.2','logger')],
[QT_TRANSLATE_NOOP('MainWindow','Advanced Data Logger'), ('7.3','advanced_logger')]
]

modulesI2C = [ 
[QT_TRANSLATE_NOOP('MainWindow','Magnetic Hysteresis (MPU925x Sensor)'),('8.1', 'BHCurve')],
[QT_TRANSLATE_NOOP('MainWindow','Luminosity(TSL2561) Logger'),('8.2', 'lightsensorlogger')],
[QT_TRANSLATE_NOOP('MainWindow','Temperature(MAX6675) Logger'),('8.5', 'thermocouplelogger')],
[QT_TRANSLATE_NOOP('MainWindow','MPU-6050 Acccn, Velocity and Temp'), ('8.3', 'MPU6050')],
[QT_TRANSLATE_NOOP('MainWindow','General Purpose I2C Sensors'), ('8.4', 'i2cLogger')]
]

pythonCodes = [ 
[QT_TRANSLATE_NOOP('MainWindow','Read Inputs'),  'readInputs'],
[QT_TRANSLATE_NOOP('MainWindow','Set DC Voltages'), 'setVoltages'],
[QT_TRANSLATE_NOOP('MainWindow','Capture Single Input'), 'capture1'],
[QT_TRANSLATE_NOOP('MainWindow','Capture Two Inputs'), 'capture2'],
[QT_TRANSLATE_NOOP('MainWindow','Capture Four Inputs'), 'capture4'],
[QT_TRANSLATE_NOOP('MainWindow','Triangular Waveform'), 'triangularWave'],
[QT_TRANSLATE_NOOP('MainWindow','Arbitrary Waveform'), 'waveforms'],
[QT_TRANSLATE_NOOP('MainWindow','Waveform Table'), 'table'],
[QT_TRANSLATE_NOOP('MainWindow','RC Transient'), 'RCtransient'],
[QT_TRANSLATE_NOOP('MainWindow','RL Transient'), 'RLtransient'],
[QT_TRANSLATE_NOOP('MainWindow','RC Integration'), 'RCintegration'],
[QT_TRANSLATE_NOOP('MainWindow','Clipping with Diode'), 'clipping'],
[QT_TRANSLATE_NOOP('MainWindow','Clamping with Diode'), 'clamping'],
[QT_TRANSLATE_NOOP('MainWindow','Fullwave Rectifier'), 'fullwave'],
[QT_TRANSLATE_NOOP('MainWindow','NPN Ib vs IC plot'), 'npnTransferChar'],
[QT_TRANSLATE_NOOP('MainWindow','Fourier Transform'), 'FourierTransform'],
[QT_TRANSLATE_NOOP('MainWindow','Rod Pendulum'), 'rodpend']
]

#---------------------------------------------------------------------
		
class helpWin(QWebEngineView, QScreen):
		
	def closeEvent(self, e):
		"""
		Sends a message to self.parent to tell that the checkbox for
		the help window should be unchecked.
		"""
		self.parent.uncheckHelpBox.emit()
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

		QWebEngineView.__init__(self)
		QScreen.__init__(self)

		self.parent=parent
		self.lang=lang
		helpPath = os.path.join(os.path.dirname(os.path.abspath(__file__)),'helpFiles/')
		fn = helpPath + lang[:2] + '/' + name[1][0] + '.html'
		print(fn)

		self.load(QUrl.fromLocalFile(fn))
		self.setWindowTitle(self.tr('Help: %s') %name[0])
		#self.setMaximumSize(QSize(500, 1200))
		self.show()
		screen = self.geometry()
		self.move(screen.width()-self.width()-20, screen.height()-self.height()-60)

class MainWindow(QMainWindow,QScreen):
	WIDTH = 950
	HEIGHT = 600
	expWidget = None
	expName = ''
	hlpName = ''
	hwin = None
	credwin = None
	uncheckHelpBox = pyqtSignal()
	setEditorText = pyqtSignal(str)
	setConfigText = pyqtSignal(str)
	translate_screenshot = pyqtSignal()
	screenshot_translated = pyqtSignal(str)
	screenshot_translation_finished = pyqtSignal()
	screenshot_request = pyqtSignal(str, str, str)
	
	def __init__(self, lang, app, tr_eyes, tr_qt):
		"""
		The constructor.
		:param lang: the autodetected language, which comes from shell variables
		:type  lang: str
		:param app: pointer to the Application
		:type  app: QApplication
		:param tr_eyes: translator to localize eyes17
		:type  tr_eyes: QTranslator
		:param tr_qt: translator to localize Qt5
		:type  tr_qt: QTranslator
		"""
		QMainWindow.__init__(self)
		QScreen.__init__(self)
		self.lang=None # this will be set later, after self.translate() tries
		self.app=app
		self.tr_eyes=tr_eyes
		self.tr_qt=tr_qt
		self.title = None # the title is set by self.setExp

		self.conf = configparser.ConfigParser()
		self.conf.read(cnf)
		
		try:
			self.translate(self.conf['ScreenTheme']['language'])
			self.lang = self.conf['ScreenTheme']['language']
		except:
			self.translate(lang)
			self.lang=lang
			
		self.init_UI()
		self.uncheckHelpBox.connect(self.uncheckTheHelpBox)
		self.setEditorText.connect(self.updateEditor)
		self.setConfigText.connect(self.updateConfig)
		self.translate_screenshot.connect(self.translateScreenshotCB)
		self.screenshot_translated.connect(self.screenshotTranslatedCB)
		self.screenshot_translation_finished.connect(self.screenshotTranslationFinishedCB)
		self.screenshot_request.connect(self.screenshotRequestCB)
		self.credwin = None

		self.shortcutActions={}
		self.shortcuts={"Ctrl+R":self.reconnect,'Alt+s':self.screenshot,'Alt+p':self.screenshotPlot}
		for a in self.shortcuts:
			shortcut = QtGui.QShortcut(QtGui.QKeySequence(a), self)
			shortcut.activated.connect(self.shortcuts[a])
			self.shortcutActions[a] = shortcut
		self.screenShotThread = ScreenShotThread(self, port = 45594)
		self.screenShotThread.start()
		return

	def closeEvent(self, event):
		if self.hwin != None:
			self.hwin.close()
		self.screenShotThread.terminate()
		self.screenShotThread.wait()
		event.accept()

	def uncheckTheHelpBox(self):
		"""
		unchecks the help checkbox
		"""
		self.helpCB.setChecked(False)
		return

	def init_UI(self):
		self.makeMenu()
		self.setMinimumSize(self.WIDTH-100, self.HEIGHT-50)
		self.resize(self.WIDTH,self.HEIGHT)
		self._x = 100
		self._y = 10
		palette = QPalette()
		# background color
		palette.setColor(QPalette.ColorRole(10), QColor(81,188,185)) #("#99ccff")) "#88bbcc"
		self.setPalette(palette)	

		self.helpCB = QCheckBox(self.tr('Enable PopUp Help Window'))
		self.helpCB.stateChanged.connect(self.showHelp)
		#self.helpCB.setStyleSheet('background-color: white')

		self.statusBar = QStatusBar()
		self.setStatusBar(self.statusBar)
		self.statusBar.addWidget(self.helpCB)
		
		self.callExpt(electronicsExptsScope[0])					# Start the scope by default
		self.screen = self.geometry()
		self.show()
		self.move(20, 20)
		
	def updateEditor(self,text):
		if self.expName[1] == 'editor':
			text = text.replace('import eyes17.eyes','#import eyes17.eyes')
			text = text.replace('p = eyes17.eyes.open()','#p = eyes17.eyes.open() #Uncomment when running script in standalone mode')
			self.expWidget.Edit.setText(text)
			self.activateWindow()

	def updateConfig(self,text):
		if self.expName[1] == 'advanced_logger':
			self.expWidget.setConfig(text)
			self.activateWindow()

	class editorHandler(QObject):
		def __init__(self,sigEditor,sigConfig):
			QMainWindow.__init__(self)
			self.sigEditor = sigEditor
			self.sigConfig = sigConfig

		@pyqtSlot(str)
		def update(self,value):
			self.sigEditor.emit(value)

		@pyqtSlot(str)
		def config(self,value):
			self.sigConfig.emit(value)


	def showCredits(self):
		if self.credwin == None:
			self.credwin = helpWin(self, (self.tr('Credits'),('1.1','Credits')), self.lang)
		self.credwin.show()

	def showHelp(self):
		if self.helpCB.isChecked() == True:
			if self.hwin == None:
				self.hwin = helpWin(self, (self.title,self.hlpName), self.lang)
				if(self.hlpName[1] in ['editor','advanced_logger']):
					try:
						from PyQt5.QtWebChannel import QWebChannel
						self.channel = QWebChannel()
						self.handler = self.editorHandler(self.setEditorText,self.setConfigText)
						self.channel.registerObject('handler', self.handler)
						self.hwin.page().setWebChannel(self.channel)
						print('online help available')
					except Exception as e:
						print(e)

			self.hwin.show()
		else:
			if self.hwin != None: self.hwin.hide()
	
	
	def scope_help(self,e):
		self.hlpName = e[1]
		if self.expName != 'scope':
			explib = importlib.import_module('scope')
			try:
				if self.expWidget != None:
					self.expWidget.timer.stop()     # Stop the timer loop of current widget			
				self.hwin = None
				self.expWidget= None 			    # Let python delete it
				w = explib.Expt(p) 
				self.setCentralWidget(w)
				self.expWidget = w
				self.expName = 'scope'
			except:
				self.expName = ''
				self.setWindowTitle(self.tr('Failed to load scope'))
		self.setWindowTitle(self.tr(e[0]))
		self.hwin = None
		self.title = e[0]
		self.showHelp()
	

	def callExpt(self, e):
		"""
		:parm: e lst with a title and a HTML file designation; when e[1]
		is not a string, then it is an iterable with possible HTML file names,
		and the last file name may also be a module name.
		"""	
		self.title=e[0] # record the title of the experiments, for snapshots
		module_name =  e[1] if type(e[1]) is str else e[1][-1]
		explib = importlib.import_module(module_name)
		try:
			if self.expWidget != None:
				self.expWidget.timer.stop()	 # Stop the timer loop of current widget			
			self.hwin = None
			self.expWidget= None				 # Let python delete it
			w = explib.Expt(p)
			self.setWindowTitle(self.tr(e[0]))
			self.setCentralWidget(w)
			self.expWidget = w
			self.expName = e[1]
			self.hlpName = e[1]
			self.title = e[0]
			self.showHelp()
		except Exception as err:
			print("Exception:", err)	
			self.expName = ''
			self.setWindowTitle(self.tr('Failed to load %s') %e[0])
		return
		
	def runCode(self, e):
		if self.expName != 'editor': #Moved here from some other non coding expt
			self.hlpName = e
			self.callExpt( ['Python Coding', ('9.0','editor')])
		self.expWidget.mycode = e[1]
		self.expWidget.update()

	def setConfig(self,section, key, value):
		"""
		Sets some part of eyes17's configuration
		@param section a section of the configuration file cnf, for
		example: 'ScreenTheme'
		@param key for example: 'Background'
		@param value the text to assign to the key, for example: 'dark'
		"""
		self.conf = configparser.ConfigParser()
		self.conf.read(cnf)
		self.conf[section][key] = value
		with open(cnf,"w") as out: self.conf.write(out)
		return
	
	def setWBG(self):
		"""
		sets a light background for the scope's screen
		"""	
		self.setConfig('ScreenTheme', 'Background', 'light')
		self.conf.read(cnf)
		self.callExpt(electronicsExptsScope[0])	# Start the scope by default
		return
		
	def setBBG(self):
		"""
		sets a dark background for the scope's screen
		"""	
		self.setConfig('ScreenTheme', 'Background', 'dark')
		self.conf.read(cnf)
		self.callExpt(electronicsExptsScope[0])	 # Start the scope by default
		return
	
	def makeMenu(self):
		imagePath = os.path.join(os.path.dirname(
			os.path.abspath(__file__)),'images')
		bar = self.menuBar()
		bar.clear() # reset all menu actions
		mb = bar.addMenu(self.tr("Device"))
		mb.addAction(self.tr('Reconnect'), self.reconnect)
		mb.addAction(self.tr('LightBackGround'), self.setWBG)
		mb.addAction(self.tr('DarkBackGround'), self.setBBG)
		sm = mb.addMenu(self.tr("Choose Language"))
		sm.setIcon(QIcon(os.path.join(imagePath, "UN_emblem_blue.svg")))
		translationProgress=csv.DictReader(
			open(os.path.join(os.path.dirname(__file__),"lang/status.txt")),
			delimiter=",",
			fieldnames=('ident','finished','unfinished','ignored'),
		)
		translationProgress=list(translationProgress)
		for e in languages:
			action = sm.addAction(f"{e.name} ({e.localName})",  lambda item=e.ident: self.setLanguage(item))
			flag=e.flag(imagePath)
			# if flag exists, append localisation status underneath
			# else display only localisation status
			if flag:
				action.setIcon(QIcon(flag))
				action.setIconVisibleInMenu(True)
				prog = [tp for tp in translationProgress if e.ident[:2] == tp["ident"]]
				if prog:
					prog = prog[0]
					tip = self.tr('Language = {} : done = {}, to finish = {}, untranslated = {}')
					tip = tip.format(prog["ident"], prog["finished"], prog["unfinished"], prog["ignored"])
				action.setStatusTip(tip + ". To contribute to the translation, please contact the authors.")
				action.setToolTip(tip)
		sm = mb.addMenu(self.tr('Screenshot'))
		action = sm.addAction(self.tr('Whole Window Alt-s'),  self.screenshot)
		action = sm.addAction(self.tr('Graph Only Alt-p'),  self.screenshotPlot)
		mb.addAction(self.tr('Credits'), self.showCredits)
		mb.addAction(self.tr('Experiment List'), lambda item=('2.99','experiment-list'): self.callExpt(item))
		mb.addSeparator()

		mb.addSeparator()
		mb.addAction(self.tr('Quit'), self.close)

		em = bar.addMenu(self.tr("School Expts"))
		for e in schoolExpts:
			em.addAction(self.tr(e[0]),  lambda item=e: self.scope_help(item))	

		em = bar.addMenu(self.tr("Electronics"))
		for e in electronicsExptsScope:
			em.addAction(self.tr(e[0]),  lambda item=e: self.scope_help(item))	
			
		for e in electronicsExpts:
			em.addAction(self.tr(e[0]),  lambda item=e: self.callExpt(item))	
		
		em = bar.addMenu(self.tr("Electrical"))
		for e in electricalExpts:
			em.addAction(self.tr(e[0]),  lambda item=e: self.callExpt(item))	

		em = bar.addMenu(self.tr("Sound"))
		for e in soundExpts:
			em.addAction(self.tr(e[0]),  lambda item=e: self.callExpt(item))	

		em = bar.addMenu(self.tr("Mechanics"))
		for e in mechanicsExpts:
			em.addAction(self.tr(e[0]),  lambda item=e: self.callExpt(item))	

		em = bar.addMenu(self.tr("Other Expts"))
		for e in otherExpts:
			em.addAction(self.tr(e[0]),  lambda item=e: self.callExpt(item))	

		em = bar.addMenu(self.tr("I2C Modules"))
		for e in modulesI2C:
			em.addAction(self.tr(e[0]),  lambda item=e: self.callExpt(item))	

		em = bar.addMenu(self.tr("PythonCode"))
		for e in pythonCodes:
			em.addAction(self.tr(e[0]),  lambda item=e: self.runCode(item))	

	def setLanguage(self,l):
		self.setConfig('ScreenTheme', 'language', l)
		self.translators=self.translate(l)
		self.lang=l
		self.init_UI()
		return

	def safeFileName(self, candidate, ext):
		"""
		Build a safe flie name from a candidate string
		:param candidate: a string which can contain spaces, accented chars, etc.
		:param ext: the extension of the file name
		:returns: a safe ASCII file name
		"""
		result=""
		for c in candidate:
			if ord(c) in set(range(48,58)).union(set(range(65,91))).union(set(range(97,123))) or c == "-":
				result += c
			else:
				result += "_"
		return result+"."+ext
		
	def screenshot(self, tmpFileName=None):
		"""
		Create a full screenshot
		:param tmpFileName: when this parameter is a path, it will be
		  the name of the output file; no attempt of translation
		  will be made
		"""
		from screenshots.printableSVG import fixNonScalingStroke
		threadCalling = bool(tmpFileName)
		try:
			if not threadCalling:
				#Timers cannot be stopped from another thread
				self.expWidget.timer.stop()
		except:
			pass

		try:
			screenShotDir = self.conf['DEFAULT']['ScreenShotDir']	
		except:
			screenShotDir = '~/'
		bw = self.conf['ScreenTheme']['BackGround']
		screenShotPath=os.path.join(screenShotDir, self.safeFileName(self.title+"-screen-"+bw, 'svg').lower())
		path=""
		if not tmpFileName:
			# ask interactively for a path if an automatic temporary file
			# name is not set
			path, _filter  = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', screenShotPath, 'SVG(*.svg)')
		if path or tmpFileName:
			self.setConfig('DEFAULT', 'ScreenShotDir', os.path.dirname(path))
			self.conf.read(cnf)
			generator = QtSvg.QSvgGenerator()
			if path[-4:] != '.svg':
				path+='.svg'
			if tmpFileName:
				path = tmpFileName
			generator.setFileName(path)
			target_rect = QtCore.QRectF(0, 0, 800, 600)
			generator.setSize(target_rect.size().toSize())#self.size())
			generator.setViewBox(self.rect())
			d=datetime.now()
			generator.setTitle(d.strftime("ExpEYES 17 Screenshot--%Y-%m-%d--%H-%M"))
			generator.setDescription(self.title)
			p = QtGui.QPainter()
			p.begin(generator)
			self.render(p)
			p.end()
			# fix the width of oscilloscope's traces, for SVG readers which
			# do not honor the attribute 'vector-effect = "non-scaling-stroke"'
			fixNonScalingStroke(path)

		try:
			if not threadCalling:
				#Timers cannot be started from another thread
				self.expWidget.timer.start(self.expWidget.TIMER)
		except:
			pass
		
		if tmpFileName:
			return

		# if the language is currently English, it is possible to
		# translate the screenshot in various languages
		if self.lang[:2] == "en" and path:
			self.translateScreenshot(path)

	def translateScreenshot(self, path):
		"""
		Generate translations of a screen shot
		BONUS: if the screen shot is in dark screen mode, creates also
		SVG files for print usage, with light colors.
		:param path: the path to a svg file
		"""
		try:
			translate_svg_path = self.conf['DEFAULT']['translate_svg_path']
			supported_languages = self.conf['DEFAULT']['supported_languages']
		except:
			translate_svg_path = os.path.join(
				os.path.dirname(path), "screen", "{lang}", "{filename}"
			)
			supported_languages = "en,es,fr,ml"
		from translate_svg import translateDialog
		from PyQt5.QtSvg import QSvgWidget
		from PyQt5.QtWidgets import QVBoxLayout, QDialog, QCheckBox
		d = translateDialog(self)
		d.buttonBox.helpRequested.connect(self.translateScreenshotHelp)
		svg=QSvgWidget(path)
		d.imgFrame.setLayout(QVBoxLayout())
		d.imgFrame.layout().addWidget(svg)
		d.pathEdit.setText(translate_svg_path)
		d.langEdit.setText(supported_languages)
		width = int(self.conf['DEFAULT'].get('pngWidth', "400"))
		d.widthSpinBox.setValue(width)
		ok = d.exec_()
		if ok:
			self.translate_svg_path = d.pathEdit.text()
			supported_languages = d.langEdit.text()
			pngWanted=False
			if d.widthCheckBox.isChecked():
				pngWanted=True
				self.PNGwidth = d.widthSpinBox.value()
				self.setConfig('DEFAULT', 'pngWidth', str(self.PNGwidth))
			self.setConfig('DEFAULT', 'translate_svg_path', self.translate_svg_path)
			self.setConfig('DEFAULT', 'supported_languages', supported_languages)
			self.conf.read(cnf)
			self.targetLanguages = [l.strip() for l in supported_languages.split(",")]
			self.sourceSVGpath = path
			self.exportScreenshotBox = QDialog()
			self.exportScreenshotBox.setWindowTitle(self.tr("Translating ..."))
			self.translatedBoxes={}
			vl = QVBoxLayout()
			for e in languages:
				lang = e.ident[:2]
				if lang not in self.targetLanguages:
					continue
				cb = QCheckBox(self.tr("Export screenshot in {name} ({localname}).").format(name=e.name, localname=e.localName))
				self.translatedBoxes[lang] = cb
				vl.addWidget(cb)
			self.exportScreenshotBox.setLayout(vl)
			self.exportScreenshotBox.setModal(False)
			self.exportScreenshotBox.show()
			QTimer.singleShot(50, self.translate_screenshot)
		return

	@pyqtSlot()
	def translateScreenshotCB(self):
		"""
		callback function to translate screenshots.
		"""
		from translate_thread import TranslateThread
		t = TranslateThread(self)
		t.start()
		return
	
	@pyqtSlot(str)
	def screenshotTranslatedCB(self, lang):
		"""
		Callback function to indicate the end of the translation
		of a screenshot
		"""
		self.translatedBoxes[lang].setChecked(True)
		return
		
	@pyqtSlot()
	def screenshotTranslationFinishedCB(self):
		"""
		Callback function to indicate the end of the translation
		of a screenshot
		"""
		QTimer.singleShot(1000, self.exportScreenshotBox.close)
		return
	
	@pyqtSlot()
	def screenshotRequestCB(self, format, width, shot):
		"""
		Callback to reply a signal created by the web service's thread
		to make a screenshot, and feed it into a BytesIO. When this 
		callback finishes, if fires a signal in the thread to serve the
		result with suitable HTTP headers.
		"""
		
	def translateScreenshotHelp(self):
		"""
		callback function for the help button of screenshot
		translation dialog.
		"""
		# this message is not translated, since it appears
		# only when self.lang is set for English language
		QtWidgets.QMessageBox.warning(self, 
		  'Translate screenshots', 
		  """\
This feature is for developers. 
When English language is chosen, the programe Eyes17
can output localized screenshots for a list of 
languages. The path used to save files is specified 
in a Python-specific way {lang} refers to a language 
string, {filename} is the name of the SVG file which 
will be translated. Do not modify those special templates.

You can customize the way they are used to build the path."""
		)
		return
		
	def screenshotPlot(self, tmpFileName=None):
		"""
		Create a screenshot with the display only
		:param tmpFileName: when this parameter is a path, it will be
		  the name of the output file; no attempt of translation
		  will be made
		"""
		from screenshots.printableSVG import fixNonScalingStroke
		try:
			plt = self.expWidget.pwin
		except Exception as e:
			QtWidgets.QMessageBox.warning(self, self.tr('Missing Plot'), self.tr('Unable to locate a plot. Please try to right click and export'))
			print(' no plot found ',e)
			return

		threadCalling = bool(tmpFileName)
		try:
			if not threadCalling:
				#Timers cannot be stopped from another thread
				self.expWidget.timer.stop()
		except:
			pass

		try:
			ScreenShotDir = self.conf['DEFAULT']['ScreenShotDir']	
		except:
			ScreenShotDir = '~/'
		bw = self.conf['ScreenTheme']['BackGround']
		ScreenShotPath=os.path.join(ScreenShotDir, self.safeFileName(self.title+"-small-screen-"+bw, 'svg').lower())			
		path=""
		if not tmpFileName:
			# ask interactively for a path if an automatic temporary file
			# name is not set
			path, _filter  = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', ScreenShotPath, 'SVG(*.svg);;PNG(*.png)')
		if path or tmpFileName:
			self.setConfig('DEFAULT', 'ScreenShotDir', os.path.dirname(path))
			self.conf.read(cnf)
			#check if file extension is svg or png
			if path[-4:] not in ['.svg','.png'] :
				path+='.svg'
			if tmpFileName:
				path = tmpFileName
			if path[-4:] == '.png':
				ex = PQG_ImageExporter(plt.scene())#plotItem)
				ex.parameters()['width'] = 600 #Default export width is 600px
				val,ok = QtWidgets.QInputDialog.getInt(self,"Set Width", self.tr('Enter Width(px). Height will be autoset'),800,50,4000)
				if ok :
					ex.parameters()['width'] = val # Override with user conf
				ex.export(path)

			elif threadCalling or path[-4:] == '.svg':
				generator = QtSvg.QSvgGenerator()
				generator.setFileName(path)
				target_rect = QtCore.QRectF(0, 0, 800, 600)
				generator.setSize(target_rect.size().toSize())#self.size())
				generator.setViewBox(plt.rect())
				d=datetime.now()
				generator.setTitle(d.strftime("ExpEYES 17 Smaller Screenshot--%Y-%m-%d--%H-%M"))
				generator.setDescription(self.title)
				p = QtGui.QPainter()
				p.begin(generator)
				self.render(p)
				p.end()
				# fix the width of oscilloscope's traces, for SVG readers which
				# do not honor the attribute 'vector-effect = "non-scaling-stroke"'
				fixNonScalingStroke(path)

				if tmpFileName:
					return
				
				# if the language is currently English, it is possible to
				# translate the screenshot in various languages
				if self.lang[:2] == "en" and path:
					self.translateScreenshot(path)

		try:
			if not threadCalling:
				#Timers cannot be started from another thread
				self.expWidget.timer.start(self.expWidget.TIMER)
		except:
			pass
		
		return

	def reconnect(self):
		global p,eyes
		try:
			p.H.disconnect()
		except:
			pass
		p=eyes.open()
		if self.expWidget is None:
			explib = importlib.import_module('scope')
			self.expWidget = explib.Expt(p) 
			self.setCentralWidget(self.expWidget)
			self.setWindowTitle(self.tr('Oscilloscope'))
			self.expName = 'scope'

		self.expWidget.p = p
		self.expWidget.msg('')
		if p != None: 
			print('recovering...',self.expName)
			if self.expName == ('3.1','scope'):
				self.expWidget.recover()
		
	# translation stuff
	def translate(self, lang = None):
		try:
			self.app.removeTranslator(self.tr_eyes)
			self.app.removeTranslator(self.tr_qt)
		except:
			pass

		if lang is None:
			lang=QLocale.system().name()
		self.tr_eyes=QTranslator()
		self.tr_eyes.load("lang/"+lang, os.path.dirname(__file__))
		self.app.installTranslator(self.tr_eyes)
		self.tr_qt=QTranslator()
		self.tr_qt.load("qt_"+lang,
					QLibraryInfo.path(QLibraryInfo.LibraryPath(10))) # 10 = QLibraryInfo.TranslationsPath
		self.app.installTranslator(self.tr_qt)
		self.uncheckHelpBox.emit()

def run():
	# Program starts here
	global app,p,eyes
	import eyes17.eyes as eyes
	p = eyes.open()
	if p != None: 
		p.set_sine(1000)
		p.set_sqr1(-1)
		p.set_pv1(0)
		p.set_pv2(0)
		p.set_state(OD1=0)
		print('Version:',p.version_number)

	app = QApplication(sys.argv)
	# translation stuff
	lang=QLocale.system().name()
	t=QTranslator()
	t.load("lang/"+lang, os.path.dirname(__file__))
	app.installTranslator(t)
	t1=QTranslator()
	t1.load("qt_"+lang,
		QLibraryInfo.path(QLibraryInfo.LibraryPath(10))) # 10 = QLibraryInfo.TranslationsPath
	app.installTranslator(t1)

	mw = MainWindow(lang, app, t, t1)
	sys.exit(app.exec())

if __name__ == '__main__':
	run()
