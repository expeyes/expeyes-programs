import configparser
import json
import os
import struct
import sys
from functools import partial

import markdown2
import time
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QWidget, \
    QGraphicsPixmapItem, QGraphicsProxyWidget, QInputDialog

import pyqtgraph as pg

from eyes17 import eyes
from interactive.MyTypes import IoTypes, DisplayTypes, Measurement, GraphTypes, IOClassification
from interactive.interactiveControlUtils import xy_logger_controls, NOLOGGING, SWEEPLOGGER, DATALOGGER, NLOGGER
from interactive.myUtils import load_defaults, CustomGraphicsView
from interactive.widgetUtils import miniscope, Gauge, myLabel, DIOINPUT, Datalogger, popupEditor, XYlogger, MyRow, \
    MyExptRow
from layouts import ui_interactive_layout3 as ui_interactive_layout

imageMap = {}
propMap = {}

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "interactive")


class graphConfig():
    mode = GraphTypes.SCOPE
    title = ""
    name = ""
    timeLog = True
    xmin = 0
    duration = 100
    xmax = 100
    ymin = 0
    ymax = 10
    ID = ""
    x = "time"
    y = ""
    autoscaleY = False
    cursor = True
    delay = 20
    NS = 500
    TG = 10
    timebase = 1

    xy = False
    xyy = ""
    xyx = ""
    xCls = None
    yCls = None
    channel_names = []
    hidechannels = []
    channel_legends = []
    channel_units = []
    fitmode = "off"
    xunits = "S"
    yunits = "V"
    xlabel = ""
    ylabel = ""
    attempts = 0
    channels = 0

    threshold = 0.
    maxthreshold = 16.
    selectorStart = 0
    selectorEnd = 0
    automatic = True
    desc = ""

    def __init__(self, ID, desc: configparser.RawConfigParser):
        self.ID = ID
        self.y = ID
        if desc.get('default', 'mode', fallback='') == 'scope':
            self.mode = GraphTypes.SCOPE
        elif desc.has_option('default', 'sweep'):
            self.mode = GraphTypes.XYLOGGER
        elif desc.has_option('default', 'logging'):
            print('making graphconfig data logger')
            self.mode = GraphTypes.LOGGER

        self.xmin = desc.getfloat('default', 'xmin', fallback=self.xmin)
        self.xmax = desc.getfloat('default', 'xmax', fallback=self.xmax)
        self.ymin = desc.getfloat('default', 'ymin', fallback=desc.getfloat('default', 'min', fallback=self.ymin))
        self.ymax = desc.getfloat('default', 'ymax', fallback=desc.getfloat('default', 'max', fallback=self.ymax))

        self.automatic = desc.getboolean('default', 'automatic', fallback=True)
        self.rangeA1 = desc.getboolean('default', 'rangeA1', fallback=False)
        self.rangeA2 = desc.getboolean('default', 'rangeA2', fallback=False)
        self.timeLog = desc.getboolean('default', 'timeLog', fallback=False)
        self.cursor = desc.getboolean('default', 'cursor', fallback=True)
        self.autoscaleY = desc.getboolean('default', 'autoscaleY', fallback=True)
        self.xlabel = desc.get('default', 'xlabel', fallback="time")
        self.xunits = desc.get('default', 'xunits', fallback=self.xunits)
        self.yunits = desc.get('default', 'yunits', fallback=self.yunits)
        self.fitmode = desc.get('default', 'fitmode', fallback="off")
        self.range = desc.getfloat('default', 'range', fallback=10.)
        self.timebase = desc.getint('default', 'timebase', fallback=1)
        self.NS = desc.getint('default', 'NP', fallback=self.NS)
        self.chanlist = []
        if self.mode == GraphTypes.SCOPE:
            if desc.has_option('default', 'ylist'):  # scope channels in list
                self.chanlist = desc.get('default', 'ylist').split("[")[1].split("]")[0].split(",")
            else:
                if desc.has_option('default', 'y1'):
                    self.chanlist.append(desc.get('default', 'y1'))
                if desc.has_option('default', 'y2'):
                    self.chanlist.append(desc.get('default', 'y2'))
                if desc.has_option('default', 'y3'):
                    self.chanlist.append(desc.get('default', 'y3'))
                if desc.has_option('default', 'y4'):
                    self.chanlist.append(desc.get('default', 'y4'))

        elif self.mode == GraphTypes.XYLOGGER:
            print('activated XY mode')
            if not desc.has_option('default', 'xlabel'):
                desc.set('default', 'xlabel', desc.get('default', 'xaxis', fallback='X'))
            if not desc.has_option('default', 'ylabel'):
                desc.set('default', 'ylabel', desc.get('default', 'yaxis', fallback='Y'))

        elif self.mode == GraphTypes.LOGGER:
            print('activated time log graph mode')
            if not desc.has_option('default', 'xlabel'):
                desc.set('default', 'xlabel', desc.get('default', 'xaxis', fallback='time'))
            if not desc.has_option('default', 'ylabel'):
                desc.set('default', 'ylabel', desc.get('default', 'yaxis', fallback=self.ID))

        self.desc = desc

    def get_description(self):
        return self.desc


