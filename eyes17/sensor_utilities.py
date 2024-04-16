import sys
from PyQt5 import QtGui, QtCore, QtWidgets

import time, os, os.path
import numpy as np
from layouts import ui_dio_sensor,ui_dio_control,ui_dio_robot, ui_sensor_row, ui_sensor_logger, ui_dio_sensor_scope

from layouts.gauge import Gauge
import functools
from functools import partial
import pyqtgraph as pg

import numpy as np
import utils
from collections import OrderedDict

colors = ['#00ffff', '#008080', '#ff0000', '#800000', '#ff00ff', '#800080', '#00FF00', '#008000', '#ffff00',
          '#808000', '#0000ff', '#000080', '#a0a0a4', '#808080', '#ffffff', '#4000a0']


########### I2C : SENSOR AND CONTROL LAYOUTS ##################


class DIOSENSOR(QtWidgets.QDialog, ui_dio_sensor.Ui_Dialog):
    def __init__(self, parent, sensor, addr):
        super(DIOSENSOR, self).__init__(parent)
        name = sensor['name']
        self.initialize = sensor['init']
        self.address = addr
        self.read = sensor['read']
        self.isPaused = False
        self.setupUi(self)
        colors = ['#00ffff', '#008080', '#ff0000', '#800000', '#ff00ff', '#800080', '#00FF00', '#008000', '#ffff00',
                  '#808000', '#0000ff', '#000080', '#a0a0a4', '#808080', '#ffffff', '#4000a0']
        self.currentPage = 0
        self.max = sensor.get('max', None)
        self.min = sensor.get('min', None)
        self.fields = sensor.get('fields', None)
        self.widgets = []
        self.buttonframe = None

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

        self.graph.setRange(xRange=[-5, 0])
        import pyqtgraph as pg
        self.region = pg.LinearRegionItem()
        self.region.setBrush([255, 0, 50, 50])
        self.region.setZValue(10)
        for a in self.region.lines: a.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor));
        self.graph.addItem(self.region, ignoreBounds=False)
        self.region.setRegion([-3, -.5])

        self.curves = {};
        self.curveData = {};
        self.fitCurves = {}
        self.cbs = {}
        self.gauges = {}
        self.datapoints = 0
        self.T = 0
        self.time = np.empty(300)
        self.start_time = time.time()
        row = 1;
        col = 1;
        MAXCOL = 4;
        if len(self.fields) >= 6: MAXCOL = 5
        for a, b, c in zip(self.fields, self.min, self.max):
            gauge = Gauge(self, a)
            gauge.setObjectName(a)
            gauge.set_MinValue(b)
            gauge.set_MaxValue(c)
            # listItem = QtWidgets.QListWidgetItem()
            # self.listWidget.addItem(listItem)
            # self.listWidget.setItemWidget(listItem, gauge)
            self.gaugeLayout.addWidget(gauge, row, col)
            col += 1
            if col == MAXCOL:
                row += 1
                col = 1
            self.gauges[a] = [gauge, a, b, c]  # Name ,min, max value

            curve = self.graph.plot(pen=colors[len(self.curves.keys())], connect="finite")
            fitcurve = self.graph.plot(pen=colors[len(self.curves.keys())], width=2, connect="finite")
            cbs = QtWidgets.QCheckBox(a)
            cbs.setStyleSheet('background-color:%s;' % (colors[len(self.curves.keys())]))
            self.parameterLayout.addWidget(cbs)
            cbs.setChecked(True)
            cbs.clicked.connect(self.toggled)

            self.curves[a] = curve
            self.curveData[a] = np.empty(300)
            self.fitCurves[a] = fitcurve
            self.cbs[a] = cbs

        self.setWindowTitle('Sensor : %s' % name)

    def toggled(self):
        for inp in self.fields:
            if self.cbs[inp].isChecked():
                self.curves[inp].setVisible(True)
                self.gauges[inp][0].set_NeedleColor()
                self.gauges[inp][0].set_enable_filled_Polygon()
            else:
                self.curves[inp].setVisible(False)
                self.gauges[inp][0].set_NeedleColor(255, 0, 0, 30)
                self.gauges[inp][0].set_enable_filled_Polygon(False)

    def setDuration(self):
        self.graph.setRange(xRange=[-1 * int(self.durationBox.value()), 0])

    def next(self):
        if self.currentPage == 1:
            self.currentPage = 0
            self.switcher.setText("Data Logger")
        else:
            self.currentPage = 1
            self.switcher.setText("Analog Gauge")

        self.monitors.setCurrentIndex(self.currentPage)

    def restartLogging(self):
        self.pauseLogging(False);
        self.pauseButton.setChecked(False)
        self.setDuration()
        for pos in self.fields:
            self.curves[pos].setData([], [])
            self.datapoints = 0
            self.T = 0
            self.curveData[pos] = np.empty(300)
            self.time = np.empty(300)
            self.start_time = time.time()

    def readValues(self):
        return self.read()

    def setValue(self, vals):
        if vals is None:
            print('check connections')
            return
        if self.currentPage == 0:  # Update Analog Gauges
            p = 0
            for a in self.fields:
                if (self.cbs[a].isChecked()):
                    self.gauges[a][0].update_value(vals[p])
                p += 1
        elif self.currentPage == 1:  # Update Data Logger
            if self.isPaused: return
            p = 0
            self.T = time.time() - self.start_time
            self.time[self.datapoints] = self.T
            if self.datapoints >= self.time.shape[0] - 1:
                tmp = self.time
                self.time = np.empty(self.time.shape[0] * 2)  # double the size
                self.time[:tmp.shape[0]] = tmp

            for a in self.fields:
                self.curveData[a][self.datapoints] = vals[p]
                if not p: self.datapoints += 1  # Increment datapoints once per set. it's shared

                if self.datapoints >= self.curveData[a].shape[0] - 1:
                    tmp = self.curveData[a]
                    self.curveData[a] = np.empty(self.curveData[a].shape[0] * 2)  # double the size
                    self.curveData[a][:tmp.shape[0]] = tmp
                self.curves[a].setData(self.time[:self.datapoints], self.curveData[a][:self.datapoints])
                self.curves[a].setPos(-self.T, 0)
                p += 1

    def sineFit(self):
        self.pauseButton.setChecked(True);
        self.isPaused = True;
        S, E = self.region.getRegion()
        start = (np.abs(self.time[:self.datapoints] - self.T - S)).argmin()
        end = (np.abs(self.time[:self.datapoints] - self.T - E)).argmin()
        print(self.T, start, end, S, E, self.time[start], self.time[end])
        res = 'Amp, Freq, Phase, Offset<br>'
        for a in self.curves:
            if self.cbs[a].isChecked():
                try:
                    fa = utils.fit_sine(self.time[start:end], self.curveData[a][start:end])
                    if fa is not None:
                        amp = abs(fa[0])
                        freq = fa[1]
                        phase = fa[2]
                        offset = fa[3]
                        s = '%5.2f , %5.3f Hz, %.2f, %.1f<br>' % (amp, freq, phase, offset)
                        res += s
                        x = np.linspace(self.time[start], self.time[end], 1000)
                        self.fitCurves[a].clear()
                        self.fitCurves[a].setData(x - self.T, utils.sine_eval(x, fa))
                        self.fitCurves[a].setVisible(True)

                except Exception as e:
                    res += '--<br>'
                    print(e.message)

        self.msgBox = QtWidgets.QMessageBox(self)
        self.msgBox.setWindowModality(QtCore.Qt.NonModal)
        self.msgBox.setWindowTitle('Sine Fit Results')
        self.msgBox.setText(res)
        self.msgBox.show()

    def dampedSineFit(self):
        self.pauseButton.setChecked(True);
        self.isPaused = True;
        S, E = self.region.getRegion()
        start = (np.abs(self.time[:self.datapoints] - self.T - S)).argmin()
        end = (np.abs(self.time[:self.datapoints] - self.T - E)).argmin()
        print(self.T, start, end, S, E, self.time[start], self.time[end])
        res = 'Amplitude, Freq, phase, Damping<br>'
        for a in self.curves:
            if self.cbs[a].isChecked():
                try:
                    fa = utils.fit_dsine(self.time[start:end], self.curveData[a][start:end])
                    if fa is not None:
                        amp = abs(fa[0])
                        freq = fa[1]
                        decay = fa[4]
                        phase = fa[2]
                        s = '%5.2f , %5.3f Hz, %.3f, %.3e<br>' % (amp, freq, phase, decay)
                        res += s
                        x = np.linspace(self.time[start], self.time[end], 1000)
                        self.fitCurves[a].clear()
                        self.fitCurves[a].setData(x - self.T, utils.dsine_eval(x, fa))
                        self.fitCurves[a].setVisible(True)
                except Exception as e:
                    res += '--<br>'
                    print(e.message)

        self.msgBox = QtWidgets.QMessageBox(self)
        self.msgBox.setWindowModality(QtCore.Qt.NonModal)
        self.msgBox.setWindowTitle('Damped Sine Fit Results')
        self.msgBox.setText(res)
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


