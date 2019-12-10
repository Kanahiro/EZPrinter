from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt, QSize
from qgis.PyQt.QtGui import QIcon, QImage, QPainter, QCursor
from qgis.PyQt.QtWidgets import QAction
from qgis.core import *

class PrintLayout:
    def init(self, project, title="title", subtitle="", attribution="", scale=True, direction=False):
        self.project = project
        self.title = title
        self.subtitle = subtitle
        self.attribution = attribution
        self.scale = scale
        self.direction = direction

    def makePage(self):
        print(self)