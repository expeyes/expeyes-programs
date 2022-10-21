# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
import sys, time, math, importlib, os, platform, os.path, metaconfig
from utils import cnf
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot
from PyQt5.QtGui import QIcon
from QtVersion import *
showVersions()


import pyqtgraph as pg

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

"""
The first submenu
"""
QT_TRANSLATE_NOOP('MainWindow','Reconnect')
QT_TRANSLATE_NOOP('MainWindow','LightBackGround next time')
QT_TRANSLATE_NOOP('MainWindow','DarkBackGround next time')
QT_TRANSLATE_NOOP('MainWindow','Choose Language')

"""
Warning dialogs
"""
QT_TRANSLATE_NOOP('MainWindow','No immediate application')
QT_TRANSLATE_NOOP('MainWindow',"Please restart the application to lighten the screen's background")
QT_TRANSLATE_NOOP('MainWindow',"Please restart the application to darken the screen's background.")


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
[QT_TRANSLATE_NOOP('MainWindow','IC555 Multivibrator'),('3.5','osc555')],
[QT_TRANSLATE_NOOP('MainWindow','Logic Gates'),('3.6','logic-gates')]
]

electronicsExpts = [ 
[QT_TRANSLATE_NOOP('MainWindow','Diode Characteristics'),('3.7','diodeIV')],
[QT_TRANSLATE_NOOP('MainWindow','NPN Output Characteristics'),('3.8','npnCEout')]
]


electricalExpts = [ 
[QT_TRANSLATE_NOOP('MainWindow','Plot I-V Curve'),('4.1','plotIV')],
[QT_TRANSLATE_NOOP('MainWindow','RLC Steady state response'),('4.2','RLCsteadystate')],
[QT_TRANSLATE_NOOP('MainWindow','RC Transient response'),('4.3','RCtransient')],
[QT_TRANSLATE_NOOP('MainWindow','RL Transient response'),('4.4','RLtransient')],
[QT_TRANSLATE_NOOP('MainWindow','RLC transient response'),('4.5','RLCtransient')],
[QT_TRANSLATE_NOOP('MainWindow','Electromagnetic Induction'),('4.6','induction')]
]

soundExpts = [
[QT_TRANSLATE_NOOP('MainWindow','Sound beats'), ('5.1','soundBeats')]
]

mechanicsExpts = [
[QT_TRANSLATE_NOOP('MainWindow','Rod Pendulum with Light barrier'), ('6.1','rodPendulum')],
[QT_TRANSLATE_NOOP('MainWindow','Pendulum Wavefrorm'),('6.2','pendulumVelocity')],
[QT_TRANSLATE_NOOP('MainWindow','Driven Pendulum resonance'),('6.3','driven-pendulum')],
[QT_TRANSLATE_NOOP('MainWindow','Gravity by Time of Flight'), ('6.4','tof')]
]

otherExpts = [ 
[QT_TRANSLATE_NOOP('MainWindow','Data Logger'), ('7.1','logger')]
]


class Language:
	def __init__(self, name, finished=True):
		"""
		the constructor
		:param name: the name of the language, for example "de_DE"
		:param finished: boolean stating whether the translation is OK; True by default
		"""
		self.name = name
		self.finished = finished

	def __str__(self):
		if self.finished:
			return self.name
		else:
			return f"{self.name} (experimental)"

	def flag(self, imagePath):
		"""
		:param imagePath: directory containing language flags
		:return: the path to an image if available for this language
		"""
		result=os.path.join(imagePath, f"{self.name}.svg")
		if os.path.exists(result):
			return result
		else:
			return ""

languages = [
	Language('fr_FR'),Language('en_IN'), Language('es_ES', False),
	Language('ml_IN'), Language('ta_IN'),Language('kd_IN', False)]


#---------------------------------------------------------------------
		
class helpWin(QWebView):
		
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

		QWebView.__init__(self)

		self.parent=parent
		self.lang=lang
		helpPath = os.path.join(os.path.dirname(os.path.abspath(__file__)),'helpFiles/')
		fn = helpPath + lang[:2] + '/' + name[1][0] + '.html'

		self.load(QUrl.fromLocalFile(fn))
		self.setWindowTitle(unicode(self.tr('Help: %s')) %name[0])
		#self.setMaximumSize(QSize(500, 1200))
		self.show()
		screen = QDesktopWidget().screenGeometry()
		self.move(screen.width()-self.width()-20, screen.height()-self.height()-60)


