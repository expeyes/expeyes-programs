# dependencies: python3-pyqt5.qtopengl python3-pyqt5.qtsvg
  
from PyQt5.QtCore import QFile, QSize, Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtSvg import QGraphicsSvgItem

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
  
        self.currentFile = ''
  
        self.svg = SvgView()
  
        fileMenu = QMenu("&File", self)
        openAction = fileMenu.addAction("&Open...")
        openAction.setShortcut("Ctrl+O")
        quitAction = fileMenu.addAction("E&xit")
        quitAction.setShortcut("Ctrl+Q")
  
        self.menuBar().addMenu(fileMenu)
  
  
        openAction.triggered.connect(self.openFile)
        quitAction.triggered.connect(QApplication.instance().quit)
  
        self.setCentralWidget(self.svg)
        self.setWindowTitle("SVG Viewer")
  
    def openFile(self, path=None):
        if not path:
            path, _ = QFileDialog.getOpenFileName(self, "Open SVG File",
                    self.currentFile, "SVG files (*.svg *.svgz *.svg.gz)")
        if path:
            svg_file = QFile(path)
            if not svg_file.exists():
                QMessageBox.critical(self, "Open SVG File",
                        "Could not open file '%s'." % path)
  
                return
  
            self.svg.openFile(svg_file)
  
            self.currentFile = path
            self.setWindowTitle("%s - SVGViewer" % self.currentFile)
  
            self.resize(self.svg.sizeHint() + QSize(80, 80 + self.menuBar().height()))
  
class SvgView(QGraphicsView):
    def __init__(self, parent=None):
        super(SvgView, self).__init__(parent)
  
        self.setViewport(QWidget())
        self.svgItem = None
        self.image = QImage()
  
        self.setScene(QGraphicsScene(self))
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
  
    def openFile(self, svg_file):
        if not svg_file.exists():
            return
  
        s = self.scene()
    
        s.clear()
        self.resetTransform()
  
        self.svgItem = QGraphicsSvgItem(svg_file.fileName())
        self.svgItem.setFlags(QGraphicsItem.ItemClipsToShape)
        self.svgItem.setCacheMode(QGraphicsItem.NoCache)
        self.svgItem.setZValue(0)
    
        s.addItem(self.svgItem)

  
    def wheelEvent(self, event):
        factor = pow(1.2, event.angleDelta().y() / 240.0)
        self.scale(factor, factor)
        event.accept()

if __name__ == '__main__':
  
    import sys
  
    app = QApplication(sys.argv)
  
    window = MainWindow()
    window.openFile('ej1.svg')
    window.show()
    sys.exit(app.exec_())