class DIOCONTROL(QtWidgets.QDialog, ui_dio_control.Ui_Dialog):
    def __init__(self, parent, sensor, addr):
        super(DIOCONTROL, self).__init__(parent)
        name = sensor['name']
        self.initialize = sensor['init']
        self.address = addr
        self.setupUi(self)
        self.isPaused = False
        self.currentPage = 0  # Only one page exists.
        self.val = 0

        self.widgets = []
        self.gauges = {}
        self.functions = {}

        for a in sensor.get('write', []):  # Load configuration menus
            l = QtWidgets.QSlider(self);
            l.setMinimum(a[1]);
            l.setMaximum(a[2]);
            l.setValue(a[3]);
            l.setOrientation(QtCore.Qt.Orientation(0x1))  # Qt.Horizontal
            l.valueChanged['int'].connect(functools.partial(self.write, l))
            self.configLayout.addWidget(l);
            self.widgets.append(l)

            gauge = Gauge(self)
            gauge.setObjectName(a[0])
            gauge.set_MinValue(a[1])
            gauge.set_MaxValue(a[2])
            gauge.update_value(a[3])
            self.gaugeLayout.addWidget(gauge)
            self.gauges[l] = gauge  # Name ,min, max value,default value, func
            self.functions[l] = a[4]

        self.setWindowTitle('Control : %s' % name)

    def readValues(self):
        return None

    def write(self, w, val):
        self.val = val
        self.gauges[w].update_value(val)
        self.functions[w](val)

    def launch(self):
        self.initialize(address=self.address)
        self.show()


