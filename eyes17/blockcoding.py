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
from layouts import ui_blockly_layout, syntax
from layouts.advancedLoggerTools import LOGGER

from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage


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
		self.mypage = webPage(self)
		self.setPage(self.mypage)


		try:
			from PyQt5.QtWebChannel import QWebChannel
			self.channel = QWebChannel()
			self.handler = self.dataHandler(self.parent)
			self.channel.registerObject('backend', self.handler)

			self.hwhandler = self.HWHandler(self.parent)
			self.channel.registerObject('hwbackend', self.hwhandler)



			self.page().setWebChannel(self.channel)

			fn = os.path.join(self.parent.blocksPath , 'webview.html')

			self.load(QUrl.fromLocalFile(fn))
			self.setWindowTitle(self.tr('Block Coding: %s') %fn)


		except Exception as e:
			print(e)


	class dataHandler(QtCore.QObject):
		def __init__(self,parent):
			QMainWindow.__init__(self)
			self.parent = parent
			self.local_xml  = ''
			self.openFileWriters = {}
			self.MCAST_GRP = '234.0.0.1'
			self.MCAST_PORT = 9999
			self.MULTICAST_TTL = 2
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
			self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.MULTICAST_TTL)

		def setLocalXML(self,fname):
			self.local_xml = open(fname).read()

		@QtCore.pyqtSlot(str)
		def updateCode(self,code):
			code = "import eyes17.eyes as eyes\np = eyes.open()\n\n"+code
			self.parent.editor.setPlainText(code)

		@QtCore.pyqtSlot(str, bool)
		def xmlCode(self,code, bcast):
			if bcast:
				self.sock.sendto(code.encode(), (self.MCAST_GRP, self.MCAST_PORT))

		@QtCore.pyqtSlot()
		def startStepBroadcast(self):
				self.sock.sendto("!+".encode(), (self.MCAST_GRP, self.MCAST_PORT))

		@QtCore.pyqtSlot()
		def offBroadcast(self):
				self.sock.sendto("!-".encode(), (self.MCAST_GRP, self.MCAST_PORT))

		@QtCore.pyqtSlot(str, str)
		def saveXML(self,name, code):
			import shelve
			shelf = shelve.open(name)
			shelf['code'] = code
			shelf.close()
			print('wrote',name)
			

		@QtCore.pyqtSlot()
		def closeFiles(self):
			for a in self.openFileWriters:
				try: a.close()
				except: pass
			self.openFileWriters = {}

		@QtCore.pyqtSlot(str, str)
		def writeToFile(self, fname, data):
			if fname not in self.openFileWriters:
				self.openFileWriters[fname] = open(os.path.join(os.path.expanduser('~'),fname),'wt')
			self.openFileWriters[fname].write(data)


		@QtCore.pyqtSlot(str, str,str,str,str)
		def save_lists(self, fname, x,y1,y2,y3):
			print('not implemented')

		@QtCore.pyqtSlot(str, result=str)
		def loadLocalXML(self,tp):
			print('load local',tp)
			if(tp == 'local_opened_file'):
				return self.local_xml
			import shelve
			shelf = shelve.open(tp)
			return shelf['code']


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


		@QtCore.pyqtSlot(str, str, result=str)
		def fourier_transform(self,xin, yin):
			x = json.loads(xin)
			v = json.loads(yin)
			dt = x[1] - x[0]
			try:	
				xa,ya = em.fft(np.array(v),dt)
				#peak = self.peak_index(xa,ya)
				#ypos = np.max(ya)
				#pop = pg.plot(xa,ya, pen = self.traceCols[ch])
				return json.dumps([xa.tolist(),ya.tolist()])
			except Exception as err:
				print('FFT error:', err)
			return json.dumps([[],[]])


		@QtCore.pyqtSlot(str, str, int, result=float)
		def sine_fit_arrays(self,xa, ya, p):
			x = json.loads(xa)
			y = json.loads(ya)
			try:	
				yfit, fa = em.fit_sine(np.array(x),np.array(y))
				if(p==0):return fa[0]
				elif(p==1):return fa[1]*1000
				elif(p==2):return 180*fa[2]/np.pi
			except Exception as err:
				print('fit_sine error:', err)
			return 0
				
		@QtCore.pyqtSlot(str, str, str, str, int, result=float)
		def sine_fit_two_arrays(self,xa, ya,xa2,ya2, p):
			x = json.loads(xa)
			y = json.loads(ya)
			x2 = json.loads(xa2)
			y2 = json.loads(ya2)
			try:	
				yfit, fa = em.fit_sine(np.array(x),np.array(y))
				yfit2, fa2 = em.fit_sine(np.array(x2),np.array(y2))
				if(p==0): #Amp ratio (Gain)
					if(fa[0]>0):
						return fa2[0]/fa[0]
				elif(p==1): #Freq ratio (X)
					if(fa[1]>0):
						return fa2[1]/fa[1]
				elif(p==2): #Phase difference
					return 180*(fa2[2] - fa[2])/np.pi
			except Exception as err:
				print('fit_sine2 error:', err)
			return 0


	class HWHandler(QtCore.QObject):
		def __init__(self,parent):
			QMainWindow.__init__(self)
			self.p = parent.p
			self.parent = parent
			self.active_sensors = {}

		def updateHandler(self,device):
			self.p = device



		@QtCore.pyqtSlot(str, result=float)
		def get_voltage(self,chan):
			print('get voltage')
			return self.p.get_voltage(chan)

		@QtCore.pyqtSlot(int,str,float)
		def configure_trigger(self,chan , name, voltage):
			print('trigger:',chan, name, voltage)
			self.p.configure_trigger(int(chan), name, float(voltage))


		@QtCore.pyqtSlot(str, int, int, result=str)
		def capture1(self,chan, ns, tg):
			x, y = self.p.capture1(chan, ns, tg)
			return json.dumps([x.tolist(),y.tolist()])
		@QtCore.pyqtSlot(str,int, int , result=str)
		def capture2(self,chan, ns, tg):
			x, y, _, y2 = self.p.capture2( ns, tg , chan)
			return json.dumps([x.tolist(),y.tolist(), y2.tolist()])

		@QtCore.pyqtSlot(str,int, int ,result=str)
		def capture4(self,chan, ns, tg):
			x, y , _, y3, _, y4 = self.p.capture4( ns, tg, chan)
			return json.dumps([x.tolist(),y.tolist(), y2.tolist(), y3.tolist(), y4.tolist()])


		@QtCore.pyqtSlot(str,int, int , str, int, result=str)
		def capture_action(self,chan, ns, tg, action, t):
			x, y = self.p.capture2( ns, tg , chan, action, t)
			return json.dumps([x.tolist(),y.tolist()])





		@QtCore.pyqtSlot(str, float,result=float)
		def set_voltage(self,chan, value):
			if chan=='PV1':
				return self.p.set_pv1(value)
			elif chan=='PV2':
				return self.p.set_pv2(value)

		@QtCore.pyqtSlot(str, str, str, float, result=float)
		def DoublePinEdges(self,cmd, src, dst, timeout):
			edge1 = 'rising' if cmd in ['r2r','r2f'] else 'falling'
			edge2 = 'rising' if cmd in ['f2r','r2r'] else 'falling'
			T1,T2 = self.p.DoublePinEdges(src,dst,edge1,edge2,1,2,timeout,sequential=True) #src,src,rising edges , rising edges, total 2, total 2, 1 second timeout.
			if T2 is not None:
				if T2[0]:return T2[0]
				else: return T2[1]
			else:return -1

		@QtCore.pyqtSlot(str, str, str, float, result=float)
		def SinglePinEdges(self,cmd, src, dst, timeout):
			edge = 'rising' if cmd in ['s2r','c2r'] else 'falling'
			if cmd[0]=='s':   T = self.SinglePinEdges(dst,edge,1,timeout,src=1)
			elif cmd[0]=='c': T = self.SinglePinEdges(dst,edge,1,timeout,src=0)			
			if T is not None:return T[0]
			else:return -1


		@QtCore.pyqtSlot(result=bool)
		def get_device_status(self):
			print(self.p.connected, self.p)
			if self.p != None:
				return self.p.connected
			else: return False

		@QtCore.pyqtSlot()
		def programStarting(self):
			return


		@QtCore.pyqtSlot(str, str, result=float)
		def get_sensor(self,sensor, param):
			return self.p.get_sensor(sensor, int(param))


		@QtCore.pyqtSlot(int)
		def set_sine_amp(self,value):
			self.p.set_sine_amp(value)

		@QtCore.pyqtSlot(str,float)
		def select_range(self,chan,value):
			self.p.select_range(chan,value)


		@QtCore.pyqtSlot(str, float,result=float)
		def set_frequency(self,chan, value):
			if chan=='WG':
				return self.p.set_sine(value)
			elif chan=='SQ1':
				return self.p.set_sq1(value)
			elif chan=='SQ2':
				return self.p.set_sq2(value)

		@QtCore.pyqtSlot(float,result=float)
		def set_sine(self,value):
				return self.p.set_sine(value)

		@QtCore.pyqtSlot(float,float, result=float)
		def set_sqr1(self,value,dc):
				return self.p.set_sqr1(value, dc)

		@QtCore.pyqtSlot(float, float,result=float)
		def set_sqr2(self,value, dc):
				return self.p.set_sqr2(value, dc)


		@QtCore.pyqtSlot(str,float, result=float)
		def get_freq(self,chan, tmt):
			return self.p.get_freq(chan,tmt)

		@QtCore.pyqtSlot(result=float)
		def get_resistance(self):
			return self.p.get_resistance()

		@QtCore.pyqtSlot(result=float)
		def get_capacitance(self):
			return self.p.get_capacitance()

		@QtCore.pyqtSlot(str, bool)
		def set_state(self, channel, value):
			self.p.set_state(**{channel:value})


		@QtCore.pyqtSlot(str, int, float, result=float)
		def multi_r2r(self, channel, edges, timeout):
			return self.p.multi_r2rtime(channel, edges, timeout)



