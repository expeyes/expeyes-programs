import sys, time, math, os.path
import utils

from QtVersion import *

from layouts import ui_browser_layout

electronicsExpts = [ 
[QT_TRANSLATE_NOOP('MainWindow','Diode Characteristics'),('3.13','diodeIV','pics','diode-iv-screen.png')],
[QT_TRANSLATE_NOOP('MainWindow','Logic Gates'),('3.11','logic-gates','pics','ic555-screen.png')],
[QT_TRANSLATE_NOOP('MainWindow','NPN Output Characteristics'),('3.14','npnCEout','pics','transistor-ce-config.png')],
[QT_TRANSLATE_NOOP('MainWindow','RLC Steady state response'),('4.3','RLCsteadystate','pics','RLCsteadystate-screen.png')],
[QT_TRANSLATE_NOOP('MainWindow','RC Transient response'),('4.4','RCtransient','pics','RLCtransient-screen.png')],
[QT_TRANSLATE_NOOP('MainWindow','Fullwave Rectifier'), ('8.9','fullwave','pics','fullwave-filter-screen.png')]
]


class Expt(QtWidgets.QWidget, ui_browser_layout.Ui_Form):
	def __init__(self, device=None):
		super(Expt, self).__init__()
		self.setupUi(self)
		self.thumbList = {}

		self.p = device										# connection to the device hardware 
		for ex in electronicsExpts:
			fname = ex[1][1]
			helpPath = os.path.join(os.path.dirname(os.path.abspath(__file__)),'helpFiles',lang[:2],ex[1][0]+'.html')
			thumbpath = os.path.join(os.path.dirname(os.path.abspath(__file__)),'helpFiles' , lang[:2] ,ex[1][2], ex[1][3])
			print(ex,helpPath)
			x = QtGui.QIcon(thumbpath)
			a = QtGui.QListWidgetItem(x,fname)
			self.listWidget.addItem(a)
			self.thumbList[fname] = [a,helpPath]

		print(self.thumbList)

	def itemDoubleClicked(self,sel):
		fname = self.thumbList[str(sel.text())][1]
		print('2',fname)

	def itemClicked(self,sel):
		fname = self.thumbList[str(sel.text())][1]
		print(fname)

		with open(fname) as f:
				self.comments.setHtml(f.read())


	def msg(self, m):
		self.msgwin.setText(self.tr(m))
		

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
	