class Element:
    minValue = 0
    maxValue = 1
    ID = ""
    desc = ""
    x = ""
    y = ""
    TEXT_UPDATE_INTERVAL = 0.3  # mS units
    lastTextUpdateTime = 0
    minOrder = -12
    initNeeded = True
    waitingForData = False

    mux_address = -1
    automatic = True
    getfft = False
    equation = ""
    name = ""
    label = None
    gauge = None
    units = ""
    val = 0
    NS = 500
    TG = 10
    stepsize = 0.01
    IOtype = IoTypes.MISSING
    display = DisplayTypes.TEXT
    busy = False
    renderBlock = False
    state = False
    tristate = False
    error = False
    timeLog = False
    opts = 0
    edgetype = "falling"
    points = 2
    displayGauge = None
    displayLabel = None
    read_input = None
    set_output = None
    myType = IOClassification.MEASURE
    device = None
    graphConf = None
    idparts = []

    def __init__(self, identifier: str, device: eyes, xc: float, yc: float, description: str) -> object:
        self.IOConfig = configparser.RawConfigParser()
        self.device = device
        self.x = xc
        self.y = yc
        self.ID = identifier
        self.desc = description
        self.parse_description()
        self.IOConfig.set('default', 'xcoord', str(xc))
        self.IOConfig.set('default', 'ycoord', str(yc))

        self.minValue = float(self.IOConfig.get('default', 'min', fallback=0))
        self.maxValue = float(self.IOConfig.get('default', 'max', fallback=5e6))
        self.val = float(self.IOConfig.get('default', 'value', fallback=(self.minValue + self.maxValue) / 2))
        self.stepsize = float(self.IOConfig.get('default', 'stepsize', fallback=self.stepsize))
        self.units = self.IOConfig.get('default', 'units', fallback="?")

    def setDevice(self, dev):
        self.device = dev

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def parse_description(self):
        self.IOConfig.read_string('[default]\n' + self.desc)
        self.val = 0

        '''
        This is a graphical block which is defined in an svg file. add the default block parameters from its releveant section in defaults.aiken
        '''

        if propMap.__contains__(self.ID):
            print('blk in propMap. Update original params :', [a for a in self.IOConfig['default'].keys()])
            blkConfig = configparser.RawConfigParser()
            blkConfig.read_string('[default]\n' + propMap[self.ID])
            for a in blkConfig['default']:
                if a not in self.IOConfig['default']:
                    print('heyo',a, blkConfig['default'], blkConfig['default'][a])
                    self.IOConfig.set('default', a, blkConfig['default'][a])
        else:
            self.idparts = self.ID.split(":")
            if self.idparts[0] in ['EQ', 'VAR']:
                self.ID = self.idparts[1]

        if self.IOConfig['default'].__contains__(
                'type'):  # If type is specified, it is a standard block with an svg img
            tp = self.IOConfig.get('default', 'type')
            cmd = self.IOConfig.get('default', 'command', fallback='')
            arg = self.IOConfig.get('default', 'arg1', fallback=None)
            self.val = self.IOConfig.getfloat('default', 'value', fallback=self.val)

            if tp == 'VOLTMETER':
                self.IOtype = IoTypes.VOLTMETER
                self.read_input = partial(self.device.get_voltage, self.IOConfig.get('default', 'arg1', fallback='A1'))
            elif tp == 'ACVOLTMETER':
                self.IOtype = IoTypes.ACVOLTMETER
            elif tp == 'CAPACITANCE':
                self.myType = IOClassification.MEASURE
                self.IOtype = IoTypes.CAPACITANCE
                self.read_input = self.device.get_capacitance
            elif tp == 'DIGITALINPUT':
                self.IOtype = IoTypes.DIGITALINPUT
                if cmd == 'get_resistance':
                    self.read_input = self.device.get_resistance
                elif cmd == 'sr04_distance':
                    self.read_input = self.device.sr04_distance
                elif cmd == 'multi_r2r':
                    self.read_input = partial(self.device.multi_r2r,
                                              self.IOConfig.get('default', 'channel', fallback='IN2'))
            elif tp == 'WAVEGEN':
                self.IOtype = IoTypes.WAVEGEN
                if cmd == 'set_wg':
                    self.set_output = self.device.set_sine
                elif cmd == 'set_sq1':
                    self.set_output = self.device.set_sq1
                elif cmd == 'set_sq1_dc':
                    self.set_output = self.device.set_sq1_dc
                elif cmd == 'set_sq2':
                    self.set_output = self.device.set_sq2
                elif cmd == 'set_sq2_dc':
                    self.set_output = self.device.set_sq2dc
            elif tp == 'VOLTAGESOURCE':
                self.IOtype = IoTypes.VOLTAGESOURCE
                if cmd == 'set_pv1':
                    self.set_output = self.device.set_pv1
                elif cmd == 'set_pv2':
                    self.set_output = self.device.set_pv2
                # elif cmd == 'set_pcs':
                #    self.set_output = self.device.set_pcs
            elif tp == 'BUTTON':
                self.IOtype = IoTypes.BUTTON
            elif tp == 'WAVEGEN':
                self.IOtype = IoTypes.WAVEGEN

        print(self.ID, [a for a in self.IOConfig['default'].keys()])

    def render_gauge(self, parent):
        print(' we need  a gauge for ', self.ID)
        gauge = Gauge(None, self.ID)
        gauge.setObjectName(self.ID)
        gauge.set_MinValue(self.minValue)
        gauge.set_MaxValue(self.maxValue)
        gauge.setStyleSheet("background:#00FFFFFF")
        gauge.setFixedWidth(300)
        gauge.setFixedHeight(300)
        self.display = DisplayTypes.GAUGE
        self.displayGauge = gauge
        # gauge.setFixedWidth(self.IOConfig.getint('default', 'w', fallback=350))
        # gauge.setFixedHeight(self.IOConfig.getint('default', 'h', fallback=350))
        pWidget = QGraphicsProxyWidget()
        pWidget.setWidget(gauge)
        pWidget.setPos(self.x, self.y)

        parent.elementPixmapItems[self.ID] = pWidget
        parent.scene.addItem(pWidget)

    def render_standard_block(self, parent):
        print(' we need a text label for ', self.ID)
        pxm = QPixmap(os.path.join(os.path.join(path, 'widget_thumbs'), imageMap[self.ID]))
        pxmitem = QGraphicsPixmapItem(pxm)
        pxmitem.setTransformationMode(Qt.SmoothTransformation)
        pxmitem.setPos(self.x, self.y)
        parent.scene.addItem(pxmitem)
        parent.elementPixmapItems[self.ID + 'bg'] = pxmitem
        self.display = DisplayTypes.TEXT
        self.render_label(parent)

    def render_label(self, parent):
        labeltext = myLabel()  # QPixmap(os.path.join(os.path.join(path, 'widget_thumbs'), imageMap[self.ID]))
        labeltext.setText("")
        self.displayLabel = labeltext
        pWidget2 = QGraphicsProxyWidget()
        pWidget2.setWidget(labeltext)
        pWidget2.setPos(self.x, self.y)
        parent.scene.addItem(pWidget2)
        parent.elementPixmapItems[self.ID] = pWidget2

        if self.ID in ['PV1', 'PV2', 'WG', 'SQ1', 'SQ2']:
            labeltext.clicked.connect(partial(self.configureOutputController, parent, self.ID))
            labeltext.scrolled.connect(partial(self.label_scrolled, self.ID))

        return labeltext

    def render_element(self, parent):
        # These elements have pre-defined IMAGE blocks.
        if self.ID in imageMap:

            # Show as a gauge. implies do not render the image or label.
            if self.IOConfig.get('default', 'label', fallback='text') == 'gauge':
                self.render_gauge(parent)
                parent.add_variable(self.ID, 0)

            # Render the image button, and a label on top of it to display the value.
            else:
                self.render_standard_block(parent)
                parent.add_variable(self.ID, 0)
        else:
            print('element not gauge, and does not have a render image for text:', self.idparts)
            if self.idparts[0] == 'GRAPH':
                parent.addGraph(self.ID, self.IOConfig)

            elif self.idparts[0] == 'EQ':
                self.render_label(parent)
                if len(self.idparts) >= 2:
                    self.myType = IOClassification.DERIVED
                    self.equation = self.idparts[1]
                    self.displayLabel.setText(self.idparts[1])
                    # parent.add_variable(self.idparts[1], 0)
                if len(self.idparts) >= 3:
                    self.units = self.idparts[2]

            elif self.idparts[0] == 'VAR':
                self.render_label(parent)
                self.name = self.idparts[1]
                self.displayLabel.setStyleSheet("""font-size: 28pt;background-color: transparent;color: red;
                qproperty-alignment: 'AlignVCenter | AlignHCenter';
                """)
                if len(self.idparts) >= 3:
                    self.val = float(self.idparts[2])
                    self.displayLabel.setText(self.idparts[2])
                if len(self.idparts) >= 4:
                    self.units = self.idparts[3]

                parent.add_variable(self.name, self.val)
                self.displayLabel.clicked.connect(partial(parent.edit_var, self.ID))

        # Set the default value for output devices
        if self.set_output is not None and self.device.connected:
            v = self.set_output(self.val)
            print('output set:', self.val, self.ID, v)
            if v is not None:
                self.set_value(v)

        if self.IOConfig.has_option('default', 'sweep'):
            print('adding sweep config', self.ID)
            parent.addGraph(self.ID, self.IOConfig)
        if self.read_input is not None and self.IOConfig.getboolean('default', 'logging', fallback=False) == True:
            print('adding time log config', self.ID)
            parent.addGraph(self.ID, self.IOConfig)

    def label_scrolled(self, ID, event):
        self.set_value(self.val + event.angleDelta().y() * self.stepsize / 5)
        self.set_output(self.val)

    def update_value(self, val):
        self.set_value(val)
        self.set_output(val)

    def configureOutputController(self, parent, ID):
        self.popupEditor = popupEditor(parent, ID, self.minValue, self.maxValue, self.stepsize, self.val,
                                       self.update_value)
        if self.displayGauge is not None:
            self.popupEditor.makePopup(ID, self.displayGauge)
        else:
            self.popupEditor.makePopup(ID, self.displayLabel)

    def set_value(self, val):
        if val < self.minValue:
            val = self.minValue
        elif val > self.maxValue:
            val = self.maxValue

        self.val = val

        if self.display == DisplayTypes.GAUGE:
            self.displayGauge.update_value(val)
        elif self.display == DisplayTypes.TEXT:
            if self.units == "Hz":
                self.displayLabel.setText(Measurement(val, self.units).formattedFrequency())
            elif self.units == "V":
                self.displayLabel.setText(Measurement(val, self.units).formattedVoltage())
            else:
                self.displayLabel.setText(Measurement(val, self.units).format3())

    def eval_equation(self, variables):
        self.displayLabel.setText(Measurement(eval(self.equation, variables), self.units).format3())

    def refresh(self, force=False):
        if self.automatic or force:
            if self.read_input is not None:
                self.val = self.read_input()
                self.set_value(self.val)


