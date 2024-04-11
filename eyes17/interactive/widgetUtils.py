import configparser
import math, re, os
import time
from functools import partial

from PyQt5 import QtGui, QtCore, QtWidgets

import pyqtgraph as pg
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QRadialGradient, QColor
from PyQt5.QtWidgets import QLabel, QCheckBox
from scipy.optimize import leastsq
import scipy.optimize as optimize
import numpy as np

from interactive import utils
from interactive.MyTypes import Measurement
from layouts import ui_interactiveScope, ui_interactiveController, ui_interactive_data_logger, ui_popupEditor, \
    ui_interactive_xy_logger
from layouts import ui_category_row_2 as ui_category_row
from layouts import ui_expt_row

from interactive.advancedLoggerTools import fit_sine, sine_eval, inputs, outputs, LOGGER, dsine_eval, fit_dsine

colors = ['#00ff00', '#ff0000', '#ffff80', (10, 255, 255)] + [
    (50 + np.random.randint(200), 50 + np.random.randint(200), 150 + np.random.randint(100)) for a in range(10)]



class MyRow(QtWidgets.QFrame, ui_category_row.Ui_Form):
    set_output = None

    def __init__(self, title, description, imagepath, directory, clickEvent, parent=None):
        super(MyRow, self).__init__(parent)
        self.setupUi(self)
        self.title.setText(title)
        self.description.setText(description)
        # self.scene = QtWidgets.QGraphicsScene()
        # self.image.setScene(self.scene)
        self.directory = directory
        self.pic = QtGui.QPixmap(imagepath)
        self.scaled_pixmap = self.pic.scaled(self.image.size(), aspectRatioMode=1, transformMode=Qt.SmoothTransformation)
        self.image.setPixmap(self.scaled_pixmap)

        self.mousePressEvent = clickEvent


class MyExptRow(QtWidgets.QFrame, ui_expt_row.Ui_Form):
    set_output = None

    def __init__(self, title, description, imagepath, directory, clickEvent, parent=None):
        super(MyExptRow, self).__init__(parent)
        self.setupUi(self)
        self.title.setText(title)
        self.description.setText(description)
        # self.scene = QtWidgets.QGraphicsScene()
        # self.image.setScene(self.scene)
        self.directory = directory
        if(imagepath is not None and os.path.exists(imagepath)):
            self.pic = QtGui.QPixmap(imagepath)
            self.scaled_pixmap = self.pic.scaled(self.image.size(), aspectRatioMode=1,
                                                 transformMode=Qt.SmoothTransformation)
            self.image.setPixmap(self.scaled_pixmap)
        else:
            self.image.setParent(None)
            self.gridLayout_2.setColumnStretch(1, 0)

        self.mousePressEvent = clickEvent


class PopupDialogMixin(object):  # will not work (with PySide at least) unless implemented as 'new style' class.
    def makePopup(self, name, callWidget):
        self.setContentsMargins(0, 0, 0, 0)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setObjectName(name)
        # Move the dialog to the widget that called it
        point = callWidget.rect().bottomRight()
        global_point = callWidget.mapToGlobal(point)
        self.move(global_point - QtCore.QPoint(self.width(), 0))
        print('show popup', global_point, self.width())
        self.show()


class popupEditor(QtWidgets.QDialog, PopupDialogMixin, ui_popupEditor.Ui_Dialog):
    set_output = None

    def __init__(self, parent, name, minimum, maximum, stepsize, value, cmd):
        super(popupEditor, self).__init__(parent)
        self.set_output = cmd
        self.setupUi(self)
        self.gauge = Gauge(self, name)
        self.gauge.setObjectName(name)
        self.gauge.set_MinValue(minimum)
        self.gauge.set_MaxValue(maximum)
        self.gauge.update_value(value)
        self.gauge.value_needle_snapzone = 1
        self.valueBox.setMinimum(minimum)
        self.valueBox.setMaximum(maximum)
        self.valueBox.setSingleStep(stepsize)
        self.valueBox.setValue(value)
        self.gaugeLayout.addWidget(self.gauge)

        self.gauge.valueChanged.connect(partial(self.set_value_mouse))

    def wheelEvent(self, a0: QtGui.QWheelEvent) -> None:
        self.valueBox.wheelEvent(a0)

    def set_value(self, val):
        self.set_output(val)
        self.gauge.update_value(val)

    def set_value_mouse(self, val):
        self.set_output(val)
        self.valueBox.setValue(val)
        self.gauge.update_value(val, True)  # inform that the change was made by a mouse event. to prevent re emit sig


class myLabel(QLabel):
    clicked = pyqtSignal()
    scrolled = pyqtSignal(object)

    def __init__(self, pxm):
        QLabel.__init__(self, parent=None)
        self.setPixmap(pxm)
        self.setFixedWidth(200)
        self.setFixedHeight(200)
        self.setStyleSheet("""
            font-size: 26pt;
            background-color: transparent;
            color: black;
            padding: 0px 5px 0px 5px;
            qproperty-alignment: 'AlignVCenter | AlignLeft';
            qproperty-wordWrap: true;            
        """)

    def __init__(self):
        QLabel.__init__(self, parent=None)
        self.setFixedWidth(200)
        self.setFixedHeight(200)
        self.setStyleSheet("""
            font-size: 26pt;
            background-color: transparent;
            color: black;
            padding: 0px 5px 0px 5px;
            qproperty-alignment: 'AlignVCenter | AlignLeft';
            qproperty-wordWrap: true;            
        """)

    def mousePressEvent(self, event):
        self.clicked.emit()

    def wheelEvent(self, event):
        # event.angleDelta().y() # baseline_speed
        self.scrolled.emit(event)




