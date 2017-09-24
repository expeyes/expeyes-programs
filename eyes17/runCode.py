import sys, os

from PyQt4.QtGui import QMainWindow, QWidget, QApplication, QTextEdit
from PyQt4.QtCore import QThread, QProcess

class userCode(QThread):

    def __init__(self):
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
		print 'starting code'
		os.system('python code.py')



import sys,inspect

from expeyes import eyes17
p = eyes17.open()


functionList = {}
for a in dir(p):
	attr = getattr(p, a)
	if inspect.ismethod(attr) and a!='__init__':
		functionList[a] = attr


s = '''
from pylab import *
print (get_voltage('A1'))
x,y = capture1('A1',10,10)
plot(x,y)
show()
'''



class Window(QMainWindow):
	def __init__(self):
		super(Window, self).__init__()
		self.setGeometry(50, 50, 800, 600)
		self.setWindowTitle("MicroHOPE")
		self.msgwin = self.statusBar()
		self._processes = []


		bar = self.menuBar()
		mb = bar.addMenu("File")
		mb.addAction('Open', self.file_open)

		bar.addAction('Compile', self.compile)
		bar.addAction('Upload', self.upload)

		self.show()
		self.mytext = QTextEdit()
		self.setCentralWidget(self.mytext)

		self.terminal = QWidget(self)	
		#self.setCentralWidget(self.terminal)
		
		
	def _start_process(self, prog, args):
			child = QProcess()
			self._processes.append(child)
			print child.start(prog, args)

    
	def compile(self):
		#s =str(self.mytext.toPlainText())
		
		submitted = compile(s.encode(), '<string>', mode='exec')
		try:
			exec(submitted, functionList)
		except Exception as e:
			print(str(e))
			
		'''	
		f = open('code.py','w')
		f.write(s)
		f.close()
		os.system("xterm -e python code.py")		
		'''
		
	def upload(self):
		pass
    
	def file_open(self):
		fn = QtGui.QFileDialog.getOpenFileName(self, "", "", "")
		if fn == '': return
		f = open(fn)
		s = f.read()
		self.mytext.setText(s)	

		print self.mytext.toPlainText()
	
		
app = QApplication(sys.argv)
GUI = Window()
sys.exit(app.exec_())
