import os

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from qgis.core import *
from qgis.PyQt import QtGui, QtWidgets, uic

from .constants import Constants as CONSTANTS

class PrintWindow():
    def __init__(self, printLayout):
        self.ui = uic.loadUi(os.path.join(os.path.dirname(__file__), 'printWindow.ui'))
        self.printLayout = printLayout

        self.setPdfImage(self.printLayout)
        self.initCustomGui()

        self.ui.exec_()

    def makePrintLayoutAsImage(self, printLayout):
        exporter =  QgsLayoutExporter(printLayout)
        img_settings = exporter.ImageExportSettings()
        printLayoutImage = exporter.renderPageToImage(0)
        pdf_settings = exporter.PdfExportSettings()
        exporter.exportToPdf("/Users/kanahiroiguchi/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/ezprinter/test.pdf", pdf_settings)
        return printLayoutImage

    def setPdfImage(self, printLayout):
        printLayoutImage = self.makePrintLayoutAsImage(printLayout)
        scaledImage = printLayoutImage.scaled(400, 400, Qt.KeepAspectRatio)
        self.ui.imageLabel.setPixmap(QtGui.QPixmap.fromImage(scaledImage))

    def initCustomGui(self):
        self.ui.titleLineEdit.returnPressed.connect(self.applyGuiChangeToPrintLayout)
        self.ui.scaleBarCheck.stateChanged.connect(self.addScaleBar)

    def applyGuiChangeToPrintLayout(self):
        printLayout = self.printLayout.clone()
        titleFont = QFont()
        titleFont.setBold(True)

        titleLabel = QgsLayoutItemLabel(printLayout)
        titleLabel.setText(self.ui.titleLineEdit.text())
        titleLabel.setPos(CONSTANTS.PAPER_MARGINS["left"], CONSTANTS.PAPER_MARGINS["top"] - 20)
        titleLabel.setFont(titleFont)
        titleLabel.adjustSizeToText()
        printLayout.addItem(titleLabel)

        self.setPdfImage(printLayout)

    def addScaleBar(self):
        printLayout = self.printLayout.clone()
        projectMap = QgsLayoutItemMap(self.printLayout)
        if self.ui.scaleBarCheck.isChecked():
            page = printLayout.pageCollection().pages()[0]
            paperSize = page.pageSize()

            scaleBar = QgsLayoutItemScaleBar(printLayout)
            scaleBar.setLinkedMap(projectMap)
            scaleBar.applyDefaultSettings()
            scaleBar.applyDefaultSize()
            scaleBar.setNumberOfSegmentsLeft(0)
            scaleBar.setNumberOfSegments (3)
            scaleBar.update()
            scaleBar.setPos(CONSTANTS.PAPER_MARGINS['left'], paperSize.height() - CONSTANTS.PAPER_MARGINS['bottom'] - 15)
            printLayout.addItem(scaleBar)
        self.setPdfImage(printLayout)