class Gauge(QtWidgets.QWidget, QtWidgets.QGraphicsWidget):
    valueChanged = QtCore.pyqtSignal(float)

    def __init__(self, parent=None, name=''):
        super(Gauge, self).__init__(parent)
        self.decimals = True

        self.use_timer_event = False
        self.black = QtGui.QColor(0, 0, 0, 255)

        # self.valueColor = QtGui.QColor(50, 50, 50, 255)
        # self.set_valueColor(50, 50, 50, 255)
        # self.NeedleColor = QtGui.QColor(50, 50, 50, 255)
        self.set_NeedleColor(100, 100, 100, 255)
        self.NeedleColorReleased = self.NeedleColor
        # self.NeedleColorDrag = QtGui.QColor(255, 0, 00, 255)
        self.set_NeedleColorDrag(255, 0, 00, 255)

        self.set_ScaleValueColor(100, 100, 100, 255)
        self.set_DisplayValueColor(100, 100, 120, 255)
        self.set_DisplayTitleColor(200, 100, 120, 255)

        # self.CenterPointColor = QtGui.QColor(50, 50, 50, 255)
        self.set_CenterPointColor(50, 50, 50, 255)

        # self.valueColor = black
        # self.black = QtGui.QColor(0, 0, 0, 255)

        self.value_needle_count = 1
        self.value_needle = QtCore.QObject
        self.change_value_needle_style([QtGui.QPolygon([
            QtCore.QPoint(4, 4),
            QtCore.QPoint(-4, 4),
            QtCore.QPoint(-3, -120),
            QtCore.QPoint(0, -126),
            QtCore.QPoint(3, -120)
        ])])

        self.value_min = 0
        self.value_max = 1000
        self.value = self.value_min
        self.value_offset = 0
        self.value_needle_snapzone = 0.2
        self.last_value = 0

        # self.value2 = 0
        # self.value2Color = QtGui.QColor(0, 0, 0, 255)

        self.gauge_color_outer_radius_factor = 1
        self.gauge_color_inner_radius_factor = 0.9
        self.center_horizontal_value = 0
        self.center_vertical_value = 0
        self.debug1 = None
        self.debug2 = None
        self.scale_angle_start_value = 135
        self.scale_angle_size = 270
        self.angle_offset = 0

        # self.scala_main_count = 10
        self.set_scala_main_count(10)
        self.scala_subdiv_count = 5

        self.pen = QtGui.QPen(QtGui.QColor(0, 0, 0))
        self.font = QtGui.QFont('Decorative', 20)

        self.scale_polygon_colors = []
        self.set_scale_polygon_colors([
            [.00, QtGui.QColor("red")],
            [.1, QtGui.QColor("yellow")],
            [.15, QtGui.QColor("green")],
            [1, QtGui.QColor("transparent")]])

        # initialize Scale value text
        # self.enable_scale_text = True
        self.set_enable_ScaleText(True)
        self.scale_fontname = "Decorative"
        self.initial_scale_fontsize = 15
        self.scale_fontsize = self.initial_scale_fontsize

        # initialize Main value text
        self.enable_value_text = True
        self.value_fontname = "Decorative"
        self.initial_value_fontsize = 40
        self.value_fontsize = self.initial_value_fontsize
        self.text_radius_factor = 0.7

        # initialize Title text
        self.title_text = name
        self.enable_title_text = True
        self.title_fontname = "Serif"
        self.initial_title_fontsize = 32
        self.title_fontsize = self.initial_title_fontsize
        self.title_radius_factor = 0.2

        # En/disable scale / fill
        # self.enable_barGraph = True
        self.set_enable_barGraph(True)
        # self.enable_filled_Polygon = True
        self.set_enable_filled_Polygon(True)

        self.enable_CenterPoint = True
        self.enable_fine_scaled_marker = True
        self.enable_big_scaled_marker = True

        self.needle_scale_factor = 0.8
        self.enable_Needle_Polygon = True

        # necessary for resize
        self.setMouseTracking(False)

        self.update()
        self.rescale_method()

    def rescale_method(self):
        # print("slotMethod")
        if self.width() <= self.height():
            self.widget_diameter = self.width()
        else:
            self.widget_diameter = self.height()

        my_y = int(- self.widget_diameter / 2 * self.needle_scale_factor)
        self.change_value_needle_style([QtGui.QPolygon([
            QtCore.QPoint(4, 30),
            QtCore.QPoint(-4, 30),
            QtCore.QPoint(-2, my_y),
            QtCore.QPoint(0, my_y - 6),
            QtCore.QPoint(2, my_y)
        ])])

        self.scale_fontsize = self.initial_scale_fontsize * self.widget_diameter / 400
        self.value_fontsize = self.initial_value_fontsize * self.widget_diameter / 400

    def change_value_needle_style(self, design):
        # prepared for multiple needle instrument
        self.value_needle = []
        for i in design:
            self.value_needle.append(i)
        if not self.use_timer_event:
            self.update()

    def update_value(self, value, mouse_controlled=False):
        if (value == None): return
        if value <= self.value_min:
            self.value = self.value_min
        elif value >= self.value_max:
            self.value = self.value_max
        else:
            self.value = value
        if not mouse_controlled:
            self.valueChanged.emit(value)
        if not self.use_timer_event:
            self.update()

    def update_angle_offset(self, offset):
        self.angle_offset = offset
        if not self.use_timer_event:
            self.update()

    def center_horizontal(self, value):
        self.center_horizontal_value = value

    def center_vertical(self, value):
        self.center_vertical_value = value

    ###############################################################################################
    # Set Methods
    ###############################################################################################
    def set_NeedleColor(self, R=50, G=50, B=50, Transparency=255):
        # Red: R = 0 - 255
        # Green: G = 0 - 255
        # Blue: B = 0 - 255
        # Transparency = 0 - 255
        self.NeedleColor = QtGui.QColor(R, G, B, Transparency)
        self.NeedleColorReleased = self.NeedleColor

        if not self.use_timer_event:
            self.update()

    def set_NeedleColorDrag(self, R=50, G=50, B=50, Transparency=255):
        # Red: R = 0 - 255
        # Green: G = 0 - 255
        # Blue: B = 0 - 255
        # Transparency = 0 - 255
        self.NeedleColorDrag = QtGui.QColor(R, G, B, Transparency)

        if not self.use_timer_event:
            self.update()

    def set_ScaleValueColor(self, R=50, G=50, B=50, Transparency=255):
        # Red: R = 0 - 255
        # Green: G = 0 - 255
        # Blue: B = 0 - 255
        # Transparency = 0 - 255
        self.ScaleValueColor = QtGui.QColor(R, G, B, Transparency)

        if not self.use_timer_event:
            self.update()

    def set_DisplayValueColor(self, R=50, G=50, B=50, Transparency=255):
        self.DisplayValueColor = QtGui.QColor(R, G, B, Transparency)

        if not self.use_timer_event:
            self.update()

    def set_DisplayTitleColor(self, R=50, G=50, B=50, Transparency=255):
        self.DisplayTitleColor = QtGui.QColor(R, G, B, Transparency)

        if not self.use_timer_event:
            self.update()

    def set_CenterPointColor(self, R=50, G=50, B=50, Transparency=255):
        self.CenterPointColor = QtGui.QColor(R, G, B, Transparency)

        if not self.use_timer_event:
            self.update()

    def set_enable_Needle_Polygon(self, enable=True):
        self.enable_Needle_Polygon = enable

        if not self.use_timer_event:
            self.update()

    def set_enable_ScaleText(self, enable=True):
        self.enable_scale_text = enable

        if not self.use_timer_event:
            self.update()

    def set_enable_barGraph(self, enable=True):
        self.enable_barGraph = enable

        if not self.use_timer_event:
            self.update()

    def set_enable_value_text(self, enable=True):
        self.enable_value_text = enable

        if not self.use_timer_event:
            self.update()

    def set_enable_title_text(self, enable=True):
        self.enable_title_text = enable

        if not self.use_timer_event:
            self.update()

    def set_enable_CenterPoint(self, enable=True):
        self.enable_CenterPoint = enable

        if not self.use_timer_event:
            self.update()

    def set_enable_filled_Polygon(self, enable=True):
        self.enable_filled_Polygon = enable

        if not self.use_timer_event:
            self.update()

    def set_enable_big_scaled_grid(self, enable=True):
        self.enable_big_scaled_marker = enable

        if not self.use_timer_event:
            self.update()

    def set_enable_fine_scaled_marker(self, enable=True):
        self.enable_fine_scaled_marker = enable

        if not self.use_timer_event:
            self.update()

    def set_scala_main_count(self, count):
        if count < 1:
            count = 1
        self.scala_main_count = count

        if not self.use_timer_event:
            self.update()

    def set_MinValue(self, min):
        if self.value < min:
            self.value = min
        if min >= self.value_max:
            self.value_min = self.value_max - 1
        else:
            self.value_min = min

        if not self.use_timer_event:
            self.update()

    def set_MaxValue(self, max):
        if self.value > max:
            self.value = max
        if max <= self.value_min:
            self.value_max = self.value_min + 1
        else:
            self.value_max = max

        if not self.use_timer_event:
            self.update()

    def set_start_scale_angle(self, value):
        # Value range in DEG: 0 - 360
        self.scale_angle_start_value = value
        # print("startFill: " + str(self.scale_angle_start_value))

        if not self.use_timer_event:
            self.update()

    def set_total_scale_angle_size(self, value):
        self.scale_angle_size = value
        # print("stopFill: " + str(self.scale_angle_size))

        if not self.use_timer_event:
            self.update()

    def set_gauge_color_outer_radius_factor(self, value):
        self.gauge_color_outer_radius_factor = float(value) / 1000
        # print(self.gauge_color_outer_radius_factor)

        if not self.use_timer_event:
            self.update()

    def set_gauge_color_inner_radius_factor(self, value):
        self.gauge_color_inner_radius_factor = float(value) / 1000
        # print(self.gauge_color_inner_radius_factor)

        if not self.use_timer_event:
            self.update()

    def set_scale_polygon_colors(self, color_array):
        # print(type(color_array))
        if 'list' in str(type(color_array)):
            self.scale_polygon_colors = color_array
        elif color_array == None:
            self.scale_polygon_colors = [[.0, QtGui.QColor("transparent")]]
        else:
            self.scale_polygon_colors = [[.0, QtGui.QColor("transparent")]]

        if not self.use_timer_event:
            self.update()

    ###############################################################################################
    # Get Methods
    ###############################################################################################

    def get_value_max(self):
        return self.value_max

    ###############################################################################################
    # Painter
    ###############################################################################################

    def create_polygon_pie(self, outer_radius, inner_raduis, start, lenght):
        polygon_pie = QtGui.QPolygonF()
        # start = self.scale_angle_start_value
        # start = 0
        # lenght = self.scale_angle_size
        # lenght = 180
        # inner_raduis = self.width()/4
        # print(start)
        n = 360  # angle steps size for full circle
        # changing n value will causes drawing issues
        w = 360 / n  # angle per step
        # create outer circle line from "start"-angle to "start + lenght"-angle
        x = 0
        y = 0

        # todo enable/disable bar graf here
        if not self.enable_barGraph:
            # float_value = ((lenght / (self.value_max - self.value_min)) * (self.value - self.value_min))
            lenght = int(round((lenght / (self.value_max - self.value_min)) * (self.value - self.value_min)))
            # print("f: %s, l: %s" %(float_value, lenght))
            pass

        # mymax = 0

        for i in range(lenght + 1):  # add the points of polygon
            t = w * i + start - self.angle_offset
            x = outer_radius * math.cos(math.radians(t))
            y = outer_radius * math.sin(math.radians(t))
            polygon_pie.append(QtCore.QPointF(x, y))
        # create inner circle line from "start + lenght"-angle to "start"-angle
        for i in range(lenght + 1):  # add the points of polygon
            # print("2 " + str(i))
            t = w * (lenght - i) + start - self.angle_offset
            x = inner_raduis * math.cos(math.radians(t))
            y = inner_raduis * math.sin(math.radians(t))
            polygon_pie.append(QtCore.QPointF(x, y))

        # close outer line
        polygon_pie.append(QtCore.QPointF(x, y))
        return polygon_pie

    def draw_filled_polygon(self, outline_pen_with=0):
        if not self.scale_polygon_colors == None:
            painter_filled_polygon = QtGui.QPainter(self)
            painter_filled_polygon.setRenderHint(QtGui.QPainter.Antialiasing)
            painter_filled_polygon.translate(self.width() / 2, self.height() / 2)

            painter_filled_polygon.setPen(QtCore.Qt.NoPen)

            self.pen.setWidth(outline_pen_with)
            if outline_pen_with > 0:
                painter_filled_polygon.setPen(self.pen)

            colored_scale_polygon = self.create_polygon_pie(
                ((self.widget_diameter / 2) - (self.pen.width() / 2)) * self.gauge_color_outer_radius_factor,
                (((self.widget_diameter / 2) - (self.pen.width() / 2)) * self.gauge_color_inner_radius_factor),
                self.scale_angle_start_value, self.scale_angle_size)

            gauge_rect = QtCore.QRect(QtCore.QPoint(0, 0),
                                      QtCore.QSize(int(self.widget_diameter / 2 - 1), int(self.widget_diameter - 1)))
            grad = QtGui.QConicalGradient(QtCore.QPointF(0, 0), - self.scale_angle_size - self.scale_angle_start_value +
                                          self.angle_offset - 1)

            for eachcolor in self.scale_polygon_colors:
                grad.setColorAt(eachcolor[0], eachcolor[1])
            painter_filled_polygon.setBrush(grad)
            painter_filled_polygon.drawPolygon(colored_scale_polygon)
        # return painter_filled_polygon

    def draw_bg(self):
        diameter = self.widget_diameter
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.translate(int(self.width() / 2), int(self.height() / 2))
        painter.setPen(QtCore.Qt.NoPen)

        # Create the radial gradient
        gradient = QRadialGradient(0, 0, self.widget_diameter / 2)
        gradient.setColorAt(0, QColor("#fff"))
        gradient.setColorAt(1, QColor("#acc"))

        # Set the gradient as the brush for the painter
        painter.setBrush(gradient)
        # painter.setBrush(QtGui.QColor("#dfe"))
        painter.drawEllipse(int(-diameter / 2), int(-diameter / 2), int(diameter), int(diameter))

    ###############################################################################################
    # Scale Marker
    ###############################################################################################

    def draw_big_scaled_markter(self):
        my_painter = QtGui.QPainter(self)
        my_painter.setRenderHint(QtGui.QPainter.Antialiasing)
        # Koordinatenursprung in die Mitte der Flaeche legen
        my_painter.translate(int(self.width() / 2), int(self.height() / 2))

        # my_painter.setPen(QtCore.Qt.NoPen)
        self.pen = QtGui.QPen(QtGui.QColor(0, 0, 0, 255))
        self.pen.setWidth(2)
        # # if outline_pen_with > 0:
        my_painter.setPen(self.pen)

        my_painter.rotate(self.scale_angle_start_value - self.angle_offset)
        steps_size = (float(self.scale_angle_size) / float(self.scala_main_count))
        scale_line_outer_start = self.widget_diameter / 2
        scale_line_lenght = (self.widget_diameter / 2) - (self.widget_diameter / 20)
        # print(stepszize)
        for i in range(self.scala_main_count + 1):
            my_painter.drawLine(int(scale_line_lenght), 0, int(scale_line_outer_start), 0)
            my_painter.rotate(steps_size)

    def create_scale_marker_values_text(self):
        painter = QtGui.QPainter(self)
        # painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Koordinatenursprung in die Mitte der Flaeche legen
        painter.translate(int(self.width() / 2), int(self.height() / 2))
        # painter.save()
        font = QtGui.QFont(self.scale_fontname, int(self.scale_fontsize))
        fm = QtGui.QFontMetrics(font)

        pen_shadow = QtGui.QPen()

        pen_shadow.setBrush(self.ScaleValueColor)
        painter.setPen(pen_shadow)

        text_radius_factor = 0.8
        text_radius = self.widget_diameter / 2 * text_radius_factor

        scale_per_div = ((self.value_max - self.value_min) / self.scala_main_count)

        angle_distance = (float(self.scale_angle_size) / float(self.scala_main_count))
        for i in range(self.scala_main_count + 1):
            # text = str(int((self.value_max - self.value_min) / self.scala_main_count * i))
            val = self.value_min + scale_per_div * i
            if abs(val) > 1e6 or (abs(val) < 1e-1 and val != 0):
                text = str('%.1e' % (val))
            else:
                if self.decimals:
                    text = str('%.1f' % (val))
                else:
                    text = str('%d' % (int(val)))
            w = fm.width(text) + 1
            h = fm.height()
            painter.setFont(QtGui.QFont(self.scale_fontname, int(self.scale_fontsize)))
            angle = angle_distance * i + float(self.scale_angle_start_value - self.angle_offset)
            x = text_radius * math.cos(math.radians(angle))
            y = text_radius * math.sin(math.radians(angle))
            # print(w, h, x, y, text)
            text = [x - int(w / 2), y - int(h / 2), int(w), int(h), QtCore.Qt.AlignCenter, text]
            painter.drawText(int(text[0]), int(text[1]), int(text[2]), int(text[3]), text[4], text[5])

    # painter.restore()

    def create_fine_scaled_marker(self):
        #  Description_dict = 0
        my_painter = QtGui.QPainter(self)

        my_painter.setRenderHint(QtGui.QPainter.Antialiasing)
        # Koordinatenursprung in die Mitte der Flaeche legen
        my_painter.translate(int(self.width() / 2), int(self.height() / 2))

        my_painter.setPen(QtGui.QColor("black"))
        my_painter.rotate(self.scale_angle_start_value - self.angle_offset)
        steps_size = (float(self.scale_angle_size) / float(self.scala_main_count * self.scala_subdiv_count))
        scale_line_outer_start = self.widget_diameter / 2
        scale_line_lenght = (self.widget_diameter / 2) - (self.widget_diameter / 40)
        for i in range((self.scala_main_count * self.scala_subdiv_count) + 1):
            my_painter.drawLine(int(scale_line_lenght), 0, int(scale_line_outer_start), 0)
            my_painter.rotate(steps_size)

    def create_values_text(self):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        # painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Koordinatenursprung in die Mitte der Flaeche legen
        painter.translate(int(self.width() / 2), int(self.height() / 2))
        # painter.save()
        # xShadow = 3.0
        # yShadow = 3.0
        font = QtGui.QFont(self.value_fontname, int(self.value_fontsize))
        fm = QtGui.QFontMetrics(font)

        pen_shadow = QtGui.QPen()

        pen_shadow.setBrush(self.DisplayValueColor)
        painter.setPen(pen_shadow)

        text_radius = self.widget_diameter / 2 * self.text_radius_factor

        # angle_distance = (float(self.scale_angle_size) / float(self.scala_main_count))
        # for i in range(self.scala_main_count + 1):
        if self.decimals:
            text = str('%.2f' % (self.value))
        else:
            text = str('%d' % (self.value))
        w = fm.width(text) + 1
        h = fm.height()
        painter.setFont(QtGui.QFont(self.value_fontname, int(self.value_fontsize)))

        # Mitte zwischen Skalenstart und Skalenende:
        # Skalenende = Skalenanfang - 360 + Skalenlaenge
        # Skalenmitte = (Skalenende - Skalenanfang) / 2 + Skalenanfang
        angle_end = float(self.scale_angle_start_value + self.scale_angle_size - 360)
        angle = (angle_end - self.scale_angle_start_value) / 2 + self.scale_angle_start_value

        x = text_radius * math.cos(math.radians(angle))
        y = text_radius * math.sin(math.radians(angle))
        # print(w, h, x, y, text)
        text = [x - int(w / 2), y - int(h / 2), int(w), int(h), QtCore.Qt.AlignCenter, text]
        painter.drawText(int(text[0]), int(text[1]), int(text[2]), int(text[3]), text[4], text[5])

    # painter.restore()

    def create_title_text(self):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        painter.translate(int(self.width() / 2), int(self.height() / 2))
        font = QtGui.QFont(self.value_fontname, int(self.value_fontsize))
        fm = QtGui.QFontMetrics(font)
        pen_shadow = QtGui.QPen()
        pen_shadow.setBrush(self.DisplayTitleColor)
        painter.setPen(pen_shadow)
        text_radius = self.widget_diameter / 2 * self.text_radius_factor
        text = self.title_text
        w = fm.width(text) + 1
        h = fm.height()
        painter.setFont(QtGui.QFont(self.value_fontname, int(self.value_fontsize)))
        angle_end = float(self.scale_angle_start_value + self.scale_angle_size - 360)
        angle = (angle_end - self.scale_angle_start_value) / 2 + self.scale_angle_start_value

        x = text_radius * math.cos(math.radians(angle))
        y = text_radius * math.sin(math.radians(angle))
        text = [x - int(w / 2), y - int(self.widget_diameter / 1.5), int(w), int(h), QtCore.Qt.AlignCenter, text]
        painter.drawText(int(text[0]), int(text[1]), int(text[2]), int(text[3]), text[4], text[5])

    # painter.restore()

    def draw_big_needle_center_point(self, diameter=30):
        painter = QtGui.QPainter(self)
        # painter.setRenderHint(QtGui.QtGui.QPainter.HighQualityAntialiasing)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Koordinatenursprung in die Mitte der Flaeche legen
        painter.translate(int(self.width() / 2), int(self.height() / 2))
        painter.setPen(QtCore.Qt.NoPen)
        # painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self.CenterPointColor)
        # diameter = diameter # self.widget_diameter/6
        painter.drawEllipse(int(-diameter / 2), int(-diameter / 2), int(diameter), int(diameter))

    def draw_needle(self):
        painter = QtGui.QPainter(self)
        # painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        # Koordinatenursprung in die Mitte der Flaeche legen
        painter.translate(int(self.width() / 2), int(self.height() / 2))
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self.NeedleColor)
        painter.rotate(((self.value - self.value_offset - self.value_min) * self.scale_angle_size /
                        (self.value_max - self.value_min)) + 90 + self.scale_angle_start_value)

        painter.drawConvexPolygon(self.value_needle[0])

    ###############################################################################################
    # Events
    ###############################################################################################

    def resizeEvent(self, event):
        self.rescale_method()

    def paintEvent(self, event):
        # Main Drawing Event:
        # Will be executed on every change

        # colored pie area
        if self.enable_filled_Polygon:
            self.draw_bg()
            self.draw_filled_polygon()

        # draw scale marker lines
        if self.enable_fine_scaled_marker:
            self.create_fine_scaled_marker()
        if self.enable_big_scaled_marker:
            self.draw_big_scaled_markter()

        # draw scale marker value text
        if self.enable_scale_text:
            self.create_scale_marker_values_text()

        # Display Value
        if self.enable_value_text:
            self.create_values_text()

        # draw needle 1
        if self.enable_Needle_Polygon:
            self.draw_needle()

        # Draw Center Point
        if self.enable_CenterPoint:
            self.draw_big_needle_center_point(diameter=(self.widget_diameter / 6))

        # Display Title
        if self.enable_title_text:
            self.create_title_text()

    ###############################################################################################
    # MouseEvents
    ###############################################################################################

    def setMouseTracking(self, flag):
        def recursive_set(parent):
            for child in parent.findChildren(QtCore.QObject):
                try:
                    child.setMouseTracking(flag)
                except:
                    pass
                recursive_set(child)

        QtWidgets.QWidget.setMouseTracking(self, flag)
        recursive_set(self)

    def mouseReleaseEvent(self, QMouseEvent):
        # print("released")
        self.NeedleColor = self.NeedleColorReleased

        if not self.use_timer_event:
            self.update()
        pass

    def mouseMoveEvent(self, event):
        x, y = event.x() - (self.width() / 2), event.y() - (self.height() / 2)
        if not x == 0:
            angle = math.atan2(y, x) / math.pi * 180
            # winkellaenge der anzeige immer positiv 0 - 360deg
            # min wert + umskalierter wert
            value = (float(math.fmod(angle - self.scale_angle_start_value + 720, 360)) / \
                     (float(self.scale_angle_size) / float(self.value_max - self.value_min))) + self.value_min
            temp = value
            fmod = float(math.fmod(angle - self.scale_angle_start_value + 720, 360))
            state = 0
            if (self.value - (self.value_max - self.value_min) * self.value_needle_snapzone) <= \
                    value <= \
                    (self.value + (self.value_max - self.value_min) * self.value_needle_snapzone):
                self.NeedleColor = self.NeedleColorDrag
                state = 9
                if value >= self.value_max and self.last_value < (self.value_max - self.value_min) / 2:
                    state = 1
                    value = self.value_max
                    self.last_value = self.value_min
                    self.valueChanged.emit(value)
                elif value >= self.value_max >= self.last_value:
                    state = 2
                    value = self.value_max
                    self.last_value = self.value_max
                    self.valueChanged.emit(value)
                else:
                    state = 3
                    self.last_value = value
                    self.valueChanged.emit(value)


