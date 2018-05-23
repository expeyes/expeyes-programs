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
    """
    Implements a quick plot window, which can export its data to a few other 
    plotting applications
    """
    exportModes={
        "grace": (_("Grace"), _("Fast old-fashioned plotter/analyzer"), grace),
        "qtiplot": (_("Qtiplot"), _("Modern plotter/analyzer"), qtiplot),
        }
    def __init__(self, parent=None,
                 xdata=[], ydata=[], xlabel="", ylabel="",
                 title=""):
        """
        The constructor
        @param parent the parent window, defaults to None
        @param xdata a vector for the abscissa; any one-dimensional array or
        iterable will be ok
        @param ydata a vector for the ordinate, or a matrix containing n
        vectors for multiple curves; the shape must be compatible with xdata
        @param xlabel a label for abscissa
        @param ylabel a label for ordinate
        @param title a title for the plot
        """
        QWidget.__init__(self, parent)
        self.xdata=xdata
        self.ydata=ydata
        self.xlabel=xlabel
        self.ylabel=ylabel
        self.title=title

        layout = QGridLayout()
        self.setLayout(layout)

        plotWidget = pg.PlotWidget(title=title)
        if len(ydata.shape)==1:
            #simple plot
            plotWidget.plot(x, y)
        else:
            for i in range(ydata.shape[0]):
                #multiple plots
                plotWidget.plot(x, y[i], pen=(i,3))
        # plot goes on top, spanning all columns
        layout.addWidget(plotWidget, 0, 0, 1,(1+len(self.exportModes)))  

        l= QLabel(_("Exports"))
        layout.addWidget(l, 1, 0)
        col=1
        for exp in self.exportModes:
            btn=QPushButton(self.exportModes[exp][0])
            layout.addWidget(btn, 1, col)
            col +=1
        return
        

if __name__=="__main__":
    app = QApplication([])
    x = np.arange(1000)
    y = np.random.normal(size=(2, 1000))
    w = PlotWindow(xdata=x, ydata=y, xlabel="", ylabel="", title="Two plot curves")
    w.show()
    app.exec_()
    
