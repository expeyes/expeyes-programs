import sys, time
import functools
from functools import partial

from PyQt5 import QtGui, QtCore, QtWidgets

import pyqtgraph as pg

import math, os.path, struct
import numpy as np
from collections import OrderedDict
from . import ui_advancedLogger, ui_inputSelector, ui_miniScope, ui_dio_stepper
from .gauge import Gauge
from .advancedLoggerTools import fit_sine, sine_eval, LOGGER, inputs, outputs

colors = ['#00ff00', '#ff0000', '#ffff80', (10, 255, 255)] + [
    (50 + np.random.randint(200), 50 + np.random.randint(200), 150 + np.random.randint(100)) for a in range(10)]


class miniscope(QtWidgets.QWidget, ui_miniScope.Ui_Form):
    tbvals = [0.100, 0.200, 0.500, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100., 200.]  # allowed mS/div values
    NP = 500  # Number of samples
    TG = 1  # Number of channels
    MINDEL = 1
    MAXDEL = 1000

    def __init__(self, parent, device):
        super(miniscope, self).__init__(parent)
        self.setupUi(self)
        self.p = device
        if self.p: self.A1Box.addItems(self.p.allAnalogChannels)
        self.splitter.setSizes([500, 100])
        self.activeParameter = 0

        self.curve = self.plot.plot(pen=colors[0])
        self.fitcurve = self.plot.plot(pen=colors[1], width=2)
        self.curve2 = self.plot.plot(pen=colors[2])
        self.fitcurve2 = self.plot.plot(pen=colors[3], width=2)

        self.region = pg.LinearRegionItem()
        self.region.setBrush([255, 0, 50, 50])
        self.region.setZValue(10)
        for a in self.region.lines: a.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor));
        self.plot.addItem(self.region, ignoreBounds=False)
        self.region.setRegion([.1, .5])

        self.results = []
        for a in ['amplitude', 'frequency', 'phase', 'offset', '', '', '', '', '', '']:
            x = QtWidgets.QListWidgetItem(a)
            self.list.addItem(x)
            self.results.append(None)

    def changeParameter(self, p):
        self.activeParameter = p
        self.message.setText('Selected Parameter = %s of %s' % (self.list.item(p).text(), self.A1Box.currentText()))

    def timebaseChanged(self, val):
        msperdiv = self.tbvals[int(val)]  # millisecs / division
        totalusec = msperdiv * 1000 * 10.0  # total 10 divisions
        self.TG = int(totalusec / self.NP)
        if self.TG < self.MINDEL:
            self.TG = self.MINDEL
        elif self.TG > self.MAXDEL:
            self.TG = self.MAXDEL
        xmax = self.TG * self.NP * 1e-3
        self.plot.setRange(xRange=[0, xmax])
        self.timebaseLabel.setText('%.2f mS' % (totalusec / 1e3))
        self.region.setRegion([.1 * xmax, .95 * xmax])

    def read(self, **kwargs):
        chan = str(self.A1Box.currentText())
        if self.p and chan in self.p.allAnalogChannels:
            for a in range(10): self.list.item(a).setText('')
            if self.A2Box.isChecked():  # 2 channel capture
                t, v, t2, v2 = self.p.capture2(self.NP, self.TG, chan)
                self.curve.setData(t, v)
                kwargs['fitCurve'] = self.fitcurve
                res1 = self.sineFit(t, v, **kwargs)

                if res1 is not None:
                    self.list.item(0).setText('Amplitude %.2f' % res1[0]);
                    self.list.item(1).setText('Frequency %.2f' % res1[1])
                    self.list.item(2).setText('Phase %.2f' % res1[2]);
                    self.list.item(3).setText('Offset %.2f' % res1[3]);

                self.curve2.setData(t2, v2)
                kwargs['fitCurve'] = self.fitcurve2
                res2 = self.sineFit(t2, v2, **kwargs)

                if res2 is not None:
                    self.list.item(4).setText('Amplitude %.2f' % res2[0]);
                    self.list.item(5).setText('Frequency %.2f' % res2[1])
                    self.list.item(6).setText('Phase %.2f' % res2[2]);
                    self.list.item(7).setText('Offset %.2f' % res2[3]);

                if res1 is not None and res2 is not None:
                    try:
                        self.results = list(res1) + list(res2)
                        self.results.append(res2[0] / res1[0])  # Amplitude ratio
                        self.results.append(res2[2] - res1[2])  # Phase diff
                        self.list.item(8).setText('AMP(2/1) %.2f' % (res2[0] / res1[0]))
                        self.list.item(9).setText('Phase(2-1) %.2f' % (res2[2] - res1[2]))
                        return float(self.results[self.activeParameter])
                    except Exception as e:
                        print(e)
                        return False
            else:
                if self.activeParameter > 3:
                    self.activeParameter = 0
                    self.list.setCurrentRow(0)
                t, v = self.p.capture1(chan, self.NP, self.TG)
                self.curve.setData(t, v)
                kwargs['fitCurve'] = self.fitcurve
                self.results = self.sineFit(t, v, **kwargs)

                if self.results is not None:
                    self.list.item(0).setText('Amplitude %.2f' % self.results[0]);
                    self.list.item(1).setText('Frequency %.2f' % self.results[1])
                    self.list.item(2).setText('Phase %.2f' % self.results[2]);
                    self.list.item(3).setText('Offset %.2f' % self.results[3]);

                    return float(self.results[self.activeParameter])
        return False

    def changeChannel(self, chan):
        chan = str(chan)
        miny = min(self.p.analogInputSources[chan].calPoly10(0), self.p.analogInputSources[chan].calPoly10(1023))
        maxy = max(self.p.analogInputSources[chan].calPoly10(0), self.p.analogInputSources[chan].calPoly10(1023))
        self.plot.setRange(yRange=[miny, maxy])

    def sineFit(self, t, v, **kwargs):
        S, E = self.region.getRegion()
        start = (np.abs(t - S)).argmin()
        end = (np.abs(t - E)).argmin()
        try:
            fa = fit_sine(t[start:end], v[start:end])
            if fa is not None:
                amp = abs(fa[0])
                freq = fa[1] * 1e3
                if 'freq' in kwargs and self.freqCheckBox.isChecked():  # Input frequency supplied. check for fitting error
                    if (abs(kwargs.get('freq') - freq) / freq) > 0.1:  # Frequency mismatch >10%
                        return None

                phase = fa[2] * 180 / np.pi
                offset = fa[3]
                # self.message.setText(s)
                x = np.linspace(t[start], t[end], 1000)
                if 'fitCurve' in kwargs:
                    kwargs['fitCurve'].clear()
                    kwargs['fitCurve'].setData(x, sine_eval(x, fa))
                return amp, freq, phase, offset
        except Exception as e:
            self.message.setText('fit failed')
            print(e)
        return None