class miniscope(QtWidgets.QWidget, ui_interactiveScope.Ui_Form):
    NP = 1000  # Number of samples
    TG = 1  # Number of channels
    MINDEL = 1
    MAXDEL = 8100

    MAXCHAN = 4
    Ranges12 = ['16 V', '8 V', '4 V', '2.5 V', '1 V', '.5V']  # Voltage ranges for A1 and A2
    RangeVals12 = [16., 8., 4., 2.5, 1., 0.5]
    Ranges34 = ['4 V', '2 V', '1 V', '.5V']  # Voltage ranges for A3 and MIC
    RangeVals34 = [4, 2, 1, 0.5]
    chanStatus = [1, 0, 0, 0]
    tbvals = [0.100, 0.200, 0.500, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0, 400.0]  # allowed mS/div values
    sources = ['A1', 'A2', 'A3', 'MIC', 'SEN', 'IN1', 'AN8']
    delay = MINDEL  # Time interval between samples
    TBval = 1  # timebase list index
    Trigindex = 0
    Triglevel = 0
    dutyCycle = 50

    traceWidget = [None] * 4
    xdata = [None] * 4
    ydata = [None] * 4
    ydataFit = [None] * 4
    offSliders = [None] * 4
    offValues = [0] * 4
    DiffTraceW = None
    fitResWidget = [None] * 4
    chanSelCB = [None] * 4
    rangeSelPB = [None] * 4
    fitFlags = [0] * 4
    Amplitude = [0] * 4
    Frequency = [0] * 4
    Phase = [0] * 4
    rangeVals = [4] * 4  # selected value of range
    scaleLabs = [None] * 4  # display fullscale value inside pg
    voltMeters = [None] * 3
    voltMeterCB = [None] * 3
    valueLabel = None
    scopeBusy = False
    fetchTime = 0
    A1Buf = 0
    A2Buf = 0
    A3Buf = 0
    MICBuf = 0

    def __init__(self, parent, device):
        super(miniscope, self).__init__(parent)
        self.XYEnabled = False
        self.setupUi(self)
        self.p = device
        self.chanStatus = [1, 0, 0, 0]  # PyQt problem. chanStatus somehow getting preserved ???
        self.resultCols = utils.makeResultColors()
        self.traceCols = utils.makeTraceColors()
        self.htmlColors = utils.makeHtmlColors()

        self.trigBox.addItems(self.sources)
        if self.p is not None:
            self.A1Map.addItems(self.p.allAnalogChannels)
            if (self.p.connected):
                self.p.set_sine(1000)
        self.splitter.setSizes([500, 100])
        self.activeParameter = 0

        self.plot.disableAutoRange()
        self.plot.setXRange(0, self.tbvals[self.TBval] * 10)
        self.plot.setYRange(-16, 16)
        self.plot.hideButtons()  # Do not show the 'A' button of pg

        self.XYplot.setXRange(-5, 5)
        self.XYplot.setYRange(-5, 5)

        for ch in range(self.MAXCHAN):  # initialize the pg trace widgets
            self.traceWidget[ch] = self.plot.plot([0, 0], [0, 0], pen=self.traceCols[ch])
        self.diffTraceW = self.plot.plot([0, 0], [0, 0], pen=self.traceCols[-1])

        self.XYTrace = self.XYplot.plot([0, 0], [0, 0], pen=self.traceCols[0])
        self.xc = "A1"
        self.yc = "A2"
        self.xeq = "A1"
        self.yeq = "A2"

        self.chanSelCB = [self.A1Box, self.A2Box, self.A3Box, self.MICBox]
        self.rangeSelPB = [self.A1Range, self.A2Range]
        self.fitSelCB = [self.A1Fit, self.A2Fit, self.A3Fit, self.MICFit]
        # self.voltMeterCB = [self.voltMeterCB1, self.voltMeterCB2, self.voltMeterCB3]

        for ch in range(4):
            self.chanSelCB[ch].stateChanged.connect(partial(self.select_channel, ch))
            self.chanSelCB[ch].setStyleSheet('''border: 1px solid %s;''' % (self.htmlColors[ch]))  # <font color="%s">
        for ch in range(2):
            self.rangeSelPB[ch].currentIndexChanged['int'].connect(partial(self.select_range, ch))

        self.chanSelCB[0].setChecked(True)

        self.region = pg.LinearRegionItem()
        self.region.setBrush([255, 0, 50, 50])
        self.region.setZValue(10)
        for a in self.region.lines: a.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor));
        self.plot.addItem(self.region, ignoreBounds=False)
        self.region.setRegion([.01, .05])

        self.set_timebase(self.TBval)



    def select_trig_source(self, index):
        src = self.sources[self.Trigindex]
        self.Trigindex = index
        print('set trigger source', self.Trigindex, src, self.Triglevel)
        if index > 3:
            self.Trigindex = 0
        try:
            self.p.configure_trigger(self.Trigindex, src, self.Triglevel)
        except Exception as e:
            print('Could not set trigger source', e)

    def updateChannels(self):
        if self.chanStatus[0] == 1 and self.chanStatus[1] == 1:  # channel 1, 2 is selected
            self.xchan.setText(self.A1Map.currentText())
            self.xc = self.xeq = self.A1Map.currentText()
            self.ychan.setText("A2")
            self.yc = self.yeq = "A2"
            self.XYEnabled = True
            self.updateLabel()
        else:
            self.XYEnabled = False
            self.XYTrace.clear()

    def updateX(self):
        self.xeq = self.xchan.text()
        print(self.xeq, 'vs', self.yeq)
        self.updateLabel()

    def updateY(self):
        self.yeq = self.ychan.text()
        print(self.xeq, 'vs', self.yeq)
        self.updateLabel()

    def set_timebase(self, tb):
        print('oscilloscope timebase changed:', tb)
        self.TBval = tb
        self.plot.setXRange(0, self.tbvals[self.TBval] / 100.)
        msperdiv = self.tbvals[int(tb)]  # millisecs / division
        totalusec = msperdiv * 1000 * 10.0  # total 10 divisions
        self.TG = int(totalusec / self.NP)
        if self.TG < self.MINDEL:
            self.TG = self.MINDEL
        elif self.TG > self.MAXDEL:
            self.TG = self.MAXDEL

        print('oscilloscope timebase changed:', tb, ' =>', '%.2f mS' % (totalusec / 1e3))
        self.timebaseLabel.setText('%.2f mS' % (totalusec / 1e3))
        self.region.setRegion([.1 * self.tbvals[self.TBval] / 100., .95 * self.tbvals[self.TBval] / 100.])

    def select_range(self, ch, index):
        try:
            self.p.select_range(self.sources[ch], self.RangeVals12[index])
        except:
            self.comerr()
            return

    def A1MapChanged(self, chan):

        self.xchan.setText(self.A1Map.currentText())
        self.xc = self.xeq = self.A1Map.currentText()
        self.ychan.setText("A2")
        self.yc = self.yeq = "A2"
        self.updateLabel()

    def updateLabel(self):
        self.XYLabel.setText(self.xeq + " Vs " + self.yeq)

    def set_trigger_level(self, tr):
        self.Triglevel = tr * 0.001  # convert to volts
        try:
            if self.TBval > 3:
                self.p.configure_trigger(self.Trigindex, self.sources[self.Trigindex], self.Triglevel, resolution=10,
                                         prescaler=5)
            else:
                self.p.configure_trigger(self.Trigindex, self.sources[self.Trigindex], self.Triglevel)
        except:
            print('trig set error')

    def setWG(self, v):
        self.WGLabel.setText('WG:' + '%.2f' % self.p.set_sine(v))

    def setSQ1(self, v):
        self.SQ1Label.setText('SQ1:' + '%.2f' % self.p.set_sq1(v))

    def setPV1(self, v):
        self.PV1Label.setText('PV1:' + '%.3f' % (self.p.set_pv1(v / 1000.)))

    def select_channel(self, ch):
        if self.chanSelCB[ch].isChecked():
            self.chanStatus[ch] = 1
            self.traceWidget[ch] = self.plot.plot([0, 0], [0, 0], pen=self.traceCols[ch])
        else:
            self.chanStatus[ch] = 0
            self.plot.removeItem(self.traceWidget[ch])

        self.updateChannels()


    def read(self, **kwargs):
        chan = str(self.A1Map.currentText())
        if self.p and chan in self.p.allAnalogChannels:
            totalTime = self.NP * self.TG * 1e-6  # in S units
            if totalTime < 50e-3:  # Acceptable time for UI freeze. 50mS
                try:
                    if self.chanStatus[2] == 1 or self.chanStatus[3] == 1:  # channel 3 or 4 selected
                        self.xdata[0], self.ydata[0], \
                            self.xdata[1], self.ydata[1], \
                            self.xdata[2], self.ydata[2], \
                            self.xdata[3], self.ydata[3] = self.p.capture4(self.NP, self.TG,
                                                                           str(self.A1Map.currentText()),
                                                                           trigger=self.trigEnable.isChecked())
                    elif self.chanStatus[1] == 1:  # channel 2 is selected
                        self.xdata[0], self.ydata[0], \
                            self.xdata[1], self.ydata[1] = self.p.capture2(self.NP, self.TG,
                                                                           str(self.A1Map.currentText()),
                                                                           trigger=self.trigEnable.isChecked())
                    elif self.chanStatus[0] == 1:  # only A1 selected
                        self.xdata[0], self.ydata[0] = self.p.capture1(str(self.A1Map.currentText()), self.NP,
                                                                       self.TG,
                                                                       trigger=self.trigEnable.isChecked())
                    for a in range(4):
                        if (self.xdata[a] is not None):
                            self.xdata[a] *= 1e-3
                except Exception as e:
                    print('Comerr', e)
                    self.p.connected = False
                    return
            else:
                if self.scopeBusy:  # Scope is busy => Capture called. => fetch available data.
                    x = self.p.oscilloscope_progress()
                    if x[2] > 10:  # Atlest 10 samples available
                        if self.A1Buf > 0:
                            self.p.__fetch_incremental_channel__(self.A1Buf, x[2])
                            self.xdata[0] = self.p.achans[self.A1Buf - 1].get_fetched_xaxis() * 1e-6
                            self.ydata[0] = self.p.achans[self.A1Buf - 1].get_fetched_yaxis()
                        if self.A2Buf > 0:
                            self.p.__fetch_incremental_channel__(self.A2Buf, x[2])
                            self.xdata[1] = self.p.achans[self.A2Buf - 1].get_fetched_xaxis() * 1e-6
                            self.ydata[1] = self.p.achans[self.A2Buf - 1].get_fetched_yaxis()
                        if self.A3Buf > 0:
                            self.p.__fetch_incremental_channel__(self.A3Buf, x[2])
                            self.xdata[2] = self.p.achans[self.A3Buf - 1].get_fetched_xaxis() * 1e-6
                            self.ydata[2] = self.p.achans[self.A3Buf - 1].get_fetched_yaxis()
                        if self.MICBuf > 0:
                            self.p.__fetch_incremental_channel__(self.MICBuf, x[2])
                            self.xdata[3] = self.p.achans[self.MICBuf - 1].get_fetched_xaxis() * 1e-6
                            self.ydata[3] = self.p.achans[self.MICBuf - 1].get_fetched_yaxis()

                        if x[0]:  # Conversion done
                            self.scopeBusy = False

                    else:
                        return


                # Scope is not busy. initiate new capture call
                else:
                    sum = 0
                    for a in self.chanStatus:
                        if a == 1:
                            sum += 1

                    self.A1Buf = self.A2Buf = self.A3Buf = self.MICBuf = 0

                    if sum == 1:  # Single Active Channel
                        if self.chanStatus[0]:
                            self.A1Buf = 1
                            self.p.capture_traces(1, self.NP, self.TG, self.A1Map.currentText(),
                                                  trigger=self.trigEnable.isChecked())
                        elif self.chanStatus[1]:
                            self.A2Buf = 1
                            self.p.capture_traces(1, self.NP, self.TG, "A2", trigger=self.trigEnable.isChecked())
                        elif self.chanStatus[2]:
                            self.A3Buf = 1
                            self.p.capture_traces(1, self.NP, self.TG, "A3", trigger=self.trigEnable.isChecked())
                        elif self.chanStatus[3]:
                            self.MICBuf = 1
                            self.p.capture_traces(1, self.NP, self.TG, "MIC", trigger=self.trigEnable.isChecked())
                    elif sum == 2:  # Two channel mode
                        if self.chanStatus[0]:  # A1/A1 Map is already enabled.
                            if self.chanStatus[1]:
                                self.A1Buf = 1
                                self.A2Buf = 2
                                self.p.capture_traces(2, self.NP, self.TG, self.A1Map.currentText(),
                                                      trigger=self.trigEnable.isChecked())
                            elif self.chanStatus[2]:
                                self.A1Buf = 1
                                self.A3Buf = 3
                                self.p.capture_traces(4, self.NP, self.TG, self.A1Map.currentText(),
                                                      trigger=self.trigEnable.isChecked())
                            elif self.chanStatus[3]:
                                self.A1Buf = 1
                                self.MICBuf = 4
                                self.p.capture_traces(4, self.NP, self.TG, self.A1Map.currentText(),
                                                      trigger=self.trigEnable.isChecked())
                        elif self.chanStatus[1]:  # A2 is enabled.
                            if self.chanStatus[2]:
                                self.A3Buf = 1
                                self.A2Buf = 2
                                self.p.capture_traces(2, self.NP, self.TG, "A3", trigger=self.trigEnable.isChecked())
                            elif self.chanStatus[3]:
                                self.MICBuf = 1
                                self.A2Buf = 2
                                self.p.capture_traces(2, self.NP, self.TG, "MIC", trigger=self.trigEnable.isChecked())
                        elif self.chanStatus[2]:  # A3 is enabled. MIC too
                            self.A3Buf = 3
                            self.MICBuf = 4
                            self.p.capture_traces(4, self.NP, self.TG, "A3", trigger=self.trigEnable.isChecked())
                    elif sum == 3 or sum == 4:
                        if self.chanStatus[0]:
                            self.A1Buf = 1
                        if self.chanStatus[1]:
                            self.A2Buf = 2
                        if self.chanStatus[2]:
                            self.A3Buf = 3
                        if self.chanStatus[3]:
                            self.MICBuf = 4
                        self.p.capture_traces(4, self.NP, self.TG, self.A1Map.currentText(),
                                              trigger=self.trigEnable.isChecked())
                    if sum > 0:
                        self.scopeBusy = True
                        self.fetchTime = time.time() + self.p.samples * self.p.timebase * 1e-6
                    return

            ## Curve Fitting routine

            for ch in range(4):
                if self.chanStatus[ch] == 1 and len(self.xdata[ch]) > 10:
                    r = 16. / self.rangeVals[ch]
                    S, E = self.region.getRegion()
                    start = (np.abs(self.xdata[ch] - S)).argmin()
                    end = (np.abs(self.xdata[ch] - E)).argmin()

                    # Draw the datapoints
                    self.traceWidget[ch].setData(self.xdata[ch], self.ydata[ch])
                    if len(self.ydata[ch][start:end]) > 10 and np.max(self.ydata[ch][start:end]) > self.rangeVals[
                        ch]:
                        self.msg(self.tr('%s input is clipped. Increase range') % self.sources[ch])

                    if self.fitSelCB[ch].isChecked():
                        try:
                            # Fit the data to a sine function
                            fa = fit_sine(self.xdata[ch][start:end], self.ydata[ch][start:end])
                        except Exception as err:
                            print('fit_sine error:', err)
                            fa = None
                        if fa is not None:
                            self.ydataFit[ch] = sine_eval(self.xdata[ch][start:end], fa)
                            self.Amplitude[ch] = abs(fa[0])
                            self.Frequency[ch] = fa[1]
                            self.Phase[ch] = fa[2] * 180 / math.pi
                            s = self.tr('%5.2f V, %5.1f Hz') % (self.Amplitude[ch], self.Frequency[ch])
                            self.fitSelCB[ch].setText(s)
                    else:
                        self.fitSelCB[ch].setText('')

            if self.XYEnabled and len(self.xdata[0]) > 10:
                self.XYplot.setLabel('bottom', self.xeq)
                self.XYplot.setLabel('left', self.yeq)

                xdata = self.ydata[0]
                ydata = self.ydata[1]

                xdata = eval(self.xeq, {self.xc: self.ydata[0], 'A2': self.ydata[1]})
                ydata = eval(self.yeq, {self.xc: self.ydata[0], 'A2': self.ydata[1]})

                self.XYTrace.setData(xdata, ydata)

        return

    def changeChannel(self, chan):
        chan = str(chan)
        miny = min(self.p.analogInputSources[chan].calPoly10(0), self.p.analogInputSources[chan].calPoly10(1023))
        maxy = max(self.p.analogInputSources[chan].calPoly10(0), self.p.analogInputSources[chan].calPoly10(1023))
        self.plot.setRange(yRange=[miny, maxy])

    def msg(self, str):
        print(str)


