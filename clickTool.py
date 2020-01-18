from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtCore import QPoint, Qt, QSize, QRect
from qgis.PyQt.QtGui import QCursor, QPixmap, QImage, QPainter

from .constants import Constants as CONSTANTS

class ClickTool(QgsMapTool):
    def __init__(self, iface, callback, paperSize, printScale, horizontal=False, wideMode=False):
        QgsMapTool.__init__(self,iface.mapCanvas())
        self.iface      = iface
        self.callback   = callback
        self.paperSize = paperSize
        self.printScale = printScale
        self.horizontal = horizontal
        self.wideMode = wideMode
        self.drugging = False

        self.margins = CONSTANTS.PAPER_MARGINS
        if self.wideMode:
            self.margins = CONSTANTS.WIDEMODE_MARGINS

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
        pointTopRight = self.iface.mapCanvas().getCoordinateTransform().toMapPoint(rect.left() + rect.width(), rect.top())
        pointBottomRight = self.iface.mapCanvas().getCoordinateTransform().toMapPoint(rect.left() + rect.width(), rect.top() + rect.height())
        pointBottomLeft = self.iface.mapCanvas().getCoordinateTransform().toMapPoint(rect.left(), rect.top() + rect.height())
        coordinates = {
            "topLeft":pointTopLeft,
            "topRight":pointTopRight,
            "bottomRight":pointBottomRight,
            "bottomLeft":pointBottomLeft
        }
        self.callback(coordinates)
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
        #mili meter of papersize
        width = self.paperSize[0] - self.margins['left'] - self.margins['right']
        height = self.paperSize[1] - self.margins['top'] - self.margins['bottom']
        if self.horizontal:
            width = self.paperSize[1] - self.margins['left'] - self.margins['right']
            height = self.paperSize[0] - self.margins['top'] - self.margins['bottom']

        #pixel calculated by the mili meters, dpi and scale
        zoom = round(self.iface.mapCanvas().scale())
        dpi = self.iface.mapCanvas().mapSettings().outputDpi()
        rectSize = (width * dpi / 25.4 * self.printScale / zoom,
                    height * dpi / 25.4 * self.printScale / zoom)
        print(zoom, dpi, rectSize)
        return rectSize