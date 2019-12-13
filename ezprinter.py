# -*- coding: utf-8 -*-
"""
/***************************************************************************
 EZPrinter
                                 A QGIS plugin
 Print your maps easily.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-11-28
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Kanahiro Iguchi
        email                : kanahiro.iguchi@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt, QSize, QRectF, QSizeF
from qgis.PyQt.QtGui import QIcon, QImage, QPainter, QCursor, QGuiApplication
from qgis.PyQt.QtWidgets import QAction
from qgis.core import *
# Initialize Qt resources from file resources.py
from .resources import *

# Import the code for the DockWidget
from .ezprinter_dockwidget import EZPrinterDockWidget
import os.path

from .clickTool import ClickTool
from .constants import Constants as CONSTANTS
from .printWindow import PrintWindow


class EZPrinter:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'EZPrinter_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&EZPrinter')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'EZPrinter')
        self.toolbar.setObjectName(u'EZPrinter')

        #print "** INITIALIZING EZPrinter"

        self.pluginIsActive = False
        self.dockwidget = None


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('EZPrinter', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/ezprinter/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'EZPrinter'),
            callback=self.run,
            parent=self.iface.mainWindow())

    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING EZPrinter"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD EZPrinter"

        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&EZPrinter'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    #--------------------------------------------------------------------------

    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True

            #print "** STARTING EZPrinter"

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = EZPrinterDockWidget()

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.TopDockWidgetArea, self.dockwidget)
            self.dockwidget.show()

        self.initCustomGUIs()

    def initPapersCombobox(self):
        combobox = self.dockwidget.papersComboBox
        papers = CONSTANTS.PAPERS
        for paper in papers:
            combobox.addItem(paper +  ":" + str(papers[paper]), papers[paper])
            #default
            if paper == "A4":
                combobox.setCurrentIndex(combobox.count() - 1)

    def initScalesCombobox(self):
        combobox = self.dockwidget.scalesComboBox
        combobox.setEditable(True)
        scales = CONSTANTS.DEFAULT_SCALES
        for scale in scales:
            combobox.addItem(str(scale), scale)
            #default
            if scale == 2500:
                combobox.setCurrentIndex(combobox.count() - 1)


    def initClicktool(self):
        if not isinstance(self.iface.mapCanvas().mapTool(), ClickTool):
            return
        paperSize = self.dockwidget.papersComboBox.currentData()
        printScale = self.dockwidget.scalesComboBox.currentData()
        horizontal = self.dockwidget.horizontalCheckBox.isChecked()
        #wideMode = self.dockwidget.wideModeCheckBox.isChecked()
        ct = ClickTool(self.iface,  self.mapCanvasClicked, paperSize, printScale, horizontal)
        self.iface.mapCanvas().setMapTool(ct)

    def selectButtonPushed(self):
        if not isinstance(self.iface.mapCanvas().mapTool(), ClickTool):
            self.previous_map_tool = self.iface.mapCanvas().mapTool()
        paperSize = self.dockwidget.papersComboBox.currentData()
        printScale = self.dockwidget.scalesComboBox.currentData()
        horizontal = self.dockwidget.horizontalCheckBox.isChecked()
        ct = ClickTool(self.iface,  self.mapCanvasClicked, paperSize, printScale, horizontal)
        self.iface.mapCanvas().setMapTool(ct)

    def toggleGuiChangeEvent(self):
        self.dockwidget.papersComboBox.currentIndexChanged.connect(self.initClicktool)
        self.dockwidget.scalesComboBox.currentTextChanged.connect(self.initClicktool)
        self.dockwidget.horizontalCheckBox.stateChanged.connect(self.initClicktool)
        #self.dockwidget.wideModeCheckBox.stateChanged.connect(self.initClicktool)

    def initCustomGUIs(self):
        self.initPapersCombobox()
        self.initScalesCombobox()
        self.toggleGuiChangeEvent()
        self.dockwidget.selectButton.clicked.connect(self.selectButtonPushed)
        self.iface.mapCanvas().scaleChanged.connect(self.initClicktool)

    #make and return QImage from MapCanvas, clipped by selected Print Area
    def makeImage(self, mapSettings):
        image = QImage(mapSettings.outputSize(), QImage.Format_RGB32)
        p = QPainter()
        p.begin(image)
        mapRenderer = QgsMapRendererCustomPainterJob(mapSettings, p)
        mapRenderer.start()
        mapRenderer.waitForFinished()
        p.end()
        return image

    def mapCanvasClicked(self, coordinates):
        #set cursor as waiting mode
        self.iface.mapCanvas().mapTool().setCursor(Qt.WaitCursor)

        #init vars
        paperSize = self.dockwidget.papersComboBox.currentData()
        printScale = self.dockwidget.scalesComboBox.currentData()
        horizontal = self.dockwidget.horizontalCheckBox.isChecked()
        #widemode = self.dockwidget.wideModeCheckBox.isChecked()
        rotation = self.iface.mapCanvas().rotation()

        #init PrintLayout
        project = QgsProject.instance()
        printLayout = QgsPrintLayout(project)
        printLayout.initializeDefaults()
        printLayout.setUnits(QgsUnitTypes.LayoutMillimeters)

        #paper setting
        paperWidth = paperSize[0]
        paperHeight = paperSize[1]
        if horizontal:
            paperWidth = paperSize[1]
            paperHeight = paperSize[0]

        page = printLayout.pageCollection().pages()[0]
        page.setPageSize(QgsLayoutSize(paperWidth, paperHeight))

        #map area
        ##papersize Setting
        mapWidth = paperWidth - CONSTANTS.PAPER_MARGINS['left'] - CONSTANTS.PAPER_MARGINS['right']
        mapHeight = paperHeight - CONSTANTS.PAPER_MARGINS['top'] - CONSTANTS.PAPER_MARGINS['bottom']
        
        ##mapsetting on paper
        projectMap = QgsLayoutItemMap(printLayout)
        projectMap.updateBoundingRect()
        projectMap.setRect(QRectF(CONSTANTS.PAPER_MARGINS['left'], CONSTANTS.PAPER_MARGINS['top'], mapWidth, mapHeight)) 
        projectMap.setPos(CONSTANTS.PAPER_MARGINS['left'], CONSTANTS.PAPER_MARGINS['top'])
        projectMap.setFrameEnabled(True)
        ##map geometry setting
        projectMap.setLayers(project.mapThemeCollection().masterVisibleLayers())
        ###when map is rotated, extent setting will not work correctly.
        ###So, by run setExtent() firstly in order to define CENTER of map and then,
        ###define rotation and scale of the map.
        projectMap.setExtent(QgsRectangle(coordinates["topLeft"], coordinates["bottomRight"]))
        projectMap.setMapRotation(rotation)
        projectMap.setScale(printScale)
        projectMap.attemptSetSceneRect(QRectF(CONSTANTS.PAPER_MARGINS['left'], CONSTANTS.PAPER_MARGINS['top'], mapWidth, mapHeight))
        
        printLayout.addItem(projectMap)

        '''
        #output PDF
        exporter =  QgsLayoutExporter(printLayout)
        pdf_settings = exporter.PdfExportSettings()
        exporter.exportToPdf("/Users/kanahiroiguchi/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/ezprinter/test.pdf", pdf_settings)
        
        #render image on memory
        img_settings = exporter.ImageExportSettings()
        printLayoutImage = exporter.renderPageToImage(0)
        '''

        #preview
        pw = PrintWindow(self.iface, printLayout, projectMap)
        self.iface.mapCanvas().setMapTool(self.previous_map_tool)
