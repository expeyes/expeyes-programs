# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
"""
QtVersion.py: this module allows one to choose between PyQt4 and PyQt5
with some rules to be fulfilled:
- when Python3 is used, PyQt4 will be dismissed, since there is no
  support for QtWebKit when Python3 and PyQt4 are chosen together; so
  PyQt5 is chosen
- if the environment variable QT_VERSION is set to somthing beginning with
  "5", or if there an argument "-qt5" in the command line, PyQt5 is chosen
- in any other case PyQt4 is chosen

Additionnally, this module provides the procedure showVersions() to
display PyQt and Python version numbers, and defines the function unicode()
when Python3 is used.

Change in July 2022 : from now on, only Qt6 is supported.

Copyright (C) 2017-2022, Georges Khaznadar <georgesk@debian.org>
License : GNU GPL version 3
"""

import sys

PQT6=True

from PyQt6 import QtGui, QtCore, QtWidgets, QtSvg
from PyQt6.QtGui import QPalette, QColor, QFont, QTextCharFormat, \
		QSyntaxHighlighter, QScreen
from PyQt6.QtWidgets import QMainWindow, QApplication, QCheckBox, \
		QStatusBar, QLabel, QWidget, QSlider, QLineEdit, \
		QVBoxLayout, QHBoxLayout, QPushButton, QMenu, QTextEdit, \
		QMessageBox, QFileDialog

from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QTimer, QUrl, QSize, \
		QTranslator, QLocale, QLibraryInfo, QRegularExpression, \
		QT_TRANSLATE_NOOP
QT_VERSION_STR="6"

def showVersions():
	print("Qt version: %s; Python version: %s" %(QT_VERSION_STR, sys.version))
