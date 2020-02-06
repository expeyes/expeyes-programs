#!/usr/bin/env python

###
# Author: Stefan Holstein
# inspired by: https://github.com/Werkov/PyQt4/blob/master/examples/widgets/analogclock.py
# Thanks to https://stackoverflow.com/
#

# Adapted by jithinbp@gmail.com for the expeyes package
###

import math
import sys
if sys.version_info.major==3:
	from PyQt5 import QtGui, QtCore, QtWidgets
else:
	from PyQt4 import QtGui, QtCore
	from PyQt4 import QtGui as QtWidgets

class Gauge(QtWidgets.QWidget):
	valueChanged = QtCore.pyqtSignal(float)

	def __init__(self, parent=None,name=''):
		super(Gauge, self).__init__(parent)
		self.decimals=True

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
		self.value_needle_snapzone = 0.05
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
		self.set_scale_polygon_colors([[.00, QtCore.Qt.red],
									 [.1, QtCore.Qt.yellow],
									 [.15, QtCore.Qt.green],
									 [1, QtCore.Qt.transparent]])

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
		self.initial_title_fontsize = 16
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

		self.change_value_needle_style([QtGui.QPolygon([
			QtCore.QPoint(4, 30),
			QtCore.QPoint(-4, 30),
			QtCore.QPoint(-2, - self.widget_diameter / 2 * self.needle_scale_factor),
			QtCore.QPoint(0, - self.widget_diameter / 2 * self.needle_scale_factor - 6),
			QtCore.QPoint(2, - self.widget_diameter / 2 * self.needle_scale_factor)
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

	def update_value(self, value, mouse_controlled = False):
		if value <= self.value_min:
			self.value = self.value_min
		elif value >= self.value_max:
			self.value = self.value_max
		else:
			self.value = value
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

	def set_enable_Needle_Polygon(self, enable = True):
		self.enable_Needle_Polygon = enable

		if not self.use_timer_event:
			self.update()

	def set_enable_ScaleText(self, enable = True):
		self.enable_scale_text = enable

		if not self.use_timer_event:
			self.update()


	def set_enable_barGraph(self, enable = True):
		self.enable_barGraph = enable

		if not self.use_timer_event:
			self.update()

	def set_enable_value_text(self, enable = True):
		self.enable_value_text = enable

		if not self.use_timer_event:
			self.update()

	def set_enable_title_text(self, enable = True):
		self.enable_title_text = enable

		if not self.use_timer_event:
			self.update()


	def set_enable_CenterPoint(self, enable = True):
		self.enable_CenterPoint = enable

		if not self.use_timer_event:
			self.update()

	def set_enable_filled_Polygon(self, enable = True):
		self.enable_filled_Polygon = enable

		if not self.use_timer_event:
			self.update()

	def set_enable_big_scaled_grid(self, enable = True):
		self.enable_big_scaled_marker = enable

		if not self.use_timer_event:
			self.update()

	def set_enable_fine_scaled_marker(self, enable = True):
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
			self.scale_polygon_colors = [[.0, QtCore.Qt.transparent]]
		else:
			self.scale_polygon_colors = [[.0, QtCore.Qt.transparent]]

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
		n = 360     # angle steps size for full circle
		# changing n value will causes drawing issues
		w = 360 / n   # angle per step
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

		for i in range(lenght+1):                                              # add the points of polygon
			t = w * i + start - self.angle_offset
			x = outer_radius * math.cos(math.radians(t))
			y = outer_radius * math.sin(math.radians(t))
			polygon_pie.append(QtCore.QPointF(x, y))
		# create inner circle line from "start + lenght"-angle to "start"-angle
		for i in range(lenght+1):                                              # add the points of polygon
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
			# Koordinatenursprung in die Mitte der Flaeche legen
			painter_filled_polygon.translate(self.width() / 2, self.height() / 2)

			painter_filled_polygon.setPen(QtCore.Qt.NoPen)

			self.pen.setWidth(outline_pen_with)
			if outline_pen_with > 0:
				painter_filled_polygon.setPen(self.pen)

			colored_scale_polygon = self.create_polygon_pie(
				((self.widget_diameter / 2) - (self.pen.width() / 2)) * self.gauge_color_outer_radius_factor,
				(((self.widget_diameter / 2) - (self.pen.width() / 2)) * self.gauge_color_inner_radius_factor),
				self.scale_angle_start_value, self.scale_angle_size)

			gauge_rect = QtCore.QRect(QtCore.QPoint(0, 0), QtCore.QSize(self.widget_diameter / 2 - 1, self.widget_diameter - 1))
			grad = QtGui.QConicalGradient(QtCore.QPointF(0, 0), - self.scale_angle_size - self.scale_angle_start_value +
									self.angle_offset - 1)

			# todo definition scale color as array here
			for eachcolor in self.scale_polygon_colors:
				grad.setColorAt(eachcolor[0], eachcolor[1])
			# grad.setColorAt(.00, QtCore.Qt.red)
			# grad.setColorAt(.1, QtCore.Qt.yellow)
			# grad.setColorAt(.15, QtCore.Qt.green)
			# grad.setColorAt(1, QtCore.Qt.transparent)
			painter_filled_polygon.setBrush(grad)
			# self.brush = QBrush(QtGui.QColor(255, 0, 255, 255))
			# painter_filled_polygon.setBrush(self.brush)
			painter_filled_polygon.drawPolygon(colored_scale_polygon)
			# return painter_filled_polygon

	###############################################################################################
	# Scale Marker
	###############################################################################################

	def draw_big_scaled_markter(self):
		my_painter = QtGui.QPainter(self)
		my_painter.setRenderHint(QtGui.QPainter.Antialiasing)
		# Koordinatenursprung in die Mitte der Flaeche legen
		my_painter.translate(self.width() / 2, self.height() / 2)

		# my_painter.setPen(QtCore.Qt.NoPen)
		self.pen = QtGui.QPen(QtGui.QColor(0, 0, 0, 255))
		self.pen.setWidth(2)
		# # if outline_pen_with > 0:
		my_painter.setPen(self.pen)

		my_painter.rotate(self.scale_angle_start_value - self.angle_offset)
		steps_size = (float(self.scale_angle_size) / float(self.scala_main_count))
		scale_line_outer_start = self.widget_diameter/2
		scale_line_lenght = (self.widget_diameter / 2) - (self.widget_diameter / 20)
		# print(stepszize)
		for i in range(self.scala_main_count+1):
			my_painter.drawLine(scale_line_lenght, 0, scale_line_outer_start, 0)
			my_painter.rotate(steps_size)

	def create_scale_marker_values_text(self):
		painter = QtGui.QPainter(self)
		# painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
		painter.setRenderHint(QtGui.QPainter.Antialiasing)

		# Koordinatenursprung in die Mitte der Flaeche legen
		painter.translate(self.width() / 2, self.height() / 2)
		# painter.save()
		font = QtGui.QFont(self.scale_fontname, self.scale_fontsize)
		fm = QtGui.QFontMetrics(font)

		pen_shadow = QtGui.QPen()

		pen_shadow.setBrush(self.ScaleValueColor)
		painter.setPen(pen_shadow)

		text_radius_factor = 0.8
		text_radius = self.widget_diameter/2 * text_radius_factor

		scale_per_div = ((self.value_max - self.value_min) / self.scala_main_count)

		angle_distance = (float(self.scale_angle_size) / float(self.scala_main_count))
		for i in range(self.scala_main_count + 1):
			# text = str(int((self.value_max - self.value_min) / self.scala_main_count * i))
			val = self.value_min + scale_per_div * i
			if abs(val)>1e6 or (abs(val)<1e-1 and val!=0):
				text = str('%.1e'%(val))
			else:
				if self.decimals: text = str('%.1f'%(val))
				else: text = str('%d'%(int(val)))
			w = fm.width(text) + 1
			h = fm.height()
			painter.setFont(QtGui.QFont(self.scale_fontname, self.scale_fontsize))
			angle = angle_distance * i + float(self.scale_angle_start_value - self.angle_offset)
			x = text_radius * math.cos(math.radians(angle))
			y = text_radius * math.sin(math.radians(angle))
			# print(w, h, x, y, text)
			text = [x - int(w/2), y - int(h/2), int(w), int(h), QtCore.Qt.AlignCenter, text]
			painter.drawText(text[0], text[1], text[2], text[3], text[4], text[5])
		# painter.restore()

	def create_fine_scaled_marker(self):
		#  Description_dict = 0
		my_painter = QtGui.QPainter(self)

		my_painter.setRenderHint(QtGui.QPainter.Antialiasing)
		# Koordinatenursprung in die Mitte der Flaeche legen
		my_painter.translate(self.width() / 2, self.height() / 2)

		my_painter.setPen(QtCore.Qt.black)
		my_painter.rotate(self.scale_angle_start_value - self.angle_offset)
		steps_size = (float(self.scale_angle_size) / float(self.scala_main_count * self.scala_subdiv_count))
		scale_line_outer_start = self.widget_diameter/2
		scale_line_lenght = (self.widget_diameter / 2) - (self.widget_diameter / 40)
		for i in range((self.scala_main_count * self.scala_subdiv_count)+1):
			my_painter.drawLine(scale_line_lenght, 0, scale_line_outer_start, 0)
			my_painter.rotate(steps_size)

	def create_values_text(self):
		painter = QtGui.QPainter(self)
		# painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
		painter.setRenderHint(QtGui.QPainter.Antialiasing)

		# Koordinatenursprung in die Mitte der Flaeche legen
		painter.translate(self.width() / 2, self.height() / 2)
		# painter.save()
		# xShadow = 3.0
		# yShadow = 3.0
		font = QtGui.QFont(self.value_fontname, self.value_fontsize)
		fm = QtGui.QFontMetrics(font)

		pen_shadow = QtGui.QPen()

		pen_shadow.setBrush(self.DisplayValueColor)
		painter.setPen(pen_shadow)

		text_radius = self.widget_diameter / 2 * self.text_radius_factor

		# angle_distance = (float(self.scale_angle_size) / float(self.scala_main_count))
		# for i in range(self.scala_main_count + 1):
		if self.decimals: text = str('%.2f'%(self.value))
		else: text = str('%d'%(self.value))
		w = fm.width(text) + 1
		h = fm.height()
		painter.setFont(QtGui.QFont(self.value_fontname, self.value_fontsize))

		# Mitte zwischen Skalenstart und Skalenende:
		# Skalenende = Skalenanfang - 360 + Skalenlaenge
		# Skalenmitte = (Skalenende - Skalenanfang) / 2 + Skalenanfang
		angle_end = float(self.scale_angle_start_value + self.scale_angle_size - 360)
		angle = (angle_end - self.scale_angle_start_value) / 2 + self.scale_angle_start_value

		x = text_radius * math.cos(math.radians(angle))
		y = text_radius * math.sin(math.radians(angle))
		# print(w, h, x, y, text)
		text = [x - int(w/2), y - int(h/2), int(w), int(h), QtCore.Qt.AlignCenter, text]
		painter.drawText(text[0], text[1], text[2], text[3], text[4], text[5])
		# painter.restore()



	def create_title_text(self):
		painter = QtGui.QPainter(self)
		# painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
		painter.setRenderHint(QtGui.QPainter.Antialiasing)

		painter.translate(self.width() / 2, 0)
		font = QtGui.QFont(self.title_fontname, self.title_fontsize)
		fm = QtGui.QFontMetrics(font)
		pen_shadow = QtGui.QPen()
		pen_shadow.setBrush(self.DisplayTitleColor)
		painter.setPen(pen_shadow)
		text_radius = self.widget_diameter / 2 * self.text_radius_factor

		text = self.title_text
		w = fm.width(text) + 1
		h = fm.height()
		painter.setFont(QtGui.QFont(self.title_fontname, self.title_fontsize))

		angle_end = float(self.scale_angle_start_value + self.scale_angle_size - 360)
		angle = (angle_end - self.scale_angle_start_value) / 2 + self.scale_angle_start_value

		x = text_radius * math.cos(math.radians(angle))
		y = text_radius * math.sin(math.radians(angle))
		# print(w, h, x, y, text)
		text = [x - int(w/2), y , int(w), int(h), QtCore.Qt.AlignCenter, text]
		painter.drawText(text[0], text[1], text[2], text[3], text[4], text[5])
		# painter.restore()


	def draw_big_needle_center_point(self, diameter=30):
		painter = QtGui.QPainter(self)
		# painter.setRenderHint(QtGui.QtGui.QPainter.HighQualityAntialiasing)
		painter.setRenderHint(QtGui.QPainter.Antialiasing)

		# Koordinatenursprung in die Mitte der Flaeche legen
		painter.translate(self.width() / 2, self.height() / 2)
		painter.setPen(QtCore.Qt.NoPen)
		# painter.setPen(QtCore.Qt.NoPen)
		painter.setBrush(self.CenterPointColor)
		# diameter = diameter # self.widget_diameter/6
		painter.drawEllipse(int(-diameter / 2), int(-diameter / 2), int(diameter), int(diameter))

	def draw_needle(self):
		painter = QtGui.QPainter(self)
		#painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
		painter.setRenderHint(QtGui.QPainter.Antialiasing)
		# Koordinatenursprung in die Mitte der Flaeche legen
		painter.translate(self.width() / 2, self.height() / 2)
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