def get_png_dimensions(image_path):
    with open(image_path, 'rb') as file:
        header = file.read(24)
    width, height = struct.unpack('!II', header[16:24])
    return width, height


def markdown_to_html(markdown_content):
    # Convert Markdown to HTML
    html_content = markdown2.markdown(markdown_content)
    return html_content


def from_json(json_object, dev):
    elements = {}
    for key in json_object:
        el = json_object[key]
        elmn = Element(el['ID'], dev, el['x'], el['y'], el['desc'])
        elements[elmn.ID] = elmn
    return elements


class Expt(QWidget, ui_interactive_layout.Ui_Form):
    colors = [
        "#FFFFFF",  # White
        "#FF0000",  # Red
        "#00FF00",  # Lime
        "#0000FF",  # Blue
        "#FFFF00",  # Yellow
        "#FF00FF",  # Magenta
        "#00FFFF",  # Cyan
        "#FFA500",  # Orange
        "#FFC0CB",  # Pink
        "#800080",  # Purple
        "#008000",  # Green
        "#FFD700",  # Gold
        "#00CED1",  # DarkTurquoise
        "#FF4500",  # OrangeRed
        "#DA70D6",  # Orchid
        "#FF8C00",  # DarkOrange
        "#FF69B4",  # HotPink
        "#00FA9A",  # MediumSpringGreen
        "#8A2BE2",  # BlueViolet
        "#ADFF2F",  # GreenYellow
    ]

    def __init__(self, device=None):
        super(Expt, self).__init__()
        self.setupUi(self)
        self.samplepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "interactive", "samples")
        self.thumbnailpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "interactive", "thumbs")
        self.setTheme('interactive_styles')
        self.image_extension = '.jpg'

        self.p = device
        self.running = False
        self.graphItems = []
        self.variables = {}
        self.mode = GraphTypes.SCOPE
        self.graphConfs = []
        self.activeGraphConf = -1
        self.image_path = None
        self.json_path = None
        self.record_path = None
        self.record_conf = None
        self.controls = None

        global propMap, imageMap
        self.raster_width = None
        self.raster_height = None
        with open(os.path.join(path, "defaults.aiken"), 'rb') as file:
            buffer = file.read()
            propMap, imageMap = load_defaults(buffer)

        self.oscilloscope = None
        self.data_logger = None
        self.xy_logger = None

        self.setWindowTitle('Interactive Schematic')
        self.setGeometry(100, 100, 400, 400)
        #self.vsplit.setSizes([300, 400])
        self.vsplit.setStretchFactor(5, 3)

        self.controlsFrame.setVisible(False)
        # Create a QVBoxLayout and a QWidget as the central widget

        self.scene = QGraphicsScene(self)
        self.view = CustomGraphicsView(self.scene)
        self.schematicLayout.addWidget(self.view)

        self.elementPixmapItems = {}
        self.elements = {}
        self.subcatScroll.setVisible(False)

        self.loadSchematic(os.path.join(self.samplepath, "Getting Started", "Lemon_Cell"))
        if os.path.exists(self.samplepath):
            try:
                self.setStyleSheet(
                    open(os.path.join(os.path.dirname(__file__), "layouts/style.qss"), "r").read())
            except Exception as e:
                print('stylesheet missing. ', e)
            self.schematicsPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'interactive')

            with open(os.path.join(self.samplepath, 'experiments.json')) as expts:
                self.expts = json.loads(expts.read())

            print(self.expts)

            # load_project_structure(self.samplepath, self.thumbnailpath, self.directoryBrowser)
            self.load_categories(self.samplepath, self.thumbnailpath, self.expts)

        self.startTime = time.time()
        self.interval = 0.1  # Seconds
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_everything)
        self.timer.start(2)
        self.running = True
        self.webView.loadStarted.connect(self.webPageLoading)
        self.webView.loadProgress.connect(self.webPageProgress)
        self.webView.loadFinished.connect(self.webPageLoaded)
        self.webPageProgressBar.setVisible(False)

    def webPageLoading(self):
        self.webPageProgressBar.setVisible(True)
    def webPageProgress(self, p):
        self.webPageProgressBar.setValue(p)
    def webPageLoaded(self):
        self.webPageProgressBar.setVisible(False)

    def addOscilloscope(self):
        self.clearPlotLayout()
        if self.oscilloscope is None:
            self.oscilloscope = miniscope(None, self.p)
        self.plotLayout.addWidget(self.oscilloscope)

    def addDataLogger(self):
        self.clearPlotLayout()
        if self.data_logger is None:
            self.data_logger = Datalogger()
        self.plotLayout.addWidget(self.data_logger)

    def addXYLogger(self):
        self.clearPlotLayout()
        if self.xy_logger is None:
            self.xy_logger = XYlogger()
        self.plotLayout.addWidget(self.xy_logger)

    def clearPlotLayout(self):
        if self.oscilloscope is not None:
            self.oscilloscope.setParent(None)
            self.oscilloscope = None
        if self.data_logger is not None:
            self.data_logger.setParent(None)
            self.data_logger= None
            #self.plotLayout.removeWidget(self.data_logger)
        if self.xy_logger is not None:
            self.xy_logger.setParent(None)
            self.xy_logger= None
            #self.plotLayout.removeWidget(self.xy_logger)

    def setTheme(self, theme):
        self.setStyleSheet("")
        self.setStyleSheet(open(os.path.join(self.samplepath, theme + ".qss"), "r").read())
        print('Theme set to ', os.path.join(self.samplepath, theme + ".qss"))

    def setDialogTheme(self, theme, item):
        item.setStyleSheet("")
        item.setStyleSheet(open(os.path.join(self.samplepath, theme + ".qss"), "r").read())
        print(str(item)+' Theme set to ', os.path.join(self.samplepath, theme + ".qss"))

    def load_categories(self, startpath, thumbpath, exptjson):
        for cat in exptjson:
            catdeets = exptjson[cat]
            print('DEETS:', catdeets)
            name = catdeets['image'].split('.')[0]
            clickevent = partial(self.load_subcategory, startpath, catdeets['files'], catdeets['directory'])
            catrow = MyRow(name, catdeets['description'], os.path.join(startpath, catdeets['image']),
                           catdeets['directory'], clickevent)
            self.categoryLayout.addWidget(catrow)

    exptCards = []
    activeCategory = None

    def load_subcategory(self, startpath, files, directory, ev):
        self.setTheme('interactive_styles')

        if (directory == self.activeCategory):
            self.activeCategory = None
            self.subcatScroll.setVisible(False)
        else:
            self.subcatScroll.setVisible(True)
            self.activeCategory = directory

        for a in self.exptCards:
            self.subcategoryLayout.removeWidget(a)
        self.exptCards = []
        self.subcategoryLabel.setText(directory)
        for fname in files:
            desc = files[fname]
            name = fname.split('.')[0].replace(' ', '_')  # Replcae spaces with _ for python files.
            clickevent = partial(self.load_expt, os.path.join(startpath, directory, name))
            if os.path.exists(os.path.join(self.thumbnailpath, name + '.jpg')):
                catrow = MyExptRow(name, desc, os.path.join(self.thumbnailpath, name + '.jpg'), directory, clickevent)
            elif os.path.exists(os.path.join(self.samplepath, directory, name + '.png')):
                catrow = MyExptRow(name, desc, os.path.join(self.samplepath, directory, name + '.png'), directory,
                                   clickevent)
            else:
                print('missing thumbnail')
                catrow = MyExptRow(name, desc, os.path.join(self.samplepath, directory, name + '.png'), directory,
                                   clickevent)
            self.subcategoryLayout.addWidget(catrow)
            self.exptCards.append(catrow)


    def add_variable(self, name, val):
        self.variables[name] = val

    def edit_var(self, ID):
        cls = self.elements[ID]
        print('edit ', ID, cls.val)
        val, ok = QInputDialog.getDouble(self, "Edit Value",
                                         'Set a new value for ' + ID,
                                         cls.val, cls.minValue, cls.maxValue)
        if ok:
            cls.set_value(val)

    def update_everything(self):
        if not self.p.connected or not self.running:
            return

        if self.mode == GraphTypes.SCOPE and self.oscilloscope is not None:
            v = self.oscilloscope.read()
        else:
            # Allow automated recording options to set next output
            if self.controls is not None:  # Automated recording in progress
                if self.controls.LOGTYPE == SWEEPLOGGER and self.controls.running:
                    self.controls.next_value()

            # Make any measurements
            for a in self.elements:
                if self.elements[a].read_input is not None:
                    self.elements[a].refresh()
                    if self.mode == GraphTypes.LOGGER:
                        # print('log', self.elements[a].val)
                        self.data_logger.insert_value(a, self.elements[a].val)
                    if self.mode == GraphTypes.XYLOGGER:
                        self.xy_logger.evaluate(self.variables)

                # Copy latest values to variable list.
                if self.elements[a].myType != IOClassification.DERIVED:  # Equation.
                    self.variables[a] = self.elements[a].val
                else:
                    self.elements[a].eval_equation(self.variables)

            # Let automated recording options evaluate variables and plot .
            if self.controls is not None:  # Automated recording in progress
                if self.controls.LOGTYPE == SWEEPLOGGER and self.controls.running:
                    self.controls.evaluate(self.variables)


    def add_logger_item(self, name, minimum, maximum):
        self.data_logger.add_field(name, minimum, maximum)

    def show_directory(self):
        self.directoryFrame.setVisible(True)


    def load_expt(self, path, ev):
        print(path, ev)
        self.activeCategory = None
        self.subcatScroll.setVisible(False)

        self.filenameLabel.setText(path)

        if os.path.exists(path + self.image_extension):
            self.scene.clear()
            self.loadSchematic(path)
        else:
            return

        if os.path.exists(path + '.help'):
            self.loadHelp(path + '.help')
            self.webFrame.setVisible(True)
            self.vsplit.setStretchFactor(5, 3)
        else:
            self.webFrame.setVisible(False)

        # self.directoryFrame.setVisible(False)

    def loadHelp(self, fname):
        with open(fname, 'r') as helpfile:
            self.webView.setHtml(markdown_to_html(helpfile.read()))

    def loadSchematic(self, title):
        self.mode = GraphTypes.SCOPE

        if self.data_logger is not None:
            self.data_logger.init_fields()
        self.elements.clear()
        self.variables.clear()
        if self.xy_logger is not None:
            self.xy_logger.clear()
        self.elementPixmapItems.clear()
        self.graphConfs = []
        self.activeGraphConf = -1
        self.image_path = title + self.image_extension
        self.json_path = title + '.json'
        self.record_path = title + '.record'
        self.raster_width, self.raster_height = get_png_dimensions(self.image_path)

        self.schematicpixmap = QPixmap(self.image_path)
        self.schematicpixmapitem = QGraphicsPixmapItem(self.schematicpixmap)
        self.schematicpixmapitem.setTransformationMode(Qt.SmoothTransformation)
        self.scene.addItem(self.schematicpixmapitem)

        with open(self.json_path, 'r') as file:
            self.elements = from_json(json.load(file), self.p)

        print(self.elements.keys())
        for a in self.elements:
            cls = self.elements[a]
            print('Render Element', cls.ID)
            print(self.json_path, cls.ID, cls.IOConfig.sections())
            cls.render_element(self)

        if self.controls is not None:
            self.controls.setParent(None)


        self.controlsFrame.setVisible(False)

        if os.path.exists(self.record_path):
            print('record path', self.record_path)
            self.controlsFrame.setVisible(True)
            with open(self.record_path, 'r') as file:
                self.record_conf = configparser.RawConfigParser()
                self.record_conf.read(self.record_path)
                print('record configuration', self.record_conf.sections())
                self.controls = None
                tp = self.record_conf.get('default', 'ui', fallback='')
                if tp == 'datalogger':  # Y vs Time
                    self.LOGTYPE = DATALOGGER
                    self.controls = xy_logger_controls(self, self.record_conf, self.elements)

                elif tp == 'samplelogger':  # N vs Time
                    self.LOGTYPE = NLOGGER

                elif tp == 'sweeplogger':  # X vs Y with sweeping parameter.
                    self.LOGTYPE = SWEEPLOGGER
                    self.controls = xy_logger_controls(self, self.record_conf, self.elements)

                self.setDialogTheme('new',self.controls)
                if self.controls is not None:
                    print('initializing self.controls .....', list(self.record_conf['default']))
                    self.controls.init.connect(self.toggle_recording)
                    self.controls.newdata.connect(self.newdata)
                    #self.controlsLayout.addWidget(self.controls)
                    #self.controls.show()
                    # Inform X vs Y logger of the controller in charge
                    if self.xy_logger is not None:
                        self.xy_logger.setup(self.record_conf)
        else:
            print('systematic recording unavailable!')

        self.configureGraph()
        print(self.elementPixmapItems)
        self.running = True
        if self.oscilloscope is not None:
            self.oscilloscope.scopeBusy = False

    def showControls(self):
        print('show ', self.LOGTYPE)
        if self.controls is not None:
            px = self.controls.parent().geometry().x()
            pw = self.controls.parent().width()
            py = self.controls.parent().geometry().y()
            dw = self.controls.width()
            dh = self.controls.height()
            self.controls.setGeometry(px+pw-dw, py , dw, dh)
            self.controls.show()

    def toggle_recording(self):
        if self.controls.LOGTYPE == SWEEPLOGGER and self.record_conf.has_option('default', 'output'):
            self.sweepElement = self.controls.sweepElement
            print('configuring recorindg..:', self.sweepElement, self.elements.keys())
            if self.sweepElement in self.elements:

                # Copy equation values from the X vs Y graph if it exists
                if self.xy_logger is not None:
                    self.xy_logger.setup_graph(self.record_conf)
                    if self.controls.xequation == '':
                        self.controls.xequation = self.xy_logger.xvar
                    if self.controls.yequation == '':
                        self.controls.yequation = self.xy_logger.yvar
                self.elements[self.sweepElement].update_value(self.controls.currentSweepValue)

                print('configuring sweep for:', self.controls.sweepElement, self.controls.xequation,
                      self.controls.yequation)

    def newdata(self, num, x, y):
        if self.controls is not None and self.controls.LOGTYPE == SWEEPLOGGER and self.xy_logger is not None:
            if num == -1:
                for a in self.graphItems:
                    self.xy_logger.graph.removeItem(a)
            else:
                self.graphItems.append(
                    self.xy_logger.graph.plot(x, y, name=str('#' + str(num)), pen=pg.mkPen(self.colors[num], width=3)))
                l = pg.TextItem(text=str('#' + str(num)), color=self.colors[num])
                l.setPos(x[-1], y[-1])
                self.xy_logger.graph.addItem(l)
                self.graphItems.append(l)
                self.xy_logger.bring_scatter_to_front()

    def addGraph(self, ID, desc):
        cnf = graphConfig(ID, desc)
        self.graphConfs.append(cnf)
        self.activeGraphConf += 1

        if cnf.mode == GraphTypes.SCOPE:
            self.addOscilloscope()
        elif cnf.mode == GraphTypes.LOGGER:
            self.addDataLogger()
        elif cnf.mode == GraphTypes.XYLOGGER:
            self.addXYLogger()

    def configureGraph(self):
        if self.activeGraphConf == -1:  # Graph option not available
            return
        cnf = self.graphConfs[self.activeGraphConf]
        print('setting up graph tabs', self.activeGraphConf, self.graphConfs, cnf.mode)
        desc = cnf.desc
        ylabel = desc.get('default', 'ylabel', fallback='')
        self.mode = cnf.mode
        if cnf.mode == GraphTypes.LOGGER and self.data_logger is not None:
            print('setting up data logger------------------------------')

            if desc.has_option('default', 'selectorStart'):
                spread = cnf.xmax - cnf.xmin
                st = desc.getfloat('default', 'selectorStart') * spread
                end = cnf.xmin + desc.getfloat('default', 'selectorEnd') * spread
                self.data_logger.region.setRegion([st, end])

            self.data_logger.setup(cnf.desc)
            self.add_logger_item(cnf.ID, cnf.ymin, cnf.ymax)

            # Also inform XY Logger
            # cnf.desc.set('default',xvar,desc.get('default','ID'))
            # self.xy_logger.setup(cnf.desc)
        elif cnf.mode == GraphTypes.XYLOGGER and self.xy_logger is not None:
            print('setting up XY logger')
            self.addXYLogger()
            self.xy_logger.setup(cnf.desc)

        elif cnf.mode == GraphTypes.SCOPE and self.oscilloscope is not None:
            print('setting up Oscilloscope')
            chans = cnf.chanlist
            ylabel = ','.join(chans)
            if len(chans) > 0:
                self.oscilloscope.A1Box.setChecked(True)
                self.oscilloscope.A1Map.setCurrentIndex(self.p.allAnalogChannels.index(chans[0]))
            if len(chans) > 1:
                if chans[1] == "A2":
                    self.oscilloscope.A2Box.setChecked(True)
                else:
                    print('need to add derived channel', chans[1])
            if len(chans) > 2:
                if chans[2] == "A3":
                    self.oscilloscope.A3Box.setChecked(True)
                else:
                    print('need to add derived channel', chans[2])
            if len(chans) > 3:
                if chans[3] == "MIC":
                    self.oscilloscope.MICBox.setChecked(True)
                else:
                    print('need to add derived channel', chans[3])

            for a in self.oscilloscope.fitSelCB:
                if desc.get('default', 'fitmode', fallback="off") == "sine":
                    a.setChecked(True)
                else:
                    a.setChecked(False)
            print(cnf.ymin, cnf.ymax)
            self.oscilloscope.plot.setYRange(cnf.ymin, cnf.ymax)
            self.oscilloscope.timebaseSlider.setValue(cnf.timebase)
            # if desc.c

            if desc.has_option('default', 'selectorStart'):
                spread = cnf.xmax - cnf.xmin
                st = desc.getfloat('default', 'selectorStart') * spread
                end = cnf.xmin + desc.getfloat('default', 'selectorEnd') * spread
                print('range', [st, end], self.oscilloscope.region.getRegion())

            if desc.has_option('default', 'trigger_channel'):
                tc = desc.get('default', 'trigger_channel')
                print('triggering on ', tc)
                if tc == 'y1':
                    self.oscilloscope.trigBox.setCurrentIndex(0)
                elif tc == 'y2':
                    self.oscilloscope.trigBox.setCurrentIndex(1)
                elif tc == 'y3':
                    self.oscilloscope.trigBox.setCurrentIndex(2)
                elif tc == 'y4':
                    self.oscilloscope.trigBox.setCurrentIndex(3)
            if desc.has_option('default', 'trigger_level'):
                tl = desc.getfloat('default', 'trigger_level')
                self.oscilloscope.trigSlider.setValue(int(tl / 10))

                # self.oscilloscope.region.setRegion([st,end])

            self.oscilloscope.plot.getPlotItem().setLabel('left', ylabel,
                                                          cnf.yunits)  # p5.setLabel('bottom', 'Time', 's')
            self.oscilloscope.plot.getPlotItem().setLabel('bottom', cnf.xlabel, cnf.xunits)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    from eyes17 import eyes

    p = eyes.open()
    window = Expt(p)
    window.show()

    sys.exit(app.exec_())
