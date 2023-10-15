import configparser
import json
import os
import struct
import sys
from functools import partial

import markdown2
import time
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QWidget, \
    QGraphicsPixmapItem, QGraphicsProxyWidget, QInputDialog

import pyqtgraph as pg

from eyes17 import eyes
from interactive.widgetUtils import miniscope
from layouts import ui_xy_layout


class Expt(QWidget, ui_xy_layout.Ui_Form):
    colors = [
        "#FFFFFF",  # White
        "#FF0000",  # Red
        "#00FF00",  # Lime
        "#0000FF",  # Blue
        "#FFFF00",  # Yellow
        "#FF00FF",  # Magenta
        "#00FFFF",  # Cyan
        "#FFA500",  # Orange
        "#FFC0CB",  # Pink
        "#800080",  # Purple
        "#008000",  # Green
        "#FFD700",  # Gold
        "#00CED1",  # DarkTurquoise
        "#FF4500",  # OrangeRed
        "#DA70D6",  # Orchid
        "#FF8C00",  # DarkOrange
        "#FF69B4",  # HotPink
        "#00FA9A",  # MediumSpringGreen
        "#8A2BE2",  # BlueViolet
        "#ADFF2F",  # GreenYellow
    ]

    def __init__(self, device=None):
        super(Expt, self).__init__()
        self.setupUi(self)
        self.p = device
        self.running = False
        self.oscilloscope = miniscope(None, device)
        self.plotLayout.addWidget(self.oscilloscope)

        print('setting up Oscilloscope')
        chans = ['A1', 'A2']
        ylabel = ','.join(chans)
        if len(chans) > 0:
            self.oscilloscope.A1Box.setChecked(True)
            self.oscilloscope.A1Map.setCurrentIndex(self.p.allAnalogChannels.index(chans[0]))
        if len(chans) > 1:
            if chans[1] == "A2":
                self.oscilloscope.A2Box.setChecked(True)
            else:
                print('need to add derived channel', chans[1])
        if len(chans) > 2:
            if chans[2] == "A3":
                self.oscilloscope.A3Box.setChecked(True)
            else:
                print('need to add derived channel', chans[2])
        if len(chans) > 3:
            if chans[3] == "MIC":
                self.oscilloscope.MICBox.setChecked(True)
            else:
                print('need to add derived channel', chans[3])

        self.fitting = False
        for a in self.oscilloscope.fitSelCB:
            if self.fitting:
                a.setChecked(True)
            else:
                a.setChecked(False)

        self.ymin = -5
        self.ymax = 5

        self.oscilloscope.plot.setYRange(self.ymin, self.ymax)

        self.tb = 2
        self.oscilloscope.timebaseSlider.setValue(self.tb)

        self.oscilloscope.plot.getPlotItem().setLabel('left', ylabel, 'Y')
        self.oscilloscope.plot.getPlotItem().setLabel('bottom', ylabel, 'X')

        self.startTime = time.time()
        self.interval = 0.1  # Seconds
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_everything)
        self.timer.start(2)
        self.running = True


    def update_everything(self):
        if not self.p.connected or not self.running:
            return

        v = self.oscilloscope.read()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    from eyes17 import eyes

    p = eyes.open()
    window = Expt(p)
    window.show()

    sys.exit(app.exec_())
