import sys
from PyQt5 import QtGui, QtCore, QtWidgets

import time
import numpy as np
from layouts import ui_dio_sensor_scope

import pyqtgraph as pg

import numpy as np
import utils

colors = ['#00ffff', '#008080', '#ff0000', '#800000', '#ff00ff', '#800080', '#00FF00', '#008000', '#ffff00',
          '#808000', '#0000ff', '#000080', '#a0a0a4', '#808080', '#ffffff', '#4000a0']


class TableDialog(QtWidgets.QDialog):
    def __init__(self, title, columns, headers):
        super().__init__()
        self.setWindowTitle(title)
        self.rows = 2
        self.columns = columns
        self.headers = headers
        self.setGeometry(100, 100, 700, 300)

        self.initUI()

    def initUI(self):
        self.layout = QtWidgets.QVBoxLayout()

        self.tableWidget = QtWidgets.QTableWidget()
        self.tableWidget.setColumnCount(self.columns)
        self.tableWidget.setHorizontalHeaderLabels(self.headers)
        self.tableWidget.setRowCount(self.rows)
        self.setLayout(self.layout)
        self.layout.addWidget(self.tableWidget)

    def setData(self, row, col, data):
        if row>self.rows:
            self.rows = row
            self.tableWidget.setRowCount(self.rows)
        item = QtWidgets.QTableWidgetItem(data)
        self.tableWidget.setItem(row, col, item)


