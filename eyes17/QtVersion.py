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

Copyright (C) 2017, Georges Khaznadar <georgesk@debian.org>
License : GNU GPL version 3
"""

PQT5 = False
import sys, os

if sys.version_info.major==3:
	PQT5=True

if (os.getenv("QT_VERSION") and os.getenv("QT_VERSION").startswith("5")) or \
   "-qt5" in sys.argv[1:]:
	PQT5=True

if PQT5 == True:
	from PyQt5.QtWidgets import QMainWindow, QApplication, QCheckBox, \
		QStatusBar, QLabel, QDesktopWidget, QWidget, \
		QVBoxLayout, QHBoxLayout, QPushButton, QMenu, QTextEdit
	from PyQt5.QtGui import QPalette, QColor, QFont, QTextCharFormat, \
		QSyntaxHighlighter
	from PyQt5.QtWebKitWidgets import QWebView
	from PyQt5.QtCore import Qt, QTimer, QUrl, QSize, \
		QTranslator, QLocale, QLibraryInfo, QRegExp
	from PyQt5.Qt import QT_VERSION_STR
else:
	from PyQt4.QtCore import Qt, QTimer, QUrl, QSize, \
		QTranslator, QLocale, QLibraryInfo, QRegExp
	from PyQt4.QtGui import QPalette, QColor, QFont, QTextCharFormat, \
		QMainWindow, QApplication, QCheckBox, \
		QStatusBar, QLabel, QDesktopWidget, QWidget, \
		QVBoxLayout, QHBoxLayout, QPushButton, QMenu, QTextEdit, \
		QSyntaxHighlighter
	from PyQt4.QtWebKit import QWebView,QWebSettings
	from PyQt4.Qt import QT_VERSION_STR

def showVersions():
	print("Qt version: %s; Python version: %s" %(QT_VERSION_STR, sys.version))
