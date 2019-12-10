from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtCore import QPoint, Qt, QSize, QRect
from qgis.PyQt.QtGui import QCursor, QPixmap, QImage, QPainter

from .constants import Constants as CONSTANTS

class ClickTool(QgsMapTool):
    def __init__(self, iface, callback, paperSize, printScale, horizontal=False, wideMode=True):
        QgsMapTool.__init__(self,iface.mapCanvas())
        self.iface      = iface
        self.callback   = callback
        self.paperSize = paperSize
        self.printScale = printScale
        self.horizontal = horizontal
        self.drugging = False
        self.reloadCursorRectangle()
        return None

    def reloadCursorRectangle(self):
        self.setCursor(QCursor(self.makeRectCursor()))

    def canvasPressEvent(self, e):
        self.drugging = True
        point = QPoint(e.pos().x(),e.pos().y())
        rect = self.makeRectBy(point)
        #convert CANVAS POINTS to MAP COORDINATES
        pointTopLeft = self.iface.mapCanvas().getCoordinateTransform().toMapPoint(rect.left(), rect.top())
        pointBottomRight = self.iface.mapCanvas().getCoordinateTransform().toMapPoint(rect.left() + rect.width(), rect.top() + rect.height())
        self.callback((pointTopLeft, pointBottomRight))
        return None

    #make rectangle same shape to mapcanvas rect, with point
    def makeRectBy(self, point):
        rectSize = self.calcRectSize()
        width = rectSize[0]
        height = rectSize[1]
        rect = QRect(point.x() - width / 2, point.y() - height / 2, width, height)
        return rect

    def makeRectCursor(self):
        rectSize = self.calcRectSize()
        width = rectSize[0]
        height = rectSize[1]
        #make invisible rectangle when rectSize is too large
        if width > 2000:
            width = 0
        if height > 2000:
            height = 0
        image = QImage(QSize(width, height), QImage.Format_ARGB32)
        #fill with a invisible color
        image.fill(0)
        p = QPainter()
        p.begin(image)
        p.drawRect(QRect(0, 0, width - 1, height - 1))
        p.end()
        return QPixmap.fromImage(image)

    def calcRectSize(self):
        width = self.paperSize[0] - CONSTANTS.PAPER_MARGINS['left'] - CONSTANTS.PAPER_MARGINS['right']
        height = self.paperSize[1] - CONSTANTS.PAPER_MARGINS['top'] - CONSTANTS.PAPER_MARGINS['bottom']
        if self.horizontal:
            width = self.paperSize[1] - CONSTANTS.PAPER_MARGINS['left'] - CONSTANTS.PAPER_MARGINS['right']
            height = self.paperSize[0] - CONSTANTS.PAPER_MARGINS['top'] - CONSTANTS.PAPER_MARGINS['bottom']

        zoom = round(self.iface.mapCanvas().scale())
        dpi = self.iface.mapCanvas().mapSettings().outputDpi()
        rectSize = (dpi / 25.4 * width * self.printScale / zoom,
                    dpi / 25.4 * height * self.printScale / zoom)
        return rectSize