class DIOSENSORSCOPE(QtWidgets.QDialog, ui_dio_sensor_scope.Ui_Dialog):
    def __init__(self, parent, sensor, addr, dev):
        super(DIOSENSORSCOPE, self).__init__(parent)
        self.fetched_samples = 0
        name = sensor['name']
        self.p = dev
        self.p.I2C.config(1000000)
        self.MAX_SAMPLES = 8000
        self.NP = self.MAX_SAMPLES
        self.TG = 1000
        self.busy = False
        self.start_time = 0
        self.initialize = sensor['init']
        self.address = addr
        self.startscope = sensor['startscope']
        self.fetchscope = sensor['fetchscope']
        self.parameter = 0
        self.parameters = [self.parameter]
        self.neighbours = 0
        self.nosingleshot = True
        self.read = sensor['read']
        self.isPaused = False
        self.setupUi(self)
        self.currentPage = 0
        self.max = sensor.get('max', None)
        self.min = sensor.get('min', None)
        self.fields = sensor.get('fields', None)
        self.widgets = []
        self.buttonframe = None

        # Define some keyboard shortcuts for ease of use
        self.shortcutActions = {}
        self.shortcuts = {"r": self.focusRegion}
        for a in self.shortcuts:
            shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(a), self)
            shortcut.activated.connect(self.shortcuts[a])
            self.shortcutActions[a] = shortcut

        def initbuttonframe():
            if self.buttonframe is None:
                self.buttonframe = QtWidgets.QFrame()
                self.configLayout.addWidget(self.buttonframe)
                self.widgets.append(self.buttonframe)

        for a in sensor.get('config', []):  # Load configuration menus
            widgettype = a.get('widget', 'dropdown')
            if widgettype == 'button':
                l = QtWidgets.QPushButton(a.get('name', 'Button'))
                l.clicked.connect(a.get('function', None))
            elif widgettype == 'spinbox':
                l = QtWidgets.QLabel(a.get('name', ''))
                self.buttonLayout.addWidget(l);
                self.widgets.append(l)
                l = QtWidgets.QSpinBox()
                l.setMinimum(a.get('min', 0))
                l.setMaximum(a.get('max', 100))
                val = a.get('value', 0)
                if 'readbackfunction' in a:
                    val = a.get('readbackfunction')(address=addr)
                l.setValue(val)
                l.valueChanged.connect(a.get('function', None))
            elif widgettype == 'doublespinbox':
                l = QtWidgets.QLabel(a.get('name', ''))
                self.buttonLayout.addWidget(l);
                self.widgets.append(l)
                l = QtWidgets.QDoubleSpinBox()
                l.setMinimum(a.get('min', 0))
                l.setMaximum(a.get('max', 100))
                if 'readbackfunction' in a:
                    val = a.get('readbackfunction')()
                l.setValue(val)
                l.valueChanged.connect(a.get('function', None))
            elif widgettype == 'dropdown':
                l = QtWidgets.QLabel(a.get('name', ''))
                self.buttonLayout.addWidget(l);
                self.widgets.append(l)
                l = QtWidgets.QComboBox()
                l.addItems(a.get('options', []))
                l.currentIndexChanged['int'].connect(a.get('function', None))

            self.buttonLayout.addWidget(l)
            self.widgets.append(l)

        self.graph.setRange(xRange=[0, self.TG * self.NP / 1.e6])
        self.graph.enableAutoRange('y', True)
        self.region = pg.LinearRegionItem()
        self.region.setBrush([255, 0, 50, 50])
        self.region.setZValue(10)
        for a in self.region.lines: a.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor));
        self.graph.addItem(self.region, ignoreBounds=False)
        self.region.setRegion([self.TG * self.NP / 5.e6, self.TG * self.NP / 2.e6])

        self.curve = self.graph.plot(pen=colors[0], connect="finite")
        self.fitcurve = self.graph.plot(pen=colors[0], width=2, connect="finite")

        self.curves = {}
        self.curveData = {}
        self.fitCurves = {}
        self.cbs = {}
        self.gauges = {}
        self.datapoints = 0
        self.T = 0
        self.time = np.empty(self.NP)
        self.values = np.empty(self.NP)
        self.start_time = time.time()
        row = 1
        col = 1
        MAXCOL = 4
        if len(self.fields) >= 6: MAXCOL = 5
        for a, b, c in zip(self.fields, self.min, self.max):
            col += 1
            if col == MAXCOL:
                row += 1
                col = 1
            curve = self.graph.plot(pen=colors[len(self.curves.keys())], connect="finite")
            fitcurve = self.graph.plot(pen=colors[len(self.curves.keys())], width=2, connect="finite")
            self.addLabel(a, colors[len(self.curves.keys())])

            self.curves[a] = curve
            self.curveData[a] = None
            self.fitCurves[a] = fitcurve

        self.timebaseChanged(self.timebaseSlider.value())
        self.setWindowTitle('Sensor : %s' % name)

    def autoScaleY(self):
        self.graph.enableAutoRange('y', True)

    def timebaseChanged(self, t):
        self.TG = t * 1e3 / self.NP
        self.timebaseLabel.setText(f'{self.NP}points/{t}mS | {self.TG}uS/N')
        self.graph.setRange(xRange=[0, t * 1e-3])  # mS to seconds conversion
        self.region.setRegion([self.TG * self.NP / 5.e6, self.TG * self.NP / 2.e6])
        self.busy = False  # Force restart of acquisition

    def addLabel(self, name, color=None):
        item = QtWidgets.QListWidgetItem()
        if color:
            gradient = QtGui.QLinearGradient(0, 0, 120, 10)
            gradient.setColorAt(0.0, QtGui.QColor(color))
            gradient.setColorAt(1.0, QtGui.QColor(255, 255, 150 + 150 * (len(self.parameterList) % 2)))
            brush = QtGui.QBrush(gradient)
            brush.setStyle(QtCore.Qt.LinearGradientPattern)
            item.setBackground(brush)
            brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
            brush.setStyle(QtCore.Qt.SolidPattern)
            item.setForeground(brush)
        item.setText(name)
        self.parameterList.addItem(item)
        return item

    def changeParameter(self, r):
        self.parameter = r
        self.updateParameterLabel()

    def changeNeighbours(self, n):
        self.neighbours = n
        self.updateParameterLabel()

    def updateParameterLabel(self):
        self.parameters = [a for a in
                           range(self.parameter, min(len(self.fields), self.parameter + self.neighbours + 1))]
        self.NP = self.MAX_SAMPLES / (self.neighbours + 1)

        print(self.fields, self.parameters)
        self.parameterLabel.setText(f'Fetch {[self.fields[a] for a in self.parameters]}')
        self.busy = False  # Restart acquisition

    def iterateScope(self):
        chunksize = 250
        if not self.busy:  # initialize the sensor capture routine
            if self.pauseButton.isChecked() and self.nosingleshot:
                return

            self.timebaseChanged(self.timebaseSlider.value())
            self.fitcurve.clear()
            for a in self.fields:
                self.curves[a].clear()
                self.fitCurves[a].clear()
                self.curveData[a] = None
            self.startscope(self.NP, self.TG, self.parameters)  # Start the I2C oscilloscope
            self.start_time = time.time()
            self.fetched_samples = 0
            self.busy = True
            self.nosingleshot = True
        else:  # Fetch data from the sensor capture routine till it is complete
            status, self.time, vals = self.fetchscope()
            if status > 0:
                if status == 2:
                    self.busy = False
                # print( len(vals),self.NP)
                self.datapoints = len(vals[0])
                for a in range(len(vals)):
                    self.curves[self.fields[a + self.parameter]].setData(self.time, vals[a])
                    self.curveData[self.fields[a + self.parameter]] = vals[a]
            elif status == -1:  # Error. restart scope
                self.busy = False

            '''
            elapsed_time = max(0., time.time()-self.start_time-0.1) # 0.1 seconds headstart.
            available_samples = min(self.NP,int(1e6*elapsed_time/self.TG))
            if self.TG<300: # too short acquisition time. retrieve data later.
                if available_samples<self.NP:
                    return
            if available_samples-self.p.fetched_i2c_scope_buffer>chunksize: #chunk size to prevent packet drops
                available_samples = self.p.fetched_i2c_scope_buffer+chunksize

            if available_samples > (self.p.fetched_i2c_scope_buffer+chunksize*.8) or available_samples == self.NP or elapsed_time>0.2:
                print('should have', available_samples, 'out of ',self.NP)
                self.values = self.fetchscope(available_samples)
                self.datapoints = len(self.values)
                self.time = np.linspace(0, 1e-6 * self.TG * self.datapoints, self.datapoints)
                if self.datapoints == self.NP:
                    self.busy = False
                self.curve.setData(self.time, self.values)
            '''

    def restartLogging(self):
        self.nosingleshot = False

    def fft(self):
        self.isPaused = True
        S, E = self.region.getRegion()
        start = (np.abs(self.time[:self.datapoints] - S)).argmin()
        end = (np.abs(self.time[:self.datapoints] - E)).argmin()
        self.pop2 = pg.plot()
        self.pop2.showGrid(x=True, y=True)
        self.pop2.setWindowTitle(self.tr('Frequency Spectrum 2'))
        try:
            row=0
            for cd in self.fields:
                if self.curveData[cd] is None:
                    print(cd, ' not found')
                    row += 1
                    continue
                print('show', cd)
                xa, ya = utils.fft(self.curveData[cd][start:end], self.TG * 1e-3)
                xa *= 1000
                peak = utils.find_peak(ya)
                ypos = np.max(ya)

                curve = self.pop2.plot(pen=colors[row], connect="finite")
                curve.setData(xa, ya)
                self.pop2.setRange(xRange=[0, xa[-1] / 2.])

                txt = pg.TextItem(text=self.tr('Fundamental frequency = %5.1f Hz') % xa[peak], color=colors[row])
                txt.setPos(xa[peak], ypos)
                self.pop2.addItem(txt)
                row+=1

        except Exception as e:
            print(e)

    def focusRegion(self):
        r = self.graph.visibleRange()
        width = r.width()
        self.region.setRegion(
            [self.graph.visibleRange().x() + width / 5, self.graph.visibleRange().x() + 2 * width / 5])

    def sineFit(self):
        self.isPaused = True
        S, E = self.region.getRegion()
        start = (np.abs(self.time[:self.datapoints] - S)).argmin()
        end = (np.abs(self.time[:self.datapoints] - E)).argmin()
        print(self.T, start, end, S, E, self.time[start], self.time[end])
        self.msgBox = TableDialog('Sine Fit Results', 6, ['Name', 'Amp', 'Freq', 'Phase', 'Offset', 'dPhi'])
        self.msgBox.setWindowModality(QtCore.Qt.NonModal)
        try:
            row = 0
            lastPhase = None
            for cd in self.fields:
                self.fitCurves[cd].setVisible(False)
                if self.curveData[cd] is None:
                    continue
                fa = utils.fit_sine(self.time[start:end], self.curveData[cd][start:end])
                if fa is not None:
                    self.msgBox.setData(row, 0, cd)
                    self.msgBox.setData(row, 1, '%5.2f' % abs(fa[0])) #amp
                    self.msgBox.setData(row, 2, '%5.3f Hz' % fa[1]) #freq
                    self.msgBox.setData(row, 3, '%.2f' % fa[2]) #phase
                    self.msgBox.setData(row, 4, '%.1f' % fa[3]) #offset
                    if lastPhase is not None:
                        self.msgBox.setData(row, 5, '%5.2f' % (float(fa[2])-float(lastPhase))) #dPhi
                    lastPhase = fa[2]
                    x = np.linspace(self.time[start], self.time[end], 1000)

                    self.fitCurves[cd].clear()
                    self.fitCurves[cd].setData(x, utils.sine_eval(x, fa))
                    self.fitCurves[cd].setVisible(True)
                    row+=1

        except Exception as e:
            print(e)

        self.msgBox.show()

    def dampedSineFit(self):
        self.isPaused = True;
        S, E = self.region.getRegion()
        start = (np.abs(self.time[:self.datapoints] - S)).argmin()
        end = (np.abs(self.time[:self.datapoints] - E)).argmin()
        print(self.T, start, end, S, E, self.time[start], self.time[end])

        self.msgBox = TableDialog('Damped Sine Fit Results', 5, ['Name', 'Amp', 'Freq', 'Phase', 'Decay'])
        self.msgBox.setWindowModality(QtCore.Qt.NonModal)
        try:
            row = 0
            for cd in self.fields:
                if self.curveData[cd] is None:
                    continue
                fa = utils.fit_dsine(self.time[start:end], self.curveData[cd][start:end])
                if fa is not None:
                    self.msgBox.setData(row, 0, cd)
                    self.msgBox.setData(row, 1, '%5.2f' % abs(fa[0])) #amp
                    self.msgBox.setData(row, 2, '%5.3f Hz' % fa[1]) #freq
                    self.msgBox.setData(row, 3, '%.2f' % fa[2]) #phase
                    self.msgBox.setData(row, 4, '%.3e' % fa[4]) #decay


                    x = np.linspace(self.time[start], self.time[end], 1000)
                    self.fitCurves[cd].clear()
                    self.fitCurves[cd].setData(x, utils.dsine_eval(x, fa))
                    self.fitCurves[cd].setVisible(True)
                    row+=1
        except Exception as e:
            print(e)

        self.msgBox.show()

    def pauseLogging(self, v):
        self.isPaused = v
        for inp in self.fields:
            self.fitCurves[inp].setVisible(False)

    def saveRegion(self):
        self.__saveTraces__(True)

    def saveTraces(self):
        self.__saveTraces__(False)

    def __saveTraces__(self, considerRegion):
        print('saving region' if considerRegion else 'saving all data')
        self.pauseButton.setChecked(True);
        self.isPaused = True;
        fn = QtWidgets.QFileDialog.getSaveFileName(self, "Save file", QtCore.QDir.currentPath(),
                                                   "Text files (*.txt);;CSV files (*.csv);;All files (*.*)",
                                                   "CSV files (*.csv)")
        if (len(fn) == 2):  # Tuple
            fn = fn[0]
        print(fn)

        if fn != '':
            f = open(fn, 'wt')
            f.write('time')
            for inp in self.fields:
                if self.cbs[inp].isChecked():
                    f.write(',%s' % (inp))
            f.write('\n')

            if considerRegion:
                S, E = self.region.getRegion()
                start = (np.abs(self.time[:self.datapoints] - self.T - S)).argmin()
                end = (np.abs(self.time[:self.datapoints] - self.T - E)).argmin()
                print(self.T, start, end, S, E, self.time[start], self.time[end])
                for a in range(start, end):
                    f.write('%.3f' % (self.time[a] - self.time[start]))
                    for inp in self.fields:
                        if self.cbs[inp].isChecked():
                            f.write(',%.3f' % (self.curveData[inp][a]))
                    f.write('\n')

            else:
                for a in range(self.datapoints):
                    f.write('%.3f' % (self.time[a] - self.time[0]))
                    for inp in self.fields:
                        if self.cbs[inp].isChecked():
                            f.write(',%.3f' % (self.curveData[inp][a]))
                    f.write('\n')
            f.close()

    def launch(self):
        if self.initialize is not None:
            self.initialize(address=self.address)
        self.restartLogging()
        self.show()
