# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CsvExtractor
                                 A QGIS plugin
 This plugin extract geometry from polygon type feature
                              -------------------
        begin                : 2017-04-07
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Vladimir Rybalko / 2GIS
        email                : vladimir.rybalko@gmail.com
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
from __future__ import print_function
from __future__ import absolute_import
from builtins import str
from builtins import object
from qgis.PyQt.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from qgis.PyQt.QtWidgets import QAction, QFileDialog
from qgis.PyQt.QtGui import QIcon
# Initialize Qt resources from file resources.py
# from . import resources
from .resources import *  # pylint: disable=W0401,W0614
# Import the code for the dialog
from .csv_extractor_dialog import CsvExtractorDialog
import os.path
from qgis.core import Qgis, QgsGeometry, QgsMessageLog, QgsVectorLayer, QgsWkbTypes
from qgis.gui import QgsMessageBar


class CsvExtractor(object):
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
            'CsvExtractor_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&CSV Extractor')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'CsvExtractor')
        self.toolbar.setObjectName(u'CsvExtractor')

        # Create the dialog (after translation) and keep reference
        self.dlg = CsvExtractorDialog()

        self.dlg.setFixedSize(self.dlg.size())
        self.dlg.lineEdit.clear()
        self.dlg.pushButton.clicked.connect(self.select_output_file)

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
        return QCoreApplication.translate('CsvExtractor', message)

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
            # self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(self.menu, action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = r":/plugins/CsvExtractor/icon.png"
        self.add_action(
            icon_path,
            text=self.tr(u'Save to CSV'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&CSV Extractor'),
                action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar

    def select_output_file(self):
        filename, __ = QFileDialog.getSaveFileName(self.dlg, "Select output file ", "", '*.csv')
        self.dlg.lineEdit.setText(filename)

    def run(self):
        self.dlg.comboBox.clear()
        self.dlg.lineEdit.clear()
        layers = self.iface.mapCanvas().layers()
        layer_list = []
        for layer in layers:
            if layer and isinstance(layer, QgsVectorLayer) and (layer.geometryType() == QgsWkbTypes.PolygonGeometry or layer.geometryType() == QgsWkbTypes.LineGeometry):
                layer_list.append(layer.name())
        self.dlg.comboBox.addItems(layer_list)
        self.dlg.show()
        result = self.dlg.exec_()
        if result:
            filename = self.dlg.lineEdit.text()
            if not filename:
                # fix_print_with_import
                print('file name not exist')
                return

            output_file = open(filename, 'w')

            def writeData(string):
                # text = string.decode('utf8')
                # string = text.encode('cp1251')
                output_file.write(string)
           
            selectedLayerIndex = self.dlg.comboBox.currentIndex()
            selectedLayer = layer_list[selectedLayerIndex]
            layer = None
            for lyr in layers:
                if lyr.name() == selectedLayer:
                    layer = lyr
                    break
            if layer:
                writeData('Полное наименование:;\n')
                writeData('Кадастровый (иной) номер:;\n')
                geometry_type = ''
                # self.iface.messageBar().pushMessage("Info", "geometryType() is: "+QgsWkbTypes.displayString(int(QgsWkbTypes.flatType(layer.wkbType()))), level=Qgis.Info, duration=15)
                if (QgsWkbTypes.flatType(layer.wkbType()) == QgsWkbTypes.Polygon) or (QgsWkbTypes.flatType(layer.wkbType()) == QgsWkbTypes.MultiPolygon):
                    geometry_type = 'POLYGON'
                # if QgsWkbTypes.flatType(layer.wkbType()) == QgsWkbTypes.MultiPolygon:
                    # geometry_type = 'MULTIPOLYGON'
                if QgsWkbTypes.flatType(layer.wkbType()) == QgsWkbTypes.Point:
                    geometry_type = 'POINT'
                # if layer.wkbType() == QgsWkbTypes.LineString:
                if (QgsWkbTypes.flatType(layer.wkbType()) == QgsWkbTypes.LineString) or (QgsWkbTypes.flatType(layer.wkbType()) == QgsWkbTypes.MultiLineString):
                    geometry_type = 'LINESTRING'
                # if QgsWkbTypes.flatType(layer.wkbType()) == QgsWkbTypes.MultiLineString:
                    # geometry_type = 'MULTILINESTRING'
                writeData('Тип геометрии:;{}\n'.format(geometry_type))
                writeData('Часть;Контур;№п/п;X;Y\n')
                
                # iter = None
                if self.dlg.selectCheckBox.isChecked():
                    features = layer.selectedFeatures()
                else:
                    features = layer.getFeatures()
                
                if len(features) == 0 :
                    self.iface.messageBar().pushMessage("Info", "No features to extract", level=Qgis.Info, duration=15)
                    return

                featureCount = 1
                count = 1
                pointCount = 1
                for feature in features:
                    geom = feature.geometry()
                    if QgsWkbTypes.flatType(geom.wkbType()) == QgsWkbTypes.Polygon:
                        featureOut = featureCount
                        for polygon in geom.asPolygon():
                            polygonOut = count
                            for point in polygon:
                                if self.dlg.invetrCheckBox.isChecked():
                                    writeData('{};{};{};{};{}\n'.format(featureOut, polygonOut, pointCount, str(point.y()).replace(".", ","), str(point.x()).replace(".", ",")))
                                else:
                                    writeData('{};{};{};{};{}\n'.format(featureOut, polygonOut, pointCount, str(point.x()).replace(".", ","), str(point.y()).replace(".", ",")))
                                pointCount = pointCount + 1
                            count = count + 1
                        featureCount = featureCount + 1
                    elif QgsWkbTypes.flatType(geom.wkbType()) == QgsWkbTypes.MultiPolygon:
                        for polygons in geom.asMultiPolygon():
                            featureOut = featureCount
                            for polygon in polygons:
                                polygonOut = count
                                for point in polygon:
                                    if self.dlg.invetrCheckBox.isChecked():
                                        writeData('{};{};{};{};{}\n'.format(featureOut, polygonOut, pointCount, str(point.y()).replace(".", ","), str(point.x()).replace(".", ",")))
                                    else:
                                        writeData('{};{};{};{};{}\n'.format(featureOut, polygonOut, pointCount, str(point.x()).replace(".", ","), str(point.y()).replace(".", ",")))
                                    pointCount = pointCount + 1
                                count = count + 1
                            featureCount = featureCount + 1
                    elif QgsWkbTypes.flatType(geom.wkbType()) == QgsWkbTypes.LineString or QgsWkbTypes.flatType(geom.wkbType()) == QgsWkbTypes.MultiLineString:
                        featureOut = featureCount
                        for line in geom.asPolyline():
                            lineOut = count
                            if self.dlg.invetrCheckBox.isChecked():
                                writeData('{};{};{};{};{}\n'.format(featureOut, lineOut, pointCount, str(line.y()).replace(".", ","), str(line.x()).replace(".", ",")))
                            else:
                                writeData('{};{};{};{};{}\n'.format(featureOut, lineOut, pointCount, str(line.x()).replace(".", ","), str(line.y()).replace(".", ",")))
                            pointCount = pointCount + 1
                            count = count + 1
                        featureCount = featureCount + 1
                    # QgsMessageLog.logMessage(str(line.x()), 'CsvExtractor', QgsMessageLog.INFO)
                    # elif geom.wkbType() == QGis.WKBPoint:
            self.iface.messageBar().pushMessage("Info", "The file was exported", level=Qgis.Info, duration=15)
            output_file.close()
