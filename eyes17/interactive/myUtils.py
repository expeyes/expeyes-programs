import functools
import os

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QIcon, QPainter
from PyQt5.QtWidgets import QTreeWidgetItem, QGraphicsView
from PyQt5.QtCore import Qt, QTimer



def load_defaults(buffer):
    pMap = {}
    iMap = {}

    DefaultPropsFile = buffer.decode('utf-8')
    lines = DefaultPropsFile.split('\n')
    currentProp = ''

    for line in lines:
        if len(line) == 0:
            continue  # ignore blank lines

        if ".png" in line or ".jpg" in line:  # '.svg' in line
            currentProp = line.split('.')[0]
            pMap[currentProp] = ''  # description goes here
            iMap[currentProp] = line  # Image filename
        else:
            if currentProp in pMap:
                pMap[currentProp] += '\n' + line

    return pMap, iMap
    # print(propMap.keys())


class CustomGraphicsView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)


def load_project_structure(startpath, thumbpath, tree):
    for element in os.listdir(startpath):
        path_info = startpath + "/" + element
        if os.path.isdir(path_info):
            parent_itm = QTreeWidgetItem(tree, [os.path.basename(element)])
            load_project_structure(path_info, thumbpath, parent_itm)
            parent_itm.setIcon(0, QIcon(os.path.join(startpath, element + '.jpg')))
        else:
            name = os.path.basename(element)
            if name.endswith('.png'):
                parent_itm = QTreeWidgetItem(tree, [name.replace('.png', '')])
                parent_itm.setIcon(0, QIcon(os.path.join(thumbpath, element.replace('.png', '.jpg'))))


