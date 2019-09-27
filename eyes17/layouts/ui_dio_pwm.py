# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dio_pwm.ui'
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

class Ui_stack(object):
    def setupUi(self, stack):
        stack.setObjectName("stack")
        stack.resize(270, 29)
        self.inputPage = QtWidgets.QWidget()
        self.inputPage.setObjectName("inputPage")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.inputPage)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.nameIn = QtWidgets.QCheckBox(self.inputPage)
        self.nameIn.setObjectName("nameIn")
        self.horizontalLayout.addWidget(self.nameIn)
        self.pullup = QtWidgets.QCheckBox(self.inputPage)
        self.pullup.setObjectName("pullup")
        self.horizontalLayout.addWidget(self.pullup)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pushButton = QtWidgets.QPushButton(self.inputPage)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        stack.addWidget(self.inputPage)
        self.outputPage = QtWidgets.QWidget()
        self.outputPage.setObjectName("outputPage")
        self.outputLayout = QtWidgets.QHBoxLayout(self.outputPage)
        self.outputLayout.setContentsMargins(0, 0, 0, 0)
        self.outputLayout.setSpacing(0)
        self.outputLayout.setObjectName("outputLayout")
        self.nameOut = QtWidgets.QCheckBox(self.outputPage)
        self.nameOut.setCheckable(True)
        self.nameOut.setChecked(False)
        self.nameOut.setTristate(False)
        self.nameOut.setObjectName("nameOut")
        self.outputLayout.addWidget(self.nameOut)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.outputLayout.addItem(spacerItem1)
        self.pushButton_2 = QtWidgets.QPushButton(self.outputPage)
        self.pushButton_2.setObjectName("pushButton_2")
        self.outputLayout.addWidget(self.pushButton_2)
        stack.addWidget(self.outputPage)
        self.pwmPage = QtWidgets.QWidget()
        self.pwmPage.setObjectName("pwmPage")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.pwmPage)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.slider = QtWidgets.QSlider(self.pwmPage)
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setObjectName("slider")
        self.horizontalLayout_2.addWidget(self.slider)
        self.lcdNumber = QtWidgets.QLCDNumber(self.pwmPage)
        self.lcdNumber.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.lcdNumber.setNumDigits(4)
        self.lcdNumber.setDigitCount(4)
        self.lcdNumber.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.lcdNumber.setObjectName("lcdNumber")
        self.horizontalLayout_2.addWidget(self.lcdNumber)
        self.pushButton_3 = QtWidgets.QPushButton(self.pwmPage)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout_2.addWidget(self.pushButton_3)
        stack.addWidget(self.pwmPage)

        self.retranslateUi(stack)
        stack.setCurrentIndex(0)
        self.pullup.clicked['bool'].connect(stack.setOutputState)
        self.pushButton.clicked.connect(stack.next)
        self.pushButton_2.clicked.connect(stack.next)
        self.slider.valueChanged['int'].connect(stack.setpwm)
        self.pushButton_3.clicked.connect(stack.next)
        self.slider.valueChanged['int'].connect(self.lcdNumber.display)
        self.nameOut.clicked['bool'].connect(stack.setOutputState)
        QtCore.QMetaObject.connectSlotsByName(stack)

    def retranslateUi(self, stack):
        _translate = QtCore.QCoreApplication.translate
        stack.setWindowTitle(_translate("stack", "StackedWidget"))
        self.nameIn.setText(_translate("stack", "name"))
        self.pullup.setText(_translate("stack", "Pull-Up"))
        self.pullup.setProperty("class", _translate("stack", "pullup"))
        self.pushButton.setText(_translate("stack", "INPUT"))
        self.nameOut.setText(_translate("stack", "name"))
        self.pushButton_2.setText(_translate("stack", "OUTPUT"))
        self.pushButton_3.setText(_translate("stack", "PWM"))

