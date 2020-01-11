import os

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from qgis.core import *
from qgis.PyQt import QtGui, QtWidgets, uic

from .constants import Constants as CONSTANTS

class PrintWindow():
    def __init__(self, iface, printLayout, projectMap, widemode):
        self.ui = uic.loadUi(os.path.join(os.path.dirname(__file__), 'printWindow.ui'))
        self.iface = iface
        self.printLayout = printLayout
        self.projectMap = projectMap
        self.widemode = widemode

        self.margins = CONSTANTS.PAPER_MARGINS
        if self.widemode:
            self.margins = CONSTANTS.WIDEMODE_MARGINS

        self.setPdfImageOf(self.printLayout)
        self.initCustomGui()

        self.ui.exec_()

    def makeImageBy(self, printLayout):
        exporter =  QgsLayoutExporter(printLayout)
        img_settings = exporter.ImageExportSettings()
        printLayoutImage = exporter.renderPageToImage(0)
        return printLayoutImage

    def setPdfImageOf(self, printLayout):
        printLayoutImage = self.makeImageBy(printLayout)
        scaledImage = printLayoutImage.scaled(400, 400, Qt.KeepAspectRatio)
        self.ui.imageLabel.setPixmap(QtGui.QPixmap.fromImage(scaledImage))

    def initCustomGui(self):
        self.ui.titleLineEdit.editingFinished.connect(self.applyGuiChangeToPrintLayout)
        self.ui.scaleBarCheck.stateChanged.connect(self.applyGuiChangeToPrintLayout)
        self.ui.subtextLineEdit.editingFinished.connect(self.applyGuiChangeToPrintLayout)
        self.ui.exportButton.clicked.connect(self.exportButtonPushed)

    #show temp printLayout to QLabel
    def applyGuiChangeToPrintLayout(self):
        appliedPrintLayout = self.setGuiValueTo(self.printLayout)
        self.setPdfImageOf(appliedPrintLayout)

    #this method won't mutate printLayout of argument
    #make clone and return mutated clone
    def setGuiValueTo(self, printLayout):
        clonePrintLayout = printLayout.clone()
        titleLabel = self.makeTitleLabel()
        clonePrintLayout.addItem(titleLabel)

        if self.ui.scaleBarCheck.isChecked():
            scaleBar = self.makeScaleBar()
            clonePrintLayout.addItem(scaleBar)

        subtextLabel = self.makeSubtextLabel()
        clonePrintLayout.addItem(subtextLabel)

        return clonePrintLayout

    def makeTitleLabel(self):
        titleFont = QFont()
        titleFont.setPointSize(CONSTANTS.TITLE_FONTSIZE)
        titleFont.setBold(True)

        titleLabel = QgsLayoutItemLabel(self.printLayout)
        titleLabel.setText(self.ui.titleLineEdit.text())
        titleLabel.setPos(self.margins["left"], self.margins["top"] - CONSTANTS.TITLE_FONTSIZE / 2)
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
        scaleBar.setPos(self.margins['left'], paperSize.height() - self.margins['bottom'] - 15)

        return scaleBar

    def makeSubtextLabel(self):
        page = self.printLayout.pageCollection().pages()[0]
        paperSize = page.pageSize()

        subtextFont = QFont()
        subtextFont.setPointSize(CONSTANTS.SUBTEXT_FONTSIZE)
        subtextFont.setBold(True)

        subtextLabel = QgsLayoutItemLabel(self.printLayout)
        subtextLabel.setText(self.ui.subtextLineEdit.text())
        subtextLabel.setPos(self.margins["left"], paperSize.height() - self.margins['bottom'])
        subtextLabel.setFont(subtextFont)
        subtextLabel.adjustSizeToText()
        return subtextLabel

    def exportButtonPushed(self):
        outputPrintLayout = self.setGuiValueTo(self.printLayout)

        filepath, mimetype = QFileDialog.getSaveFileName(caption = "save pdf", directory = '', filter = '*.pdf')
        ##if canceled
        if not filepath:
            return
        exporter =  QgsLayoutExporter(outputPrintLayout)
        pdf_settings = exporter.PdfExportSettings()
        exporter.exportToPdf(filepath, pdf_settings)

        self.iface.messageBar().pushMessage("Info", "PDF correctly saved:" + filepath, Qgis.Info)
        self.ui.reject()