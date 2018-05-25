#!/usr/bin/python3
"""
expEYES utility to display plots and export them to other applications
Author  : © 2018 Georges Khaznadar <georgesk@debian.org>
License : GNU GPL version 3
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import pyqtgraph as pg
import numpy as np

_translate = QCoreApplication. translate

qtiScript="""\
t = newTable("Table1", {rows}, {cols})
t.setColData(1, {xdata})
{templatedYdata}
l=newGraph().activeLayer()
l.setTitle("<font color = blue>{title}</font>")
{TemplatedCurve}
l.setAxisTitle(0, "{ylabel}")
l.setAxisTitle(2, "{xlabel}")
"""

ydataTemplate="t.setColData({col}, {ydata})"

curveTemplate="c{num}=l.insertCurve(t, '1', '{num}', Layer.Line, {color}, -1)"

class PlotWindow(QWidget):
    """
    Implements a quick plot window, which can export its data to a few other 
    plotting applications
    """
    def grace(self):
        print("DEBUG: should call xmgrace")
        return

    def qtiplot(self):
        print("DEBUG: calling qtiplot with title", self.title)
        from subprocess import call
        from tempfile import NamedTemporaryFile
        rows=len(self.xdata)
        xdata=str(list(self.xdata))
        if len(self.ydata.shape)==1:
            #simple plot
            cols=2
            templatedYdata=ydataTemplate.format(
                col=2,
                ydata=str(list(self.ydata)),
            )
            TemplatedCurve=curveTemplate.format(
                num=2,
                color=0,
            )
        else:
            for i in range(self.ydata.shape[0]):
                #multiple plots
                cols=self.ydata.shape[0]+1
                yd=[]
                for i in range(cols-1):
                    yd.append(
                        ydataTemplate.format(
                            col=2+i,
                            ydata=str(list(self.ydata[i])),
                        ))
                templatedYdata="\n".join(yd)
                c=[]
                for i in range(cols-1):
                    c.append(
                        curveTemplate.format(
                            num=2+i,
                            color=i,
                        ))
                TemplatedCurve="\n".join(c)
        script=qtiScript.format(
            rows=rows, cols=cols, xdata=xdata,
            templatedYdata=templatedYdata, TemplatedCurve=TemplatedCurve,
            title=self.title,
            xlabel=self.xlabel,
            ylabel=self.ylabel,
        )
        temp=NamedTemporaryFile(mode="w", prefix="qti_", delete=False)
        temp.write(script)
        temp.close()
        self.tmpFiles.append(temp)
        call("(qtiplot --execute {temp}&)".format(temp=temp.name), shell=True)
        return

    def closeEvent(self, event):
        from os import unlink
        QWidget.closeEvent(self, event)
        for temp in self.tmpFiles:
            unlink(temp.name)
        return

    """
    dictionary of supported export modes.

    the keys must be the name of a method in PlotWindow, which
    will inherit self.xdata and the like to launch an external application
    in the background and plot there the same as in the PlotWindow.

    Every key is associated with a tuple of strings, for a button label
    and its toolTip.
    """
    exportModes={
        "qtiplot": (_translate("eyesplotter","Qtiplot"),
                    _translate("eyesplotter","Modern plotter/analyzer")),
        "grace": (_translate("eyesplotter","Grace"),
                  _translate("eyesplotter","Fast old-fashioned plotter/analyzer")),
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
        self.xdata=np.array(xdata)
        self.ydata=np.array(ydata)
        self.xlabel=xlabel
        self.ylabel=ylabel
        self.title=title
        self.tmpFiles=[]

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

        l= QLabel(_translate("eyesplotter","Export to"))
        layout.addWidget(l, 1, 0)
        col=1
        for exp in self.exportModes:
            label, toolTip = self.exportModes[exp]
            procedure=getattr(self, exp)
            btn=QPushButton(label)
            btn.setToolTip(toolTip)
            layout.addWidget(btn, 1, col)
            btn.clicked.connect(procedure)  
            col +=1
        return




if __name__=="__main__":
    app = QApplication([])
    x = np.arange(1000)
    y = np.random.normal(size=(2, 1000))
    w = PlotWindow(xdata=x, ydata=y, xlabel="", ylabel="", title="Two plot curves")
    w.show()
    app.exec_()
    