class DIOINPUT(QtWidgets.QDialog, ui_interactiveController.Ui_Dialog):
    SLIDER_SCALING = 1000.
    newValue = pyqtSignal(float)

    def __init__(self, parent, device, confirmValues, **kwargs):
        super(DIOINPUT, self).__init__(parent)
        self.setupUi(self)
        self.titlePrefix = kwargs.get('title', '') + ': '
        self.confirmValues = confirmValues
        self.subSelection.setStyleSheet("border: 3px dashed #5353ff;")
        self.selectedGauge = None

        self.p = device
        if self.p: self.I2C = self.p.I2C
        self.inputs = inputs(self.p)
        self.outputs = outputs(self.p)
        self.type = None
        self.autoRefresh = True
        self.functions = []

        self.initialize = None
        self.read = None
        self.widgets = []
        self.gauges = []
        self.miniscope = None
        self.activeSensor = None
        self.permanentInputs = self.inputs.permanentInputs
        self.permanentOutputs = self.outputs.permanentOutputs
        self.init()

    def reconnect(self, device):
        self.p = device
        self.I2C = self.p.I2C
        self.inputs.__init__(self.p)
        self.outputs.__init__(self.p)
        # self.outputs.setDevice(self.p)
        self.permanentInputs = self.inputs.permanentInputs
        self.permanentOutputs = self.outputs.permanentOutputs
        self.init()

    def init(self):
        self.updateOptions(self.permanentInputs + self.refreshSensorList(), self.permanentOutputs)

    def refreshSensorList(self):
        self.logger = LOGGER(self.I2C)
        x = self.logger.I2CScan()
        # print('I2C Found: ',x)
        self.sensorList = []
        for a in x:
            s = self.logger.sensors.get(a, None)
            if s is not None:
                self.sensorList.append(s)
        return self.sensorList

    def updateOptions(self, sensors, outputs):
        self.sensors = sensors + outputs
        self.availableInputs.blockSignals(True)

        self.availableInputs.clear()
        self.availableInputs.addItems([a['name'] for a in self.sensors])
        if self.activeSensor not in self.sensors:
            self.loadSensor(self.sensors[0])
        self.availableInputs.blockSignals(False)

    def selectSensor(self, index):
        self.loadSensor(self.sensors[index])
        self.subSelectionChanged(0)

    def subSelectionChanged(self, index):
        name = str(self.subSelection.currentText())
        self.subSelectionIndex = index
        for a in self.gauges:
            if a.title_text == name:
                a.gauge_color_inner_radius_factor = 0.5
                a.set_NeedleColor(255, 0, 0, 255)
                self.selectedGauge = a
            else:
                a.gauge_color_inner_radius_factor = 0.9
                a.set_NeedleColor(100, 100, 100, 255)
        self.minValue.setValue(self.activeSensor['min'][index])
        self.maxValue.setValue(self.activeSensor['max'][index])

    def loadSensor(self, sensor):
        print('loading sensor ...', sensor)
        self.activeSensor = sensor
        self.name = sensor['name']
        self.funtions = {}
        self.initialize = sensor['init']
        self.initialize()

        self.max = sensor.get('max', None)
        self.min = sensor.get('min', None)
        self.type = sensor['type']
        self.autoRefresh = sensor.get('autorefresh', True)

        for a in self.widgets:
            a.setParent(None)
        self.widgets = []
        for a in sensor.get('config', []):  # Load configuration menus
            l = QtWidgets.QLabel(a.get('name', ''))
            self.configLayout.addWidget(l);
            self.widgets.append(l)
            l = QtWidgets.QComboBox();
            l.addItems(a.get('options', []))
            l.currentIndexChanged['int'].connect(a.get('function', None))
            self.configLayout.addWidget(l);
            self.widgets.append(l)

        for a in sensor.get('spinboxes', []):  # Load spinbox configuration options
            label = QtWidgets.QLabel(a.get('name', ''))
            self.configLayout.addWidget(label);
            self.widgets.append(label)
            l = QtWidgets.QSlider()
            l.setOrientation(QtCore.Qt.Horizontal)
            l.setProperty("class", "symmetric volts")
            l.setMaximumSize(QtCore.QSize(300, 16777215))
            MIN = a.get('minimum', 0);
            MAX = a.get('maximum', 100)
            l.setMinimum(MIN)
            l.setMaximum(MAX)
            l.setValue(a.get('value', (MAX + MIN) / 2))  # Move to midpoint if value is not specified
            l.setObjectName(a.get('name', 'undef'))
            l.valueChanged['int'].connect(a.get('function', None))
            self.configLayout.addWidget(l);
            self.widgets.append(l)

        for a in self.gauges:
            a.setParent(None)
        self.gauges = []
        self.subSelection.clear()

        if self.miniscope:
            self.miniscope.setParent(None);
            self.read = None;
            self.miniscope = None

        self.functions = []
        row = 1;
        col = 1;
        parameters = 0

        if 'scope' in self.name:  # It's an oscilloscope. make a plot instead of gauges
            self.miniscope = miniscope(self, self.p)
            self.gaugeLayout.addWidget(self.miniscope)
            self.setWindowTitle(self.titlePrefix + 'Oscilloscope with analysis')
            self.read = self.miniscope.read

        else:
            self.fields = sensor.get('fields', None)
            self.subSelection.addItems(self.fields)
            self.subSelectionIndex = 0
            for a, b, c in zip(self.fields, self.min, self.max):
                gauge = Gauge(self, a)
                gauge.setObjectName(a)
                gauge.set_MinValue(b)
                gauge.set_MaxValue(c)
                self.gaugeLayout.addWidget(gauge, row, col)
                self.gauges.append(gauge)
                col += 1
                if col == 4:
                    row += 1
                    col = 1

                if sensor['type'] == 'output':
                    l = QtWidgets.QSlider(self);
                    l.setMinimum(b * self.SLIDER_SCALING);
                    l.setMaximum(c * self.SLIDER_SCALING);
                    l.setValue(b * self.SLIDER_SCALING);
                    l.setOrientation(QtCore.Qt.Horizontal)
                    gauge.value_needle_snapzone = 1
                    gauge.valueChanged.connect(partial(self.showval, parameters))

                    l.valueChanged['int'].connect(partial(self.write, parameters))
                    self.configLayout.addWidget(l);
                    self.widgets.append(l)
                    self.functions.append(sensor['write'])
                    for a in sensor.get('outputconfig', []):  # Load configuration menus
                        l = QtWidgets.QLabel(a.get('name', ''))
                        self.configLayout.addWidget(l);
                        self.widgets.append(l)
                        l = QtWidgets.QComboBox();
                        l.addItems(a.get('options', []))
                        l.currentIndexChanged['int'].connect(a.get('function', None))
                        self.configLayout.addWidget(l)
                        self.widgets.append(l)

                parameters += 1

            if not self.autoRefresh:  # Time consuming , blocking function call. add a button for it.
                l = QtWidgets.QPushButton("MAKE A MEASUREMENT", self)
                l.clicked.connect(self.readAndUpdate)
                self.configLayout.addWidget(l);
                self.widgets.append(l)

            if sensor['type'] == 'input':
                self.read = sensor['read']
                self.setWindowTitle(self.titlePrefix + 'Input : %s' % self.name)
            else:
                self.read = None
                self.setWindowTitle(self.titlePrefix + 'Output : %s' % self.name)

    def showval(self, index, v):
        self.gauges[index].value = v
        self.gauges[index].update()
        self.widgets[index].setValue(v * self.SLIDER_SCALING)
        self.newValue.emit(v)

    def write(self, index, val):
        val /= self.SLIDER_SCALING
        self.gauges[index].update_value(val)
        self.functions[index](val)

    def readAndUpdate(self):
        a = self.read()
        self.message.setText(str(a))
        if a is not None:
            self.setValue(a)

    def setValue(self, vals):
        if vals is None:
            print('check connections')
            return
        p = 0
        for a in self.gauges:
            a.update_value(vals[p])
            p += 1

    def confirm(self):
        if self.confirmValues is None: return
        if 'scope' in self.name:
            self.confirmValues('Oscilloscope:%s:%s' % (
                self.miniscope.A1Box.currentText(), self.miniscope.list.item(self.miniscope.activeParameter).text()))
        else:
            self.confirmValues(
                '%s:%s' % (self.activeSensor['name'], self.activeSensor['fields'][self.subSelectionIndex]))

        self.hide()

    def initSweep(self, steps):
        self.value = self.minValue.value()  # self.min[self.subSelectionIndex]
        self.endValue = self.maxValue.value()  # self.max[self.subSelectionIndex]
        self.stepSize = (self.endValue - self.value) / steps
        self.message.setText('%.2f -> %.2f in %d steps' % (self.value, self.endValue, steps))
        if self.type == 'output':  # Output
            self.write(self.subSelectionIndex, self.value * self.SLIDER_SCALING)
            self.message.setText('%.2f / %.2f' % (self.value, self.endValue))

    def nextValue(self, **kwargs):
        if 'scope' in self.name:
            return self.read(**kwargs)
        elif self.type == 'input':
            a = self.read()
            if a is not None:
                if len(a) >= self.subSelectionIndex:
                    self.setValue(a)
                    try:
                        return a[self.subSelectionIndex]
                    except:
                        return False
        elif self.type == 'output':  # Output
            self.write(self.subSelectionIndex, self.value * self.SLIDER_SCALING)
            self.message.setText('%.2f / %.2f' % (self.value, self.endValue))
            v = self.value

            self.value += self.stepSize
            if self.value > self.endValue:
                return None  # None returned will stop the acquisition
            return v

        return False

    def getValue(self, a):
        v = a.read()
        if v is not None:
            return v[self.subSelectionIndex]
        return None

    def launch(self, setWindow=None):
        if self.initialize is not None:
            self.initialize()
        if setWindow is not None:
            self.setWindow(setWindow)
        self.show()

    def setWindow(self, win):
        p = 0
        for a in self.sensors:
            if win.lower() == a['name'].lower():
                # self.loadSensor(a)
                self.availableInputs.setCurrentIndex(p)
                break
            p += 1

    def reposition(self, pos):
        ph = self.parent().geometry().height()
        px = self.parent().geometry().x()
        py = self.parent().geometry().y()
        dw = self.width()
        dh = self.height()
        if pos == 'bottom-left':
            self.setGeometry(px, py + ph - dh, dw, dh)
        elif pos == 'top-left':
            self.setGeometry(px, py, dw, dh)


