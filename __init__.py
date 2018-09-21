# -*- coding: utf-8 -*-
"""
/***************************************************************************
 dataplot
                                 A QGIS plugin
 PLot data from layer using matplotlib
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2018-09-20
        copyright            : (C) 2018 by DGA Tn
        email                : ben.ensta@gmail.com
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
    """Load dataplot class from file dataplot.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .data_plotter import dataplot
    return dataplot(iface)