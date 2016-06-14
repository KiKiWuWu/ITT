#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

from pyqtgraph.flowchart import Flowchart, Node
from pyqtgraph.flowchart.library.common import CtrlNode
import pyqtgraph.flowchart.library as fclib
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import sys
import wiimote
import wiimote_node

WM_ADDRESS = "18:2A:7B:F3:F8:F5"  # default address


def input_from_cmd():
    """
    checks if cmd args are exactly 2 in number

    :return: void
    """

    if len(sys.argv) != 2:
        raise Exception("Insufficient number of CMD Args! Mac Address Required")


def add_plot_widget_to_layout(layout, offset, columns):
    """
    adds a new PlotWidget to the given layout and returns the PlotWidget

    :param layout: the layout to receive the PlotWidget
    :param offset: the row offset
    :param columns: the amount of columns the widget spans
    :return: the newly constructed and added PlotWidget
    """
    pw = pg.PlotWidget()
    layout.addWidget(pw, offset, columns)
    pw.setYRange(0, 1024)

    return pw


def setup_node(fc, node_name, x, y, pw=None):
    """
    create a new node in a given flowchart based on a given name and coords

    :param fc: the flowchart to receive the node
    :param node_name: the name of the target node to construct
    :param x: the x-position in the flowchart
    :param y: the y-position in the flowchart
    :param pw: a PlotWidget, if a PlotWidget-Node is to be constructed
    :return: the newly constructed node
    """
    node = fc.createNode(node_name, pos=(x, y))

    if pw and node_name == 'PlotWidget':
        node.setPlot(pw)

    return node


def setup_displaying_of_plots():
    """
    setup of all PyQt and PyQtGraph related objects for further use

    :return: newly constructed window object, central_widget object,
             layout object and flowchart object
    """
    win = QtGui.QMainWindow()
    win.setWindowTitle("Analyze")

    central_widget = QtGui.QWidget()

    win.setCentralWidget(central_widget)

    layout = QtGui.QGridLayout()
    central_widget.setLayout(layout)

    fc = Flowchart(terminals={})

    layout.addWidget(fc.widget(), 0, 0, 2, 1)

    return win, central_widget, layout, fc


def get_plot_widget_nodes(fc, layout):
    """
    creates and returns the node needed for plotting accompanied by their
    respective PlotWidgets in order to draw visualization data

    :param fc: the flowchart receiving the nodes
    :param layout: the layout receiving the PlotWidget objects
    :return: the 3 PlotWidgets-Nodes responsible for plotting the accelerometer
             data and the PlotWidget for the NormalVectorNode(WIP)
    """
    pwx = add_plot_widget_to_layout(layout, 0, 1)
    pwy = add_plot_widget_to_layout(layout, 1, 1)
    pwz = add_plot_widget_to_layout(layout, 2, 1)
    pww = add_plot_widget_to_layout(layout, 3, 1)

    pw_x_node = setup_node(fc, 'PlotWidget', 300, 0, pwx)
    pw_y_node = setup_node(fc, 'PlotWidget', 300, 150, pwy)
    pw_z_node = setup_node(fc, 'PlotWidget', 300, -150, pwz)
    pw_w_node = setup_node(fc, 'PlotWidget', 0, -300, pww)

    return pw_x_node, pw_y_node, pw_z_node, pw_w_node


def main():
    """
    application entry point
    :return: void
    """

    input_from_cmd()

    app = QtGui.QApplication([])

    win, cw, lt, fc = setup_displaying_of_plots()

    pw_x_node, pw_y_node, pw_z_node, pw_w_node = get_plot_widget_nodes(fc, lt)

    wiimote_node_ = setup_node(fc, 'Wiimote', 0, 0)

    buffer_node_x = setup_node(fc, 'Buffer', 150, 0)
    buffer_node_y = setup_node(fc, 'Buffer', 150, 150)
    buffer_node_z = setup_node(fc, 'Buffer', 150, -150)

    filter_node_mean = setup_node(fc, 'MeanFilter', 0, -300)
    filter_node_median = setup_node(fc, 'MedianFilter', 300, -300)
    filter_node_gaussian = setup_node(fc, 'GaussianFilter', 150, -300)

    fc.connectTerminals(wiimote_node_['accelX'], buffer_node_x['dataIn'])
    fc.connectTerminals(wiimote_node_['accelY'], buffer_node_y['dataIn'])
    fc.connectTerminals(wiimote_node_['accelZ'], buffer_node_z['dataIn'])
    fc.connectTerminals(buffer_node_x['dataOut'], filter_node_mean['In'])
    fc.connectTerminals(buffer_node_y['dataOut'], filter_node_gaussian['In'])
    fc.connectTerminals(buffer_node_z['dataOut'], filter_node_median['In'])
    fc.connectTerminals(filter_node_mean['Out'], pw_x_node['In'])
    fc.connectTerminals(filter_node_gaussian['Out'], pw_y_node['In'])
    fc.connectTerminals(filter_node_median['Out'], pw_z_node['In'])

    win.show()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


if __name__ == '__main__':
    main()
