import os

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from qgis.core import *
from qgis.PyQt import QtGui, QtWidgets, uic

from .constants import Constants as CONSTANTS

class PrintWindow():
    def __init__(self, printLayout, projectMap):
        self.ui = uic.loadUi(os.path.join(os.path.dirname(__file__), 'printWindow.ui'))
        self.printLayout = printLayout
        self.projectMap = projectMap

        self.setPdfImage(self.printLayout)
        self.initCustomGui()

        self.ui.exec_()

    def makeImageBy(self, printLayout):
        exporter =  QgsLayoutExporter(printLayout)
        img_settings = exporter.ImageExportSettings()
        printLayoutImage = exporter.renderPageToImage(0)
        pdf_settings = exporter.PdfExportSettings()
        exporter.exportToPdf("/Users/kanahiroiguchi/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/ezprinter/test.pdf", pdf_settings)
        return printLayoutImage

    def setPdfImage(self, printLayout):
        printLayoutImage = self.makeImageBy(printLayout)
        scaledImage = printLayoutImage.scaled(400, 400, Qt.KeepAspectRatio)
        self.ui.imageLabel.setPixmap(QtGui.QPixmap.fromImage(scaledImage))

    def initCustomGui(self):
        self.ui.titleLineEdit.editingFinished.connect(self.applyGuiChangeToPrintLayout)
        self.ui.scaleBarCheck.stateChanged.connect(self.applyGuiChangeToPrintLayout)
        self.ui.subtextLineEdit.editingFinished.connect(self.applyGuiChangeToPrintLayout)

    def applyGuiChangeToPrintLayout(self):
        printLayout = self.printLayout.clone()

        titleLabel = self.makeTitleLabel()
        printLayout.addItem(titleLabel)

        if self.ui.scaleBarCheck.isChecked():
            scaleBar = self.makeScaleBar()
            printLayout.addItem(scaleBar)

        subtextLabel = self.makeSubtextLabel()
        printLayout.addItem(subtextLabel)

        self.setPdfImage(printLayout)

    def makeTitleLabel(self):
        titleFont = QFont()
        titleFont.setPointSize(CONSTANTS.TITLE_FONTSIZE)
        titleFont.setBold(True)

        titleLabel = QgsLayoutItemLabel(self.printLayout)
        titleLabel.setText(self.ui.titleLineEdit.text())
        titleLabel.setPos(CONSTANTS.PAPER_MARGINS["left"], CONSTANTS.PAPER_MARGINS["top"] - CONSTANTS.TITLE_FONTSIZE / 2)
        titleLabel.setFont(titleFont)
        titleLabel.adjustSizeToText()
        return titleLabel

    def makeScaleBar(self):
        page = self.printLayout.pageCollection().pages()[0]
        paperSize = page.pageSize()

        scaleBar = QgsLayoutItemScaleBar(self.printLayout)
        scaleBar.setLinkedMap(self.projectMap)
        scaleBar.applyDefaultSettings()
        scaleBar.applyDefaultSize()
        scaleBar.setNumberOfSegmentsLeft(0)
        scaleBar.setNumberOfSegments (3)
        scaleBar.update()
        scaleBar.setPos(CONSTANTS.PAPER_MARGINS['left'], paperSize.height() - CONSTANTS.PAPER_MARGINS['bottom'] - 15)

        return scaleBar

    def makeSubtextLabel(self):
        page = self.printLayout.pageCollection().pages()[0]
        paperSize = page.pageSize()

        subtextFont = QFont()
        subtextFont.setPointSize(CONSTANTS.SUBTEXT_FONTSIZE)
        subtextFont.setBold(True)

        subtextLabel = QgsLayoutItemLabel(self.printLayout)
        subtextLabel.setText(self.ui.subtextLineEdit.text())
        subtextLabel.setPos(CONSTANTS.PAPER_MARGINS["left"], paperSize.height() - CONSTANTS.PAPER_MARGINS['bottom'])
        subtextLabel.setFont(subtextFont)
        subtextLabel.adjustSizeToText()
        return subtextLabel