class Datalogger(QtWidgets.QWidget, ui_interactive_data_logger.Ui_Form):
    fields = []
    min = []
    max = []
    cbs = {}
    pos = 0

    curves = {}
    fitCurves = {}
    gauges = {}
    T = 0
    datapoints = {}
    curveData = {}
    start_time = 0
    row = 1
    col = 1

    labelStyle = {}

    def __init__(self):
        super(Datalogger, self).__init__()
        self.xdata = None
        self.setupUi(self)
        self.currentPage = 1
        self.switcher.setText("Analog Gauge")
        self.isPaused = False
        self.init_fields()
        colors = ['#00ffff', '#008080', '#ff0000', '#800000', '#ff00ff', '#800080', '#00FF00', '#008000', '#ffff00',
                  '#808000', '#0000ff', '#000080', '#a0a0a4', '#808080', '#ffffff', '#4000a0']

        self.region = pg.LinearRegionItem()
        self.region.setBrush([255, 0, 50, 50])
        self.region.setZValue(10)
        for a in self.region.lines:
            a.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor))
        self.graph.addItem(self.region, ignoreBounds=False)
        self.region.setRegion([-3, -.5])

        self.labelStyle = {'color': 'rgb(200,250,200)', 'font-size': '12pt'}
        self.graph.setLabel('bottom', 'Time -->', units='S', **self.labelStyle)
        self.graph.setXRange(0, 5)  # xrange
        self.toggled()

    def setup(self, desc: configparser.ConfigParser):
        print('setting data logger axes', desc.get('default', 'ylabel', fallback='missing'))
        self.graph.setLabel('left', desc.get('default', 'ylabel', fallback='Voltage'),
                            units=desc.get('default', 'yunits', fallback='V'), **self.labelStyle)

        self.graph.setYRange(desc.getfloat('default', 'ymin', fallback=desc.getfloat('default', 'min', fallback=-5)),
                             desc.getfloat('default', 'ymax', fallback=desc.getfloat('default', 'max', fallback=5)))

        self.graph.setLabel('bottom', 'Time -->', units='S', **self.labelStyle)
        self.graph.setXRange(desc.getfloat('default', 'duration', fallback=5) * -1, 0)  # xrange = [0, 5]

    def init_fields(self):
        print('init fields')
        for a in self.gauges:
            self.gaugeLayout.removeWidget(self.gauges[a][0])
            self.gauges[a][0].setParent(None)

        for a in self.cbs:
            self.parameterLayout.removeWidget(self.cbs[a])
            self.cbs[a].setParent(None)

        for a in self.curves:
            self.graph.removeItem(self.curves[a])
        for a in self.fitCurves:
            self.graph.removeItem(self.fitCurves[a])

        self.fields = []
        self.min = []
        self.max = []
        self.cbs = {}
        self.pos = 0
        self.curves = {}
        self.fitCurves = {}
        self.gauges = {}
        self.T = 0
        self.datapoints = {}
        self.ydata = {}
        self.xdata = {}
        self.start_time = time.time()
        self.row = 1
        self.col = 1
        self.parameterLayout

    def add_field(self, name, minimum, maximum):
        self.fields.append(name)
        self.min.append(minimum)
        self.max.append(maximum)
        gauge = Gauge(self, name)
        gauge.setObjectName(name)
        gauge.set_MinValue(minimum)
        gauge.set_MaxValue(maximum)
        self.gaugeLayout.addWidget(gauge, self.row, self.col)
        self.col += 1
        if self.col == 4:
            self.row += 1
            self.col = 1
        self.gauges[name] = [gauge, minimum, maximum]  # Name ,min, max value

        curve = self.graph.plot(pen=colors[len(self.curves.keys())], connect="finite")
        fitcurve = self.graph.plot(pen=colors[len(self.curves.keys())], width=2, connect="finite")
        self.curves[name] = curve
        self.datapoints[name] = 0
        self.ydata[name] = np.empty(300)
        self.xdata[name] = np.empty(300)
        self.fitCurves[name] = fitcurve
        cbs = QCheckBox(name)
        cbs.clicked.connect(self.toggled)
        cbs.setChecked(True)
        self.gauges[name][0].set_NeedleColor()
        self.gauges[name][0].set_enable_filled_Polygon()
        self.parameterLayout.addWidget(cbs)
        self.cbs[name] = cbs
        self.cbs[name].setStyleSheet('background-color:%s;' % colors[self.pos])
        self.pos += 1

    def toggled(self):
        for inp in self.fields:
            if self.cbs[inp].isChecked():
                self.curves[inp].setVisible(True)
                self.gauges[inp][0].set_NeedleColor()
                self.gauges[inp][0].set_enable_filled_Polygon()
            else:
                self.curves[inp].setVisible(False)
                self.gauges[inp][0].set_NeedleColor(255, 0, 0, 30)
                self.gauges[inp][0].set_enable_filled_Polygon(False)

    def pauseLogging(self, v):
        self.isPaused = v
        for inp in self.fields:
            self.fitCurves[inp].setVisible(False)

    def setDuration(self):
        self.graph.setRange(xRange=[-1 * int(self.durationBox.value()), 0])

    def insert_value(self, inp, v):
        if inp not in self.gauges:
            return
        self.gauges[inp][0].update_value(v)

        self.T = time.time() - self.start_time

        self.xdata[inp][self.datapoints[inp]] = self.T
        self.ydata[inp][self.datapoints[inp]] = v
        if self.datapoints[inp] >= self.ydata[inp].shape[0] - 1:
            tmp = self.ydata[inp]
            self.ydata[inp] = np.empty(self.ydata[inp].shape[0] * 2)  # double the size
            self.ydata[inp][:tmp.shape[0]] = tmp

            tmp = self.xdata[inp]
            self.xdata[inp] = np.empty(self.xdata[inp].shape[0] * 2)  # double the size
            self.xdata[inp][:tmp.shape[0]] = tmp

        self.curves[inp].setData(self.xdata[inp][:self.datapoints[inp]], self.ydata[inp][:self.datapoints[inp]])
        self.curves[inp].setPos(-self.T, 0)
        self.datapoints[inp] += 1

    def updateEverything(self):
        if self.isPaused: return

        pos = 0
        for inp in self.fields:
            if self.cbs[inp].isChecked():
                v = self.p.get_average_voltage(inp, samples=2)
                self.valueTable.item(0, pos).setText('%.3f' % v)
            else:
                v = 0
                self.valueTable.item(0, pos).setText('')
            self.gauges[inp][0].update_value(v)

            if self.isPaused: return

            self.T = time.time() - self.start_time

            self.xdata[inp][self.datapoints[inp]] = self.T
            self.ydata[inp][self.datapoints[inp]] = v
            if self.datapoints[inp] >= self.ydata[inp].shape[0] - 1:
                tmp = self.ydata[inp]
                self.ydata[inp] = np.empty(self.ydata[inp].shape[0] * 2)  # double the size
                self.ydata[inp][:tmp.shape[0]] = tmp

                tmp = self.xdata[inp]
                self.xdata[inp] = np.empty(self.xdata[inp].shape[0] * 2)  # double the size
                self.xdata[inp][:tmp.shape[0]] = tmp

            self.curves[inp].setData(self.xdata[inp][:self.datapoints[inp]], self.ydata[inp][:self.datapoints[inp]])
            self.curves[inp].setPos(-self.T, 0)
            pos += 1
        self.datapoints[inp] += 1  # Increment datapoints once per set. it's shared

    def restartLogging(self):
        self.msg(self.tr('Clear Traces and Data'))
        self.pauseLogging(False);
        self.pauseButton.setChecked(False)
        self.setDuration()
        for pos in self.fields:
            self.curves[pos].setData([], [])
            self.datapoints[pos] = 0
            self.T = 0
            self.ydata[pos] = np.empty(300)
            self.xdata[pos] = np.empty(300)
            self.start_time = time.time()

    def next(self):
        if self.currentPage == 1:
            self.currentPage = 0
            self.switcher.setText("Data Logger")
            self.pauseButton.setChecked(False);
            self.pauseLogging(False)
        else:
            self.currentPage = 1
            self.switcher.setText("Analog Gauge")

        self.monitors.setCurrentIndex(self.currentPage)

    def sineFit(self):
        self.pauseButton.setChecked(True);
        self.isPaused = True;
        S, E = self.region.getRegion()
        for a in self.curves:
            start = (np.abs(self.xdata[a][:self.datapoints[a]] - self.T - S)).argmin()
            end = (np.abs(self.xdata[a][:self.datapoints[a]] - self.T - E)).argmin()
            print(self.T, start, end, S, E, self.xdata[start], self.xdata[end])
            res = 'Amp, Freq, Phase, Offset<br>'

            if self.cbs[a].isChecked():
                try:
                    fa = fit_sine(self.xdata[a][start:end], self.ydata[a][start:end])
                    if fa is not None:
                        amp = abs(fa[0])
                        freq = fa[1]
                        phase = fa[2]
                        offset = fa[3]
                        s = '%5.2f , %5.3f Hz, %.2f, %.1f<br>' % (amp, freq, phase, offset)
                        res += s
                        x = np.linspace(self.xdata[start], self.xdata[end], 1000)
                        self.fitCurves[a].clear()
                        self.fitCurves[a].setData(x - self.T, sine_eval(x, fa))
                        self.fitCurves[a].setVisible(True)

                except Exception as e:
                    res += '--<br>'
                    print(e.message)
                    pass
        self.msgBox = QtWidgets.QMessageBox(self)
        self.msgBox.setWindowModality(QtCore.Qt.NonModal)
        self.msgBox.setWindowTitle('Sine Fit Results')
        self.msgBox.setText(res)
        self.msgBox.show()

    def dampedSineFit(self):
        self.pauseButton.setChecked(True);
        self.isPaused = True;
        S, E = self.region.getRegion()
        for a in self.curves:
            start = (np.abs(self.xdata[a][:self.datapoints[a]] - self.T - S)).argmin()
            end = (np.abs(self.xdata[a][:self.datapoints[a]] - self.T - E)).argmin()
            print(self.T, start, end, S, E, self.xdata[start], self.xdata[end])
            res = 'Amplitude, Freq, phase, Damping<br>'

            if self.cbs[a].isChecked():
                try:
                    fa = fit_dsine(self.xdata[start:end], self.ydata[a][start:end])
                    if fa is not None:
                        amp = abs(fa[0])
                        freq = fa[1]
                        decay = fa[4]
                        phase = fa[2]
                        s = '%5.2f , %5.3f Hz, %.3f, %.3e<br>' % (amp, freq, phase, decay)
                        res += s
                        x = np.linspace(self.xdata[start], self.xdata[end], 1000)
                        self.fitCurves[a].clear()
                        self.fitCurves[a].setData(x - self.T, dsine_eval(x, fa))
                        self.fitCurves[a].setVisible(True)
                except Exception as e:
                    res += '--<br>'
                    print(e.message)
                    pass
        self.msgBox = QtWidgets.QMessageBox(self)
        self.msgBox.setWindowModality(QtCore.Qt.NonModal)
        self.msgBox.setWindowTitle('Damped Sine Fit Results')
        self.msgBox.setText(res)
        self.msgBox.show()

    def msg(self, m):
        self.msgwin.setText(self.tr(m))

    def saveTraces(self):
        self.init_fields()

    '''
    def saveTraces(self):
        self.pauseButton.setChecked(True);
        self.isPaused = True;
        fn = QFileDialog.getSaveFileName(self, "Save file", QtCore.QDir.currentPath(),
                                         "Text files (*.txt);;CSV files (*.csv);;All files (*.*)", "CSV files (*.csv)")
        if (len(fn) == 2):  # Tuple
            fn = fn[0]
        print(fn)
        if fn != '':
            f = open(fn, 'wt')
            f.write('time')
            for inp in self.fields:
                if self.cbs[inp].isChecked():
                    f.write(',%s' % (inp))
            f.write('\n')

            for a in range(self.datapoints[a]):
                f.write('%.3f' % (self.xdata[a] - self.xdata[0]))
                for inp in self.fields:
                    if self.cbs[inp].isChecked():
                        f.write(',%.5f' % (self.ydata[inp][a]))
                f.write('\n')
            f.close()
            self.msg(self.tr('Traces saved to ') + fn)
            
    '''