def load_project_structure(startpath, tree):
	"""
	Load Project structure tree
	:param startpath: 
	:param tree: 
	:return: 
	"""
	import os
	from PyQt5.QtWidgets import QTreeWidgetItem
	from PyQt5.QtGui import QIcon
	for element in os.listdir(startpath):
		path_info = startpath + "/" + element
		if os.path.isdir(path_info):
			parent_itm = QTreeWidgetItem(tree, [os.path.basename(element)])
			load_project_structure(path_info, parent_itm)
			parent_itm.setIcon(0, QIcon(os.path.join(startpath,element+'.jpg')) )
		else:
			name = os.path.basename(element)
			if(name.endswith('.jpeg')):
				parent_itm = QTreeWidgetItem(tree, [os.path.basename(element.replace('.jpeg','.xml'))])
				parent_itm.setIcon(0, QIcon(os.path.join(startpath,element)) )
			elif(name.endswith('.xml')):
				parent_itm = QTreeWidgetItem(tree, [os.path.basename(element)])

class Expt(QtWidgets.QWidget, ui_blockly_layout.Ui_Form):
	def __init__(self, device=None):
		super(Expt, self).__init__()
		self.setupUi(self)
		self.samplepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),"blockly/samples") 
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
		
		load_project_structure(self.samplepath,self.directoryBrowser)
	
	def updateHandler(self,device):
		if(device.connected):
			self.p = device
			self.web.updateHandler(device)
			self.web.mypage.runJavaScript("deviceConnected();")
		else:
			self.web.mypage.runJavaScript("deviceDisconnected();")
		
	def showDirectory(self):
		self.directoryBrowser.setVisible(True)

	def loadExample(self, item, col):
		if(not item.text(col).endswith('xml')):
			return
		texts = []

		self.directoryBrowser.setVisible(False)

		while item is not None:
			texts.append(item.text(0))
			item = item.parent()
		texts.reverse()
		path = os.path.join(*texts)
		sample  = os.path.join(self.samplepath,path)
		self.web.setLocalXML(sample)
		self.filenameLabel.setText(path)
		
		self.web.mypage.runJavaScript("loadXML(JSBridge.loadLocalXML('local_opened_file',loadRawXml));")

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
