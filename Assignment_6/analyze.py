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


class CustomNormalVectorNode(CtrlNode):
    nodeName = "CustomNormalVector"

    uiTemplate = []  # required; even empty; endless recursion otherwise o.O

    def __init__(self, node_name):
        terminals = {
            'x_axis_in': dict(io='in'),
            'z_axis_in': dict(io='in'),
            'x_rotation_out': dict(io='out'),
            'z_rotation_out': dict(io='out')
        }

        CtrlNode.__init__(self, node_name, terminals=terminals)

    def process(self, **kwds):

        out = [kwds['x_axis_in'] - 512, kwds['z_axis_in'] - 512]

        return {
            'x_rotation_out': np.array([0, out[0]]),
            'z_rotation_out': np.array([0, out[1]])
        }


fclib.registerNodeType(CustomNormalVectorNode, [('NVN',)])


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
    :param wm_address: the mac address to the wiimote
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

    pw_x_node = setup_node(fc, 'PlotWidget', 300, 0, pwx)
    pw_y_node = setup_node(fc, 'PlotWidget', 300, 150, pwy)
    pw_z_node = setup_node(fc, 'PlotWidget', 300, -150, pwz)

    return pw_x_node, pw_y_node, pw_z_node


def main():
    """
    application entry point
    :return: void
    """

    input_from_cmd()

    app = QtGui.QApplication([])

    win, cw, lt, fc = setup_displaying_of_plots()

    pw_x_node, pw_y_node, pw_z_node = get_plot_widget_nodes(fc, lt)

    wiimote_node_ = setup_node(fc, 'Wiimote', 0, 0)
    wiimote_node_.text.setText(sys.argv[1])

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

    # optional node implementation; also see CustomNormalVectorNode class
    nv_pw = pg.PlotWidget()

    # nv_pw.setXRange(-2, 2)

    lt.addWidget(nv_pw, 3, 1)
    nv_pw.setXRange(-1, 1)
    nv_pw.setYRange(-1, 1)
    nv_pc = fc.createNode('PlotCurve', pos=(-100, 150))
    nv_pw_node = fc.createNode('PlotWidget', pos=(-100, 300))

    nv_pw_node.setPlot(nv_pw)

    nvn = fc.createNode('CustomNormalVector', 'CustomNormalVectorNode',
                        pos=(-100, 450))

    fc.connectTerminals(wiimote_node_['accelX'], nvn['x_axis_in'])
    fc.connectTerminals(wiimote_node_['accelZ'], nvn['z_axis_in'])
    fc.connectTerminals(nvn['x_rotation_out'], nv_pc['x'])
    fc.connectTerminals(nvn['z_rotation_out'], nv_pc['y'])
    fc.connectTerminals(nv_pc['plot'], nv_pw_node['In'])

    # end of optional node implementation

    win.show()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


if __name__ == '__main__':
    main()
