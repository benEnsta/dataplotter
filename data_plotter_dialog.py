# -*- coding: utf-8 -*-
"""
/***************************************************************************
 dataplotDialog
                                 A QGIS plugin
 PLot data from layer using matplotlib
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2018-09-20
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Benoit Desrochers
        email                : ben.ensta@gmail.com
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

import matplotlib
# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib
import datetime as dt
import numpy as  np

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import QSettings, QFileInfo, QStringListModel
from qgis.core import QgsFeatureRequest

from qgis.PyQt.QtGui import QStandardItemModel
from qgis.PyQt.QtGui import QStandardItem
from qgis.PyQt.QtWidgets import QApplication, QMessageBox
from qgis.PyQt.QtCore import Qt, QVariant, pyqtSlot

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'data_plotter_dialog_base.ui'))


class DataPlotDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(DataPlotDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        plt.ion()
        self.btn_plot.clicked.connect(self.plot)
        # self.btn_plot.clicked.connect(self.plot_dbg)

        self.btn_newFigure.clicked.connect(self.new_figure)
        # self.btn_extract
        self.figures = {}

    @pyqtSlot(str)
    def on_mXFieldComboBox_currentTextChanged(self, s):
        print(s)
        


    def close_evt(self, evt):
        print("close event ", evt)
        print("detail: ", evt.canvas.figure.number)

        items = self.figuresView.findItems("Figure %d" % evt.canvas.figure.number, Qt.MatchContains)
        print("items", items)
        for item in items:
            print("remove ", item.text())
            self.figuresView.removeItemWidget(item)
            self.figuresView.takeItem(self.figuresView.row(item))

    def new_figure(self):
        nrows = self.nrows.value()
        # figureName = self.figuresListe.currentText()
        print(nrows)
        fig, ax = plt.subplots(nrows, 1, sharex=self.sharex.isChecked())
        ax = [ax] if nrows == 1 else ax.tolist()
        print(ax)
        # self.figuresListe.addItem("Figure %d" % fig.number, fig.number)
        fig.canvas.mpl_connect('close_event', self.close_evt)
        # if figureName == "":
        self.figures[fig.number] = {}
        for i in range(len(ax)):
            self.figuresView.addItem("Figure %d.%d" % (fig.number, i))
            idx = max(0, self.figuresView.count()-len(ax))
            self.figuresView.setCurrentRow(idx)

            self.figures[fig.number][i] = ax[i]
            if self.grid.isChecked():
                ax[i].grid()



    def plot_dbg(self):
        figuresStr = self.figuresView.currentItem().text()
        fig, ax = (figuresStr.split(" ")[1]).split(".")
        print(fig, ax)
        ax = self.figures[int(fig)][int(ax)]
        ax.plot(np.arange(1000), np.sin(np.arange(1000)/1000*np.pi))

    def plot(self):

        layer = self.mXFieldComboBox.layer()
        xfieldName = self.mXFieldComboBox.currentField()
        yfieldName = self.mYFieldComboBox.currentField()

        print("Xfield ", xfieldName, "Yfield", yfieldName)

        request = QgsFeatureRequest()

        # More user friendly version
        request.setSubsetOfAttributes([xfieldName, yfieldName],layer.fields())
        # Don't return geometry objects
        request.setFlags(QgsFeatureRequest.NoGeometry)
        print("loading feature")
        if  self.checkBox_selected_feature.isChecked():
            pts = [ [f[xfieldName], f[yfieldName]] for f in layer.getSelectedFeatures(request)]
        else:
            pts = [ [f[xfieldName], f[yfieldName]] for f in layer.getFeatures(request)]
        print("convert to numpy")
        print(pts)
        if isinstance(pts[0][0], QVariant):
            pts = [ [p[0].toDouble(), p[1].toDouble()] for p in pts]
        pts = np.asarray(pts)

        figuresStr = self.figuresView.currentItem()
        if figuresStr is None:
            self.new_figure()
            figuresStr = self.figuresView.currentItem().text()
        else:
            figuresStr = figuresStr.text()
        fig, ax = (figuresStr.split(" ")[1]).split(".")
        print(fig, ax)
        ax = self.figures[int(fig)][int(ax)]
        axfmt = ax.xaxis.get_major_formatter()
        if self.checkbox_utctimestamp.isChecked():
            if not isinstance(axfmt, md.DateFormatter):
                xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
                ax.xaxis.set_major_formatter(xfmt)
                ax.tick_params(axis='x', labelrotation=25)
            t = list(map(dt.datetime.utcfromtimestamp, pts[:,0]))
            ax.plot(t, pts[:,1], label=layer.name() + " " + yfieldName)        
        else:
            if isinstance(axfmt, matplotlib.ticker.ScalarFormatter):
                ax.plot(pts[:,0], pts[:,1], label=layer.name() + " " + yfieldName)
            else:
                QMessageBox.warning(self, "Datetime axis", "invalid plot. You cannot plot a non time serie graph under a time series graph")
        ax.legend()

if __name__ == '__main__':
    import sys

    from qgis.core import *
    import qgis.utils

    # supply path to qgis install location
    QgsApplication.setPrefixPath("/path/to/qgis/installation", True)

    # create a reference to the QgsApplication, setting the
    # second argument to False disables the GUI
    qgs = QgsApplication([], False)

    # load providers
    qgs.initQgis()

    vlayer = QgsVectorLayer(sys.argv[1], "layer_name_you_like", "ogr")
    QgsProject.instance().addMapLayer(vlayer)
    # app = QApplication(sys.argv)
    dlg = DataPlotDialog(qgis.utils.iface)
    dlg.show()
    dlg.exec_()

    qgs.exitQgis()