class DIOINPUT(QtWidgets.QDialog, ui_inputSelector.Ui_Dialog):
    SLIDER_SCALING = 1000.

    def __init__(self, parent, device, confirmValues, **kwargs):
        super(DIOINPUT, self).__init__(parent)
        self.setupUi(self)
        self.titlePrefix = kwargs.get('title', '') + ': '
        self.confirmValues = confirmValues
        self.subSelection.setStyleSheet("border: 3px dashed #5353ff;")
        self.selectedGauge = None

        self.p = device
        if self.p: self.I2C = self.p.I2C
        self.inputs = inputs(self.p)
        self.outputs = outputs(self.p)
        self.type = None
        self.autoRefresh = True
        self.functions = []

        self.initialize = None
        self.read = None
        self.widgets = []
        self.gauges = []
        self.miniscope = None
        self.activeSensor = None
        self.permanentInputs = self.inputs.permanentInputs
        self.permanentOutputs = self.outputs.permanentOutputs
        self.init()

    def reconnect(self, device):
        self.p = device
        self.I2C = self.p.I2C
        self.inputs.__init__(self.p)
        self.outputs.__init__(self.p)
        # self.outputs.setDevice(self.p)
        self.permanentInputs = self.inputs.permanentInputs
        self.permanentOutputs = self.outputs.permanentOutputs
        self.init()

    def init(self):
        self.updateOptions(self.permanentInputs + self.refreshSensorList(), self.permanentOutputs)

    def refreshSensorList(self):
        self.logger = LOGGER(self.I2C)
        x = self.logger.I2CScan()
        # print('I2C Found: ',x)
        self.sensorList = []
        for a in x:
            s = self.logger.sensors.get(a, None)
            if s is not None:
                self.sensorList.append(s)
        return self.sensorList

    def updateOptions(self, sensors, outputs):
        self.sensors = sensors + outputs
        self.availableInputs.blockSignals(True)

        self.availableInputs.clear()
        self.availableInputs.addItems([a['name'] for a in self.sensors])
        if self.activeSensor not in self.sensors:
            self.loadSensor(self.sensors[0])
        self.availableInputs.blockSignals(False)

    def selectSensor(self, index):
        self.loadSensor(self.sensors[index])
        self.subSelectionChanged(0)

    def subSelectionChanged(self, index):
        name = str(self.subSelection.currentText())
        self.subSelectionIndex = index
        for a in self.gauges:
            if a.title_text == name:
                a.gauge_color_inner_radius_factor = 0.5
                a.set_NeedleColor(255, 0, 0, 255)
                self.selectedGauge = a
            else:
                a.gauge_color_inner_radius_factor = 0.9
                a.set_NeedleColor(100, 100, 100, 255)
        self.minValue.setValue(self.activeSensor['min'][index])
        self.maxValue.setValue(self.activeSensor['max'][index])

    def loadSensor(self, sensor):
        self.activeSensor = sensor
        self.name = sensor['name']
        self.funtions = {}
        self.initialize = sensor['init']
        self.initialize()

        self.max = sensor.get('max', None)
        self.min = sensor.get('min', None)
        self.type = sensor['type']
        self.autoRefresh = sensor.get('autorefresh', True)

        for a in self.widgets:
            a.setParent(None)
        self.widgets = []
        for a in sensor.get('config', []):  # Load configuration menus
            l = QtWidgets.QLabel(a.get('name', ''))
            self.configLayout.addWidget(l);
            self.widgets.append(l)
            l = QtWidgets.QComboBox();
            l.addItems(a.get('options', []))
            l.currentIndexChanged['int'].connect(a.get('function', None))
            self.configLayout.addWidget(l);
            self.widgets.append(l)

        for a in sensor.get('spinboxes', []):  # Load spinbox configuration options
            label = QtWidgets.QLabel(a.get('name', ''))
            self.configLayout.addWidget(label);
            self.widgets.append(label)
            l = QtWidgets.QSlider()
            l.setOrientation(QtCore.Qt.Horizontal)
            l.setProperty("class", "symmetric volts")
            l.setMaximumSize(QtCore.QSize(300, 16777215))
            MIN = a.get('minimum', 0);
            MAX = a.get('maximum', 100)
            l.setMinimum(MIN)
            l.setMaximum(MAX)
            l.setValue(a.get('value', (MAX + MIN) / 2))  # Move to midpoint if value is not specified
            l.setObjectName(a.get('name', 'undef'))
            l.valueChanged['int'].connect(a.get('function', None))
            self.configLayout.addWidget(l);
            self.widgets.append(l)

        for a in self.gauges:
            a.setParent(None)
        self.gauges = []
        self.subSelection.clear()

        if self.miniscope:
            self.miniscope.setParent(None);
            self.read = None;
            self.miniscope = None

        self.functions = []
        row = 1;
        col = 1;
        parameters = 0

        if 'scope' in self.name:  # It's an oscilloscope. make a plot instead of gauges
            self.miniscope = miniscope(self, self.p)
            self.gaugeLayout.addWidget(self.miniscope)
            self.setWindowTitle(self.titlePrefix + 'Oscilloscope with analysis')
            self.read = self.miniscope.read

        else:
            self.fields = sensor.get('fields', None)
            self.subSelection.addItems(self.fields)
            self.subSelectionIndex = 0
            for a, b, c in zip(self.fields, self.min, self.max):
                gauge = Gauge(self, a)
                gauge.setObjectName(a)
                gauge.set_MinValue(b)
                gauge.set_MaxValue(c)
                self.gaugeLayout.addWidget(gauge, row, col)
                self.gauges.append(gauge)
                col += 1
                if col == 4:
                    row += 1
                    col = 1

                if sensor['type'] == 'output':
                    l = QtWidgets.QSlider(self);
                    l.setMinimum(int(b * self.SLIDER_SCALING))
                    l.setMaximum(int(c * self.SLIDER_SCALING))
                    l.setValue(int(b * self.SLIDER_SCALING))
                    l.setOrientation(QtCore.Qt.Horizontal)
                    gauge.value_needle_snapzone = 1
                    gauge.valueChanged.connect(functools.partial(self.showval, parameters))

                    l.valueChanged['int'].connect(functools.partial(self.write, parameters))
                    self.configLayout.addWidget(l);
                    self.widgets.append(l)
                    self.functions.append(sensor['write'])
                    for a in sensor.get('outputconfig', []):  # Load configuration menus
                        l = QtWidgets.QLabel(a.get('name', ''))
                        self.configLayout.addWidget(l);
                        self.widgets.append(l)
                        l = QtWidgets.QComboBox();
                        l.addItems(a.get('options', []))
                        l.currentIndexChanged['int'].connect(a.get('function', None))
                        self.configLayout.addWidget(l);
                        self.widgets.append(l)

                parameters += 1

            if not self.autoRefresh:  # Time consuming , blocking function call. add a button for it.
                l = QtWidgets.QPushButton("MAKE A MEASUREMENT", self)
                l.clicked.connect(self.readAndUpdate)
                self.configLayout.addWidget(l);
                self.widgets.append(l)

            if sensor['type'] == 'input':
                self.read = sensor['read']
                self.setWindowTitle(self.titlePrefix + 'Input : %s' % self.name)
            else:
                self.read = None
                self.setWindowTitle(self.titlePrefix + 'Output : %s' % self.name)

    def showval(self, index, v):
        self.gauges[index].value = v
        self.gauges[index].update()
        self.widgets[index].setValue(int(v * self.SLIDER_SCALING))

    def write(self, index, val):
        val /= self.SLIDER_SCALING
        self.gauges[index].update_value(val)
        self.functions[index](val)

    def readAndUpdate(self):
        a = self.read()
        self.message.setText(str(a))
        if a is not None:
            self.setValue(a)

    def setValue(self, vals):
        if vals is None:
            print('check connections')
            return
        p = 0
        for a in self.gauges:
            a.update_value(vals[p])
            p += 1

    def confirm(self):
        if self.confirmValues is None: return
        if 'scope' in self.name:
            self.confirmValues('Oscilloscope:%s:%s' % (
            self.miniscope.A1Box.currentText(), self.miniscope.list.item(self.miniscope.activeParameter).text()))
        else:
            self.confirmValues(
                '%s:%s' % (self.activeSensor['name'], self.activeSensor['fields'][self.subSelectionIndex]))

        self.hide()

    def initSweep(self, steps):
        self.value = self.minValue.value()  # self.min[self.subSelectionIndex]
        self.endValue = self.maxValue.value()  # self.max[self.subSelectionIndex]
        self.stepSize = (self.endValue - self.value) / steps
        self.message.setText('%.2f -> %.2f in %d steps' % (self.value, self.endValue, steps))
        if self.type == 'output':  # Output
            self.write(self.subSelectionIndex, self.value * self.SLIDER_SCALING)
            self.message.setText('%.2f / %.2f' % (self.value, self.endValue))

    def nextValue(self, **kwargs):
        if 'scope' in self.name:
            return self.read(**kwargs)
        elif self.type == 'input':
            a = self.read()
            if a is not None:
                if len(a) >= self.subSelectionIndex:
                    self.setValue(a)
                    try:
                        return a[self.subSelectionIndex]
                    except:
                        return False
        elif self.type == 'output':  # Output
            self.write(self.subSelectionIndex, self.value * self.SLIDER_SCALING)
            self.message.setText('%.2f / %.2f' % (self.value, self.endValue))
            v = self.value

            self.value += self.stepSize
            if self.value > self.endValue:
                return None  # None returned will stop the acquisition
            return v

        return False

    def getValue(self, a):
        v = a.read()
        if v is not None:
            return v[self.subSelectionIndex]
        return None

    def launch(self, setWindow=None):
        if self.initialize is not None:
            self.initialize()
        if setWindow is not None:
            self.setWindow(setWindow)
        self.show()

    def setWindow(self, win):
        p = 0
        for a in self.sensors:
            if win.lower() == a['name'].lower():
                # self.loadSensor(a)
                self.availableInputs.setCurrentIndex(p)
                break
            p += 1

    def reposition(self, pos):
        ph = self.parent().geometry().height()
        px = self.parent().geometry().x()
        py = self.parent().geometry().y()
        dw = self.width()
        dh = self.height()
        if pos == 'bottom-left':
            self.setGeometry(px, py + ph - dh, dw, dh)
        elif pos == 'top-left':
            self.setGeometry(px, py, dw, dh)


