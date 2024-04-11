import configparser
import math
import time
from functools import partial

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal, Qt
from interactive.MyTypes import Measurement
from layouts import ui_xyLoggerControls2 as ui_xyLoggerControls
from layouts import ui_timeLoggerControls2 as ui_timeLoggerControls

NOLOGGING = 0
DATALOGGER = 1  # Vs time
NLOGGER = 2  # Vs N(samples)
SWEEPLOGGER = 3


class xy_logger_controls(QtWidgets.QDialog, ui_xyLoggerControls.Ui_Dialog):
    init = pyqtSignal()
    newdata = pyqtSignal(int, list, list)
    LOGTYPE = SWEEPLOGGER
    running = False
    sweepInstance = None
    lastUpdateTime = 0
    interval = 0.005
    duration = 0
    xunits = ''
    xunits = ''
    xdata = []
    ydata = []

    def __init__(self, parent, conf: configparser.ConfigParser, sweepIns):
        super(xy_logger_controls, self).__init__(parent)
        self.dataset = 0
        self.setupUi(self)
        self.interval = conf.getfloat('default', 'interval', fallback=10) * 0.001  # default 10 ms
        self.xunits = conf.get('default', 'xunits', fallback='')
        self.yunits = conf.get('default', 'yunits', fallback=conf.get('default', 'units', fallback=''))

        self.intervalBox.setValue(int(self.interval * 1000))

        self.titleButton.setText(conf.get('default', 'title', fallback='data logger'))
        tp = conf.get('default', 'ui', fallback='')
        if tp == 'datalogger':  # Y vs Time
            self.LOGTYPE = DATALOGGER
            self.duration = conf.getfloat('default', 'duration', fallback=20)   # default 20 S
            self.stopBox.setValue(self.duration)
            for a in [self.stepBox, self.stepLabel, self.startBox, self.startLabel]:
                a.setVisible(False)
            self.stopLabel.setText('Duration')

        elif tp == 'samplelogger':  # N vs Time
            self.LOGTYPE = NLOGGER
        elif tp == 'sweeplogger':  # X vs Y with sweeping parameter.
            self.LOGTYPE = SWEEPLOGGER
            self.sweepElement = conf.get('default', 'output', fallback='missing')
            self.sweepInstance = sweepIns[self.sweepElement]

            self.startSweep = conf.getfloat('default', 'start', fallback=self.sweepInstance.minValue)
            self.stopSweep = conf.getfloat('default', 'stop', fallback=self.sweepInstance.maxValue)
            self.stepSweep = conf.getfloat('default', 'stepsize', fallback=self.sweepInstance.stepsize)
            self.xequation = conf.get('default', 'xequation', fallback='')
            self.yequation = conf.get('default', 'yequation', fallback='')
            self.startBox.setValue(self.startSweep)
            self.stopBox.setValue(self.stopSweep)
            self.stepBox.setValue(self.stepSweep)

            self.currentSweepValue = self.startSweep



    def next_value(self):
        if self.currentSweepValue <= self.stopSweep:
            if time.time() > self.lastUpdateTime + self.interval:
                self.lastUpdateTime = time.time()
                self.sweepInstance.update_value(self.currentSweepValue)
                self.progressBar.setValue(int(
                    100 * (self.currentSweepValue - self.startSweep) / (self.stopSweep - self.startSweep)))

                self.currentSweepValue += self.stepSweep
        else:
            self.progressBar.setValue(100)
            self.running = False
            self.newdata.emit(self.dataset, self.xdata, self.ydata)

    def evaluate(self, vars):
        x = eval(self.xequation, vars)
        y = eval(self.yequation, vars)
        self.xLabel.setText(Measurement(x, self.xunits).format3())
        self.yLabel.setText(Measurement(y, self.yunits).format3())
        self.xdata.append(x)
        self.ydata.append(y)

    def startLogging(self):
        self.dataset += 1
        self.interval = self.intervalBox.value() / 1000.
        self.startSweep = self.startBox.value()
        self.stopSweep = self.stopBox.value()
        self.stepSweep = self.stepBox.value()
        self.currentSweepValue = self.startSweep
        self.xdata = []
        self.ydata = []

        self.running = True
        self.progressBar.setValue(0)

    def stopLogging(self):
        self.running = False
        if len(self.xdata):
            self.newdata.emit(self.dataset, self.xdata, self.ydata)
            self.progressBar.setValue(100)

    def clearLogging(self):
        self.dataset = 0
        self.xdata = []
        self.ydata = []
        self.newdata.emit(-1, [], [])  # -1 to clear

    def emitInit(self):
        self.clearLogging()
        self.currentSweepValue = self.startSweep
        self.progressBar.setValue(0)
        self.init.emit()

class time_logger_controls(QtWidgets.QDialog, ui_timeLoggerControls.Ui_Dialog):
    init = pyqtSignal()
    newdata = pyqtSignal(int, list, list)
    LOGTYPE = DATALOGGER
    running = False
    sweepInstance = None
    lastUpdateTime = 0
    startTime = 0
    interval = 0.005
    duration = 10
    xunits = ''
    xunits = ''
    xdata = []
    ydata = []

    def __init__(self, parent, conf: configparser.ConfigParser, sweepIns):
        super(time_logger_controls, self).__init__(parent)
        self.dataset = 0
        self.setupUi(self)

        self.duration = conf.getfloat('default', 'duration', fallback=10)  # default 10 S
        self.interval = conf.getfloat('default', 'interval', fallback=10) * 0.001  # default 10 ms
        self.xunits = conf.get('default', 'xunits', fallback='')
        self.yunits = conf.get('default', 'yunits', fallback=conf.get('default', 'units', fallback=''))

        self.intervalBox.setValue(int(self.interval * 1000))
        self.durationBox.setValue(self.duration)

        self.titleButton.setText(conf.get('default', 'title', fallback='data logger'))
        tp = conf.get('default', 'ui', fallback='')
        if tp == 'datalogger':  # Y vs Time
            self.LOGTYPE = DATALOGGER
        elif tp == 'samplelogger':  # N vs Time
            self.LOGTYPE = NLOGGER

    def evaluate(self, vars):
        x = time.time() - self.startTime
        y = eval(self.yequation, vars)
        if time.time() > self.lastUpdateTime + self.interval:
            self.lastUpdateTime = time.time()
            self.sweepInstance.update_value(self.currentSweepValue)
            self.progressBar.setValue((
                100 * (self.currentSweepValue - self.startSweep) / (self.stopSweep - self.startSweep)))

        self.xLabel.setText(Measurement(x, self.xunits).format3())
        self.yLabel.setText(Measurement(y, self.yunits).format3())
        self.xdata.append(x)
        self.ydata.append(y)

    def startLogging(self):
        self.dataset += 1
        self.interval = self.intervalBox.value() / 1000.
        self.duration = self.durationBox.value()
        self.xdata = []
        self.ydata = []

        self.startTime = time.time()
        self.running = True
        self.progressBar.setValue(0)

    def stopLogging(self):
        self.running = False
        if len(self.xdata):
            self.newdata.emit(self.dataset, self.xdata, self.ydata)
            self.progressBar.setValue(100)

    def clearLogging(self):
        self.dataset = 0
        self.xdata = []
        self.ydata = []
        self.newdata.emit(-1, [], [])  # -1 to clear

    def emitInit(self):
        self.clearLogging()
        self.currentSweepValue = self.startSweep
        self.progressBar.setValue(0)
        self.init.emit()
