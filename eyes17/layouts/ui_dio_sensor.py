# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dio_sensor.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

import sys
if sys.version_info.major==3:
	from PyQt5 import QtGui, QtCore, QtWidgets
else:
	from PyQt4 import QtGui, QtCore
	from PyQt4 import QtGui as QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(900, 600)
        font = QtGui.QFont()
        font.setPointSize(9)
        Dialog.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/control/play.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        Dialog.setAutoFillBackground(True)
        Dialog.setSizeGripEnabled(True)
        Dialog.setModal(False)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setContentsMargins(3, 3, 3, 0)
        self.gridLayout.setSpacing(3)
        self.gridLayout.setObjectName("gridLayout")
        self.configLayout = QtWidgets.QHBoxLayout()
        self.configLayout.setObjectName("configLayout")
        self.gridLayout.addLayout(self.configLayout, 1, 0, 1, 4)
        self.switcher = QtWidgets.QPushButton(Dialog)
        self.switcher.setObjectName("switcher")
        self.gridLayout.addWidget(self.switcher, 0, 3, 1, 1)
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 0, 0, 1, 1)
        self.log_2 = QtWidgets.QCheckBox(Dialog)
        self.log_2.setObjectName("log_2")
        self.gridLayout.addWidget(self.log_2, 0, 1, 1, 1)
        self.monitors = QtWidgets.QStackedWidget(Dialog)
        self.monitors.setObjectName("monitors")
        self.page = QtWidgets.QWidget()
        self.page.setObjectName("page")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.page)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gaugeLayout = QtWidgets.QGridLayout()
        self.gaugeLayout.setSpacing(3)
        self.gaugeLayout.setObjectName("gaugeLayout")
        self.verticalLayout.addLayout(self.gaugeLayout)
        self.monitors.addWidget(self.page)
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setObjectName("page_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.page_2)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setHorizontalSpacing(2)
        self.gridLayout_2.setVerticalSpacing(0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.pushButton_2 = QtWidgets.QPushButton(self.page_2)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout_2.addWidget(self.pushButton_2, 2, 1, 1, 1)
        self.pauseBox = QtWidgets.QCheckBox(self.page_2)
        self.pauseBox.setMaximumSize(QtCore.QSize(70, 16777215))
        self.pauseBox.setObjectName("pauseBox")
        self.gridLayout_2.addWidget(self.pauseBox, 2, 0, 1, 1)
        self.pushButton_3 = QtWidgets.QPushButton(self.page_2)
        self.pushButton_3.setObjectName("pushButton_3")
        self.gridLayout_2.addWidget(self.pushButton_3, 2, 2, 1, 1)
        self.graph = PlotWidget(self.page_2)
        self.graph.setObjectName("graph")
        self.gridLayout_2.addWidget(self.graph, 1, 0, 1, 3)
        self.monitors.addWidget(self.page_2)
        self.gridLayout.addWidget(self.monitors, 2, 0, 1, 5)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)

        self.retranslateUi(Dialog)
        self.monitors.setCurrentIndex(0)
        self.log_2.toggled['bool'].connect(Dialog.changeRange)
        self.pushButton.clicked.connect(Dialog.initialize)
        self.switcher.clicked.connect(Dialog.next)
        self.pushButton_2.clicked.connect(Dialog.sineFit)
        self.pauseBox.toggled['bool'].connect(Dialog.pause)
        self.pushButton_3.clicked.connect(Dialog.dampedSineFit)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Sensor Reading"))
        self.switcher.setText(_translate("Dialog", "Data Logger"))
        self.pushButton.setText(_translate("Dialog", "Initialize"))
        self.log_2.setText(_translate("Dialog", "Scale"))
        self.pushButton_2.setText(_translate("Dialog", "SINE FIT"))
        self.pauseBox.setText(_translate("Dialog", "Pause"))
        self.pushButton_3.setText(_translate("Dialog", "DAMPED SINE FIT"))

from pyqtgraph import PlotWidget
from . import res_rc
