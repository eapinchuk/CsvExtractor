# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CsvExtractor
                                 A QGIS plugin
 This plugin extract geometry from polygon type feature
                             -------------------
        begin                : 2017-04-07
        copyright            : (C) 2017 by Vladimir Rybalko / 2GIS
        email                : vladimir.rybalko@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load CsvExtractor class from file CsvExtractor.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .csv_extractor import CsvExtractor
    return CsvExtractor(iface)