class DIOROBOT(QtWidgets.QDialog, ui_dio_robot.Ui_Dialog):
    def __init__(self, parent, sensor, addr):
        super(DIOROBOT, self).__init__(parent)
        name = sensor['name']
        self.initialize = sensor['init']
        self.address = addr
        self.setupUi(self)
        self.widgets = []
        self.gauges = OrderedDict()
        self.lastPos = OrderedDict()
        self.functions = OrderedDict()
        self.positions = []

        for a in sensor.get('write', []):  # Load configuration menus
            l = QtWidgets.QSlider(self);
            l.setMinimum(a[1]);
            l.setMaximum(a[2]);
            l.setValue(a[3]);
            l.setOrientation(QtCore.Qt.Orientation(0x1))  # Qt.Horizontal
            l.valueChanged['int'].connect(functools.partial(self.write, l))
            self.configLayout.addWidget(l);
            self.widgets.append(l)

            gauge = Gauge(self)
            gauge.setObjectName(a[0])
            gauge.set_MinValue(a[1])
            gauge.set_MaxValue(a[2])
            gauge.update_value(a[3])
            self.lastPos[l] = a[3]
            self.gaugeLayout.addWidget(gauge)
            self.gauges[l] = gauge  # Name ,min, max value,default value, func
            self.functions[l] = a[4]

        self.setWindowTitle('Control : %s' % name)

    def write(self, w, val):
        self.gauges[w].update_value(val)
        self.lastPos[w] = val
        self.functions[w](val)

    def add(self):
        self.positions.append([a.value() for a in self.lastPos.keys()])
        item = QtWidgets.QListWidgetItem("%s" % str(self.positions[-1]))
        self.listWidget.addItem(item)
        print(self.positions)

    def play(self):
        mypos = [a.value() for a in self.lastPos.keys()]  # Current position
        sliders = list(self.gauges.keys())
        for nextpos in self.positions:
            dx = [(x - y) for x, y in zip(nextpos, mypos)]  # difference between next position and current
            distance = max(dx)
            for travel in range(20):
                for step in range(4):
                    self.write(sliders[step], int(mypos[step]))
                    mypos[step] += dx[step] / 20.
                time.sleep(0.01)

    def launch(self):
        self.initialize(address=self.address)
        self.show()

class SENSORROW(QtWidgets.QWidget, ui_sensor_row.Ui_Form):
    def __init__(self, parent, **kwargs):
        super(SENSORROW, self).__init__(parent)
        self.setupUi(self)
        self.title.setText(kwargs.get('name'))
        self.description.setText(kwargs.get('description'))
        self.address = kwargs.get('address')
        self.addressNumber.display(self.address)
        self.scene = QtWidgets.QGraphicsScene()
        self.image.setScene(self.scene)
        self.image_qt = QtGui.QImage(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'blockly', 'media', kwargs.get('name') + '.jpeg'))
        print(os.path.join('blockly', 'media', kwargs.get('name') + '.jpeg'))
        pic = QtWidgets.QGraphicsPixmapItem()
        pic.setPixmap(QtGui.QPixmap.fromImage(self.image_qt))
        # self.scene.setSceneRect(0, 0, 100, 100)
        self.scene.addItem(pic)

