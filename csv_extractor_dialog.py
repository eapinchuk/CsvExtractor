# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CsvExtractorDialog
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

import os

from qgis.PyQt import QtGui, QtWidgets, uic

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'csv_extractor_dialog_base.ui'))


class CsvExtractorDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(CsvExtractorDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
