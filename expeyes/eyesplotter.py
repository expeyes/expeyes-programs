#!/usr/bin/python3
"""
expEYES utility to display plots and export them to other applications
Author  : Georges Khaznadar <georgesk@debian.org>
License : GNU GPL version 3
"""
def _(s):
    return s

from PyQt5.QtWidgets import *
import pyqtgraph as pg
import numpy as np

def grace(data=[], xlabel="", ylabel=""):
    return
def qtiplot(data=[], xlabel="", ylabel=""):
    return

class PlotWindow(QWidget):
    exportModes={
        "grace": (_("Grace"), _("Fast old-fashioned plotter/analyzer"), grace),
        "qtiplot": (_("Qtiplot"), _("Modern plotter/analyzer"), qtiplot),
        }
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        layout = QGridLayout()
        self.setLayout(layout)

        title= QLabel(_("Exports"))
        layout.addWidget(title, 0, 0)
        line=1
        for exp in self.exportModes:
            btn=QPushButton(self.exportModes[exp][0])
            layout.addWidget(btn, line, 0)
            line +=1
        plot = pg.PlotWidget()
        # plot goes on right side, spanning neighbouring rows
        layout.addWidget(plot, 0, 1, (1+len(self.exportModes)), 1)  
        return
        

if __name__=="__main__":
    app = QApplication([])
    w = PlotWindow()
    w.show()
    app.exec_()
    