class MainWindow(QMainWindow):
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
	
	def closeEvent(self, e):
		if self.hwin != None:
			self.hwin.close()

	def __init__(self, lang, app, tr_eyes, tr_qt):
		"""
		The constructor.
		:param lang: the autodetected language, which comes from shell variables
		:type  lang: str
		:param app: pointer to the Application
		:type  app: QApplication
		:param tr_eyes: translator to localize eyes
		:type  tr_eyes: QTranslator
		:param tr_qt: translator to localize Qt5
		:type  tr_qt: QTranslator
		"""
		QMainWindow.__init__(self)
		self.lang=None # this will be set later, after self.translate() tries
		self.app=app
		self.tr_eyes=tr_eyes
		self.tr_qt=tr_qt

		self.conf = metaconfig.ConfigParser()
		self.conf.read(cnf)
		
		try:
			self.translate(self.conf['ScreenTheme']['language'])
			self.lang = self.conf['ScreenTheme']['language']
		except:
			self.translate(lang)
			self.lang=lang
			
		self.init_UI()
		self.uncheckHelpBox.connect(self.uncheckTheHelpBox)
		#self.setEditorText.connect(self.updateEditor)
		#self.setConfigText.connect(self.updateConfig)

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
		palette = QPalette()								# background color
		palette.setColor(QPalette.Background, QColor(81,188,185)) #("#99ccff")) "#88bbcc"
		self.setPalette(palette)	

		self.helpCB = QCheckBox(self.tr('Enable PopUp Help Window'))
		self.helpCB.stateChanged.connect(self.showHelp)
		#self.helpCB.setStyleSheet('background-color: white')

		self.statusBar = QStatusBar()
		self.setStatusBar(self.statusBar)
		self.statusBar.addWidget(self.helpCB)
		
		self.callExpt(electronicsExptsScope[0])					# Start the scope by default
		self.screen = QDesktopWidget().screenGeometry()
		self.show()
		self.move(20, 20)

	def showCredits(self):
		if self.credwin == None:
			self.credwin = helpWin(self, (self.tr('Credits'),('1.0','Credits')), self.lang)
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
			self.setWindowTitle(unicode(self.tr('Failed to load %s')) %e[0])
		return
		
	def runCode(self, e):
		if self.expName != 'editor': #Moved here from some other non coding expt
			self.hlpName = e
			self.callExpt( ['Python Coding', ('9.0','editor')])
		self.expWidget.mycode = e[1]
		self.expWidget.update()

	def setConfig(self,section, key, value):
		"""
		Sets some part of eyes's configuration
		@param section a section of the configuration file cnf, for
		example: 'ScreenTheme'
		@param key for example: 'Background'
		@param value the text to assign to the key, for example: 'dark'
		"""
		self.conf = metaconfig.ConfigParser()
		self.conf.read(cnf)
		self.conf[section][key] = value
		with open(cnf,"w") as out: self.conf.write(out)
		return
	
	def setWBG(self):
		"""
		sets a light background for the scope's screen
		"""	
		self.setConfig('ScreenTheme', 'Background', 'light')
		QMessageBox.warning(
			self,
			self.tr('No immediate application'),
			self.tr("Please restart the application to lighten the screen's background")
		)
		return
		
	def setBBG(self):
		"""
		sets a dark background for the scope's screen
		"""	
		self.setConfig('ScreenTheme', 'Background', 'dark')
		QMessageBox.warning(
			self,
			self.tr('No immediate application'),
			self.tr("Please restart the application to darken the screen's background.")
		)
		return
	
	def makeMenu(self):
		imagePath = os.path.join(os.path.dirname(
			os.path.abspath(__file__)),'images')
		bar = self.menuBar()
		bar.clear() # reset all menu actions
		mb = bar.addMenu(self.tr("Device"))
		mb.addAction(self.tr('Reconnect'), self.reconnect)
		mb.addAction(self.tr('LightBackGround next time'), self.setWBG)
		mb.addAction(self.tr('DarkBackGround next time'), self.setBBG)
		sm = mb.addMenu(self.tr("Choose Language"))
		sm.setIcon(QIcon(os.path.join(imagePath, "UN_emblem_blue.svg")))
		for e in languages:
			action = sm.addAction(str(e),  lambda item=str(e): self.setLanguage(item))
			flag=e.flag(imagePath)
			if flag:
				action.setIcon(QIcon(flag))
				action.setIconVisibleInMenu(True)
		mb.addAction(self.tr('Credits'), self.showCredits)

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

	def setLanguage(self,l):
			self.setConfig('ScreenTheme', 'language', l)
			self.translators=self.translate(l)
			self.lang=l
			self.init_UI()
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
			if self.expName == 'scope':
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
			QLibraryInfo.location(QLibraryInfo.TranslationsPath))
		self.app.installTranslator(self.tr_qt)
		self.uncheckHelpBox.emit()

def run():
	# Program starts here
	global app,p,eyes
	import eyesjun.eyes as eyes
	p = eyes.open()
	if p != None: 
		p.set_sqr1(-1)
		p.set_voltage(0)
		p.set_state(10,0)  #OD1 to LOW

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

	mw = MainWindow(lang, app, t, t1)
	sys.exit(app.exec_())

if __name__ == '__main__':
	run()
