from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400

class PrintWindow(QDialog):
    def __init__(self, parent=None):
        super(PrintWindow, self).__init__(parent)
        self.setGeometry(500,500,WINDOW_WIDTH,WINDOW_HEIGHT)

    def show(self):
        self.exec_()