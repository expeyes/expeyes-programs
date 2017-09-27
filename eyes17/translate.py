# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
# Copyright (C) 2017, Georges Khaznadar <georgesk@debian.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os.path, utils

if utils.PQT5 == True:
    from PyQt5 import QtCore
else:
    from PyQt4 import QtCore

def common_paths(pathDic):
    """
    Finds common paths
    @param pathDic a dictionary key => iterable of paths, either absolute
    or relative to the current path
    @result a dictionary of common paths
    """
    curPath = os.path.dirname(os.path.realpath(__file__))
    path={}
    for k,paths in pathDic.items():
        path[k]=None
        for p in paths:
            if os.path.isabs(p):
                if os.path.exists(p):
                    path[k]=os.path.realpath(p)
                    break
            else: # p is relative to curPath
                completePath=os.path.join(curPath, p)
                if os.path.exists(completePath):
                    path[k]=completePath
    return path

def translators(*args):
    """
    create a list of translators
    @param args a list of paths + file prefix to those translators
    @return a list of intialized QTranslator instances
    """
    lang=QtCore.QLocale.system().name()
    result=[]
    for path, prefix in args:
        t=QtCore.QTranslator()
        t.load(prefix+lang, path)
    result.append(t)
    return result

def initTranslators(app, pathList):
    """
    Initialize Qt translators for some QApplication, given a list of paths to
    explore.
    @param app a QApplication instance
    @param pathList a list of paths, either absolute or relative to the
    current path
    """
    path=common_paths({
        "current":      (".",),
        "translations": ("/usr/share/eyes17/lang", "lang",)
    })
    from QtCore.QLibraryInfo import location, TranslationsPath
    for t in translators(
            (path["translation"],""),
            (location(TranslationsPath), "qt_"),
    ):
        app.installTranslator(t)