class DIOSTEPPER(QtWidgets.QDialog, ui_dio_stepper.Ui_Dialog):
    def __init__(self, parent, **configuration):
        super(DIOSTEPPER, self).__init__(parent)
        name = 'stepper'
        self.setupUi(self)
        self.position = 0
        self.targetPosition = 0

        self.p = configuration.get('device', None)

        self.totalSteps = configuration.get('total', 0)
        self.totalStepsBox.setValue(self.totalSteps)
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(self.totalSteps)
        self.setWindowTitle('Stepper Motor Control with CS1,CS2,CS3,CS4')

    def setPins(self, v):
        if v == 0:  # Ap bp an bn
            self.p.ap = 1;
            self.p.bp = 2;
            self.p.an = 4;
            self.p.bn = 8;
        elif v == 1:  # Ap an bp bn
            self.p.ap = 1;
            self.p.an = 2;
            self.p.bp = 4;
            self.p.bn = 8;
        self.p.stepper_positions = [self.p.ap + self.p.bp, self.p.an + self.p.bp, self.p.an + self.p.bn,
                                    self.p.ap + self.p.bn]  # full step sequence.

    def initialize(self):
        self.targetPosition = 0

    def stepLeft(self):
        self.targetPosition -= 1

    def stepRight(self):
        self.targetPosition += 1

    def stepTo(self):
        self.targetPosition = int(self.currentPositionBox.value())

    def read(self):  # Read is not read. it actually updates the motor position.
        if self.position == self.targetPosition:
            return None  # Could return position, but that disables needle dragging functionality of the gauge

        if self.position > self.targetPosition:
            self.p.stepper_reverse()
            self.position -= 1
        elif self.position < self.targetPosition:
            self.p.stepper_forward()
            self.position += 1
        time.sleep(0.02)
        if self.position == self.targetPosition:  # Reached
            if not self.holdBox.isChecked():
                self.p.set_multiplexer(15)  # All at 5V. no current flow.

        self.progressBar.setValue(self.position)

        return self.position

    def setTotalSteps(self, v):
        self.totalSteps = v

    def launch(self):
        self.initialize()
        self.show()