class XYlogger(QtWidgets.QWidget, ui_interactive_xy_logger.Ui_Form):
    curves = {}
    labelStyle = {}
    xvar = ''
    yvar = ''
    xunits = ''
    yunits = ''
    UPDATE_INTERVAL = 0.2  # Every 200mS
    lastUpdateTime = 0
    arrow = None
    text = None
    trailSize = 100
    duration = 20
    xdata = np.zeros(trailSize)
    ydata = np.zeros(trailSize)
    pos = 0
    TIME_MODE = 0
    XY_MODE = 1
    LOGMODE = TIME_MODE

    def __init__(self):
        super(XYlogger, self).__init__()
        self.setupUi(self)
        self.startTime = time.time()

        self.labelStyle = {'color': 'rgb(255,255,80)', 'font-size': '12pt'}

    def setup(self, desc: configparser.ConfigParser):
        self.trailSize = 100
        self.xdata = np.zeros(self.trailSize)
        self.ydata = np.zeros(self.trailSize)
        self.pos = 0

        self.xunits = desc.get('default', 'xunits', fallback='')
        self.yunits = desc.get('default', 'yunits', fallback=desc.get('default', 'units', fallback=''))
        self.graph.setLabel('left', desc.get('default', 'ylabel', fallback='Voltage'),
                            units=self.yunits, **self.labelStyle)

        self.graph.setLabel('bottom', desc.get('default', 'xlabel', fallback='X'),
                            units=self.xunits, **self.labelStyle)

        if desc.get('default', 'ui', fallback='') == 'datalogger':  # vs Time
            print('setting up xy logger in Time vs Y mode', desc.get('default', 'ui', fallback='missing'))
            self.LOGMODE = self.TIME_MODE
            self.duration = desc.getfloat('default', 'duration', fallback=20)
            self.graph.setXRange(0, self.duration)

            self.graph.setYRange(desc.getfloat('default', 'ymin', fallback=-5),
                                 desc.getfloat('default', 'ymax', fallback=5))

            self.startTime = time.time()
            self.xvar = ''
            self.yvar = desc.get('default', 'input', fallback='')
        else:
            print('setting up xy logger in X vs Y mode', desc.get('default', 'ui', fallback='missing'))
            self.LOGMODE = self.XY_MODE

            self.graph.setXRange(desc.getfloat('default', 'xmin', fallback=-5),
                                 desc.getfloat('default', 'xmax', fallback=5))

            self.graph.setYRange(desc.getfloat('default', 'ymin', fallback=-5),
                                 desc.getfloat('default', 'ymax', fallback=5))

            self.xvar = desc.get('default', 'xaxis', fallback='')
            self.yvar = desc.get('default', 'yaxis', fallback='')

        ## Set up an arrow
        self.arrow = pg.ArrowItem(pos=(0, 0), angle=-45)
        self.graph.addItem(self.arrow)

        self.text = pg.TextItem("test", anchor=(-.2, 1.1), border='w', fill=(0, 0, 255, 100))
        self.text.setPos(0, 0)
        self.graph.addItem(self.text)

        self.curve = pg.ScatterPlotItem(x=[0], y=[0], pen='w', brush='b', size=self.sizeBox.value(), pxMode=True)
        self.graph.addItem(self.curve)

    def bring_scatter_to_front(self):
        self.graph.removeItem(self.curve)
        self.graph.addItem(self.curve)

    def setup_graph(self, desc: configparser.ConfigParser):
        self.xunits = desc.get('default', 'xunits', fallback='')
        self.yunits = desc.get('default', 'yunits', fallback='')
        self.graph.setLabel('left', desc.get('default', 'ylabel', fallback='Voltage'),
                            units=desc.get('default', 'yunits', fallback='V'), **self.labelStyle)

        self.graph.setYRange(desc.getfloat('default', 'ymin', fallback=-5),
                             desc.getfloat('default', 'ymax', fallback=5))

        self.graph.setLabel('bottom', desc.get('default', 'xlabel', fallback='X'),
                            units=desc.get('default', 'xunits', fallback='V'), **self.labelStyle)

        self.graph.setXRange(desc.getfloat('default', 'xmin', fallback=-5),
                             desc.getfloat('default', 'xmax', fallback=5))

    def clear(self):
        self.pos = 0

        self.xvar = ""
        self.yvar = ""
        if self.text is not None:
            self.graph.removeItem(self.text)
            self.graph.removeItem(self.arrow)

    def evaluate(self, variables):
        if self.LOGMODE == self.TIME_MODE:
            x = time.time() - self.startTime
        else:
            x = eval(self.xvar, variables)
        try:
            y = eval(self.yvar, variables)
        except Exception as e:
            y = 0
            print('err', self.yvar, e)
        self.arrow.setPos(x, y)
        self.text.setPos(x, y)
        self.xdata[self.pos] = x
        self.ydata[self.pos] = y
        self.pos += 1
        if (self.pos == self.trailSize):
            self.pos = 0
        self.curve.setData(x=self.xdata, y=self.ydata, pen='w', brush='b', size=self.sizeBox.value(), pxMode=True)
        if time.time() - self.lastUpdateTime > self.UPDATE_INTERVAL:
            self.text.setText(Measurement(x, self.xunits).format3() + '\n' + Measurement(y, self.yunits).format3())
            self.lastUpdateTime = time.time